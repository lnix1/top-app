from flask import Blueprint, render_template, request, flash
from ip2geotools.databases.noncommercial import DbIpCity
from OSMPythonTools.overpass import Overpass, overpassQueryBuilder
import requests
from xml.etree import ElementTree
from itertools import chain

bp = Blueprint('home', __name__, url_prefix='/')

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/resource_view', methods=('GET', 'POST'))
def resource_view():
    # comment out to hardcode ip address
    #if request.method == 'POST':
    #    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
    #        addr = request.environ['REMOTE_ADDR']
    #    else:
    #        addr = request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy
    addr ="76.176.72.174"

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
            element['type'] ='LineString' 
            length = len(element['nodes'])
            element['cord']=list(range(0,length))
            for idnum in range(0,length):
                apiquery2 = requests.get("https://api.openstreetmap.org/api/0.6/node/"+str(element['nodes'][idnum]))
                apitree2 = ElementTree.fromstring(apiquery2.content)
                for child in apitree2.iter('node'):
                    element['cord'][idnum] = [float(child.attrib['lon']),float(child.attrib['lat'])]     
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
    
    
    
    return render_template('resource_view.html', context = context, coords = [geocode.latitude, geocode.longitude])

@bp.route('/lookup', methods=('GET', 'POST'))
def lookup():
    return render_template('lookup.html')

@bp.route('/tagging', methods=('GET', 'POST'))
def tagging():
    tag_address = request.form['yes_no']
    return render_template('tagging.html', context = tag_address)

@bp.route('write_osm', methods=('GET', 'POST'))
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
