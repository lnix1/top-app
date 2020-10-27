from flask import Blueprint, render_template, request, flash, g, redirect, session, url_for
from ip2geotools.databases.noncommercial import DbIpCity
from OSMPythonTools.overpass import Overpass, overpassQueryBuilder
import requests
from xml.etree import ElementTree
from itertools import chain
from werkzeug.security import check_password_hash, generate_password_hash
import functools
from top_app import db, User

bp = Blueprint('home', __name__, url_prefix='/')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = db.session.query(User).filter(User.id == user_id).one()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('home.login'))

        return view(**kwargs)

    return wrapped_view

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.session.query(User).filter(User.username == username).count() != 0:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            u = User(username = username, password = generate_password_hash(password))
            db.session.add(u)
            db.session.commit()
            return redirect(url_for('home.login'))

        flash(error)

    return render_template('register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        try:
            user = db.session.query(User).filter(User.username == username).one()
        except:
            user = None

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('home.index'))

        flash(error)

    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home.index'))

@bp.route('/resource_view', methods=('GET', 'POST'))
def resource_view():
    # comment out to hardcode ip address
    if request.method == 'POST':
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            addr = request.environ['REMOTE_ADDR']
        else:
            addr = request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy
    #addr ="76.176.72.174"

    #addr = "98.163.214.113"       
    geocode = DbIpCity.get(addr, api_key='free')
    serv_type = request.form['service_type']
    overpass = Overpass()

    if (serv_type in ['childcare']):
        query1 = overpassQueryBuilder(bbox=[geocode.latitude-1, geocode.longitude-1, 
                                        geocode.latitude+1, geocode.longitude+1],
                                    elementType=['node','way'],
                                    selector=['"amenity"="'+str(serv_type)+'"','name'],
                                    includeGeometry=False)
        
        result1 = overpass.query(query1).toJSON()
        result1 = result1['elements']
        query2 = overpassQueryBuilder(bbox=[geocode.latitude-1, geocode.longitude-1, 
                                        geocode.latitude+1, geocode.longitude+1],
                                    elementType=['node'],
                                    selector=['"amenity"="kindergarten"','name'],
                                    includeGeometry=False)
        result2 = overpass.query(query2).toJSON()
        result2 = result2['elements']
        result0 = [result1,result2]
        result = list(chain.from_iterable(result0))
    elif (serv_type in ['place_of_worship','hospital','bank']):
        query = overpassQueryBuilder(bbox=[geocode.latitude-1, geocode.longitude-1, 
                                        geocode.latitude+1, geocode.longitude+1],
                                    elementType='node',
                                    selector=['"amenity"="'+str(serv_type)+'"','name'],
                                    includeGeometry=False)
        result = overpass.query(query).toJSON()
        result = result['elements']
    elif (serv_type in ['mental_health']):
        query = overpassQueryBuilder(bbox=[geocode.latitude-10, geocode.longitude-10, 
                                        geocode.latitude+10, geocode.longitude+10],
                                    elementType=['node','way'],
                                    selector=['"social_facility:for"="'+str(serv_type)+'"','name'],
                                    includeGeometry=False)
        result = overpass.query(query).toJSON()
        result = result['elements']
    else:
        query = overpassQueryBuilder(bbox=[geocode.latitude-1, geocode.longitude-1, 
                                        geocode.latitude+1, geocode.longitude+1],
                                    elementType=['node','way'],
                                    selector=['"office"="'+str(serv_type)+'"','name'],
                                    includeGeometry=False)
        result = overpass.query(query).toJSON()
        result = result['elements']
    
    for element in result:
        if element['type']=='way':
            apiquery = requests.get("https://api.openstreetmap.org/api/0.6/node/"+str(element['id']))
            if apiquery.content != b'':
                apitree = ElementTree.fromstring(apiquery.content)
                for child in apitree.iter('node'):
                    element['cord'] = [float(child.attrib['lon']),float(child.attrib['lat'])]
                element['type'] ='Point'
            else:
                length = len(element['nodes'])
                element['cord']=list(range(0,length))
                for idnum in range(0,length):
                    apiquery2 = requests.get("https://api.openstreetmap.org/api/0.6/node/"+str(element['nodes'][idnum]))
                    apitree2 = ElementTree.fromstring(apiquery2.content)
                    for child in apitree2.iter('node'):
                        element['cord'][idnum] = [float(child.attrib['lon']),float(child.attrib['lat'])]   
                element['type'] ='LineString'
        else:
            element['type'] ='Point'
            element['cord'] = [element['lon'],element['lat']]

    
    context = {
        "type": "FeatureCollection",
        "features": [
        {
            "type": "Feature",
            "properties" : d['tags'],
            "geometry" : {
                "type": d['type'],
                "coordinates": d['cord'],
                },
        } for d in result]
    }

    if serv_type in 'hospital':
        serv_name = 'Medical Services'
    elif serv_type in 'lawyer':
        serv_name = 'Legal Services'
    elif serv_type in 'place_of_worship':
        serv_name = 'Religous Communities'
    elif serv_type in 'mental_health':
        serv_name = 'Metal Health Services'
    else:
        serv_name = 'Child Care Services'
    
    return render_template('resource_view.html', context = context, coords = [geocode.latitude, geocode.longitude], page_name = serv_name)

@bp.route('/lookup', methods=('GET', 'POST'))
@login_required
def lookup():
    return render_template('lookup.html')

@bp.route('/tagging', methods=('GET', 'POST'))
@login_required
def tagging():
    tag_address = request.form['yes_no']
    return render_template('tagging.html', context = tag_address)

@bp.route('write_osm', methods=('GET', 'POST'))
@login_required
def write_osm():
    context = {
        'org-name' : request.form['org-name'],
        'services' : request.form['services'],
        'r-services' : request.form['r-services'],
        'website' : request.form['website'],
        'p-number' : request.form['pnumber']
    }

    # utilizing the 'osmapi' package to write to OSM servers. Package info here: https://pypi.org/project/osmapi/
    #import osmapi
    #api = osmapi.OsmApi(api="https://api06.dev.openstreetmap.org", username = u"metaodi", password = u"*******")
    #api.ChangesetCreate({u"comment": u"My first test"})
    #print(api.NodeCreate({u"lon":1, u"lat":1, u"tag": {}}))
    #api.ChangesetClose()

    return render_template('/lookup.html')
