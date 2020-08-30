from flask import Blueprint, render_template, request, flash
from ip2geotools.databases.noncommercial import DbIpCity
from OSMPythonTools.overpass import Overpass, overpassQueryBuilder


bp = Blueprint('home', __name__, url_prefix='/')

@bp.route('')
def index():
    return render_template('index.html')

@bp.route('/resource_view', methods=('GET', 'POST'))
def resource_view():

    if request.method == 'POST':
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            addr = request.environ['REMOTE_ADDR']
        else:
            addr = request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy
    
    geocode = DbIpCity.get(addr, api_key='free')
    serv_type = request.form['service_type']

    query = overpassQueryBuilder(bbox=[geocode.latitude-10, geocode.longitude-10, 
                                       geocode.latitude+10, geocode.longitude+10],
                             elementType='node',
                             selector='"building"='+str(serv_type)+'"',
                             includeGeometry=False)

    overpass = Overpass()
    result = overpass.query(query)
    flash(result.elements()[0].tags('name'))
    flash(result.elements()[0].tags('addr:city'))

    #context = {}
    #context['latitude'] = geocode.latitude
    #context['longitude'] = geocode.longitude
    #context['service_type'] = request.form['service_type']
    #flash(context)
    
    return render_template('resource_view.html')#, **context)