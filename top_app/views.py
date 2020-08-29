from flask import Blueprint, render_template, request
from ip2geotools.databases.noncommercial import DbIpCity


bp = Blueprint('home', __name__, url_prefix='/')

@bp.route('')
def index():

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
    	addr = request.environ['REMOTE_ADDR']
    else:
    	addr = request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy
 
    geocode = DbIpCity.get(addr, api_key='free')
    
    return render_template('index.html'), str(geocode.latitude)


