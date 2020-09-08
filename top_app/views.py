from flask import Blueprint, render_template, request, flash
from ip2geotools.databases.noncommercial import DbIpCity
from OSMPythonTools.overpass import Overpass, overpassQueryBuilder

bp = Blueprint('home', __name__, url_prefix='/')

@bp.route('')
def index():
    return render_template('index.html')

@bp.route('/resource_view', methods=('GET', 'POST'))
def resource_view():

    #if request.method == 'POST':
    #    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
    #        addr = request.environ['REMOTE_ADDR']
    #    else:
    #        addr = request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy
    addr = '98.163.214.113'
    geocode = DbIpCity.get(addr, api_key='free')
    serv_type = request.form['service_type']

    if (serv_type in ['hospital', 'place_of_worship']):
        query = overpassQueryBuilder(bbox=[geocode.latitude-1, geocode.longitude-1, 
                                        geocode.latitude+1, geocode.longitude+1],
                                    elementType='node',
                                    selector=['"amenity"="'+str(serv_type)+'"'],
                                    includeGeometry=False)
    elif (serv_type in ['mental_health']):
        query = overpassQueryBuilder(bbox=[geocode.latitude-10, geocode.longitude-10, 
                                        geocode.latitude+10, geocode.longitude+10],
                                    elementType='node',
                                    selector=['"social_facility:for"="'+str(serv_type)+'"'],
                                    includeGeometry=False)
    else:
        query = overpassQueryBuilder(bbox=[geocode.latitude-1, geocode.longitude-1, 
                                        geocode.latitude+1, geocode.longitude+1],
                                    elementType='node',
                                    selector=['"office"="'+str(serv_type)+'"'],
                                    includeGeometry=False)

    overpass = Overpass()
    result = overpass.query(query).toJSON()
    
    context = {
        "type": "FeatureCollection",
        "features": [
        {
            "type": "Feature",
            "properties" : d['type'],
            "geometry" : {
                "type": "Point",
                "coordinates": [d["lon"], d["lat"]],
                },
        } for d in result['elements']]
    }
    
    return render_template('resource_view.html', context = context, coords = [geocode.latitude, geocode.longitude])