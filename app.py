from flask import Flask
from flask import request
from flask_cors import CORS
import json
from src.ee_utils import *
from flask import render_template
import ee
from src.model import preprocessing, display_map, burnSeverity

app = Flask(__name__)

# CORS(app, support_credentials=True)

@app.before_request
def before():
    ee.Initialize()
    CORS(app)
    

app = Flask(__name__)

@app.get('/')
def map():
    return render_template("map.html")

@app.route('/visualize', methods=['POST'])
def visualize(): 
    request_parameters = request.get_json(force=True)
    
    # get the parameters set by the user

    x_min, y_min, x_max, y_max = [float(coords) for coords in request_parameters["bbox"].split(",")]
    pre_start = request_parameters["pre_start"]
    pre_last = request_parameters["pre_last"]
    fire_start= request_parameters["fire_start"]
    fire_last = request_parameters["fire_last"]
    satellite = request_parameters["satellite"]

    # create Google Earth Engine Geometry from the bounding bax parameters
    ee_geom = ee.Geometry.Rectangle([x_min, y_min, x_max, y_max])

    # create the range dates from the date parameters selected by the user
    preFire_period = (pre_start, pre_last)
    postFire_period = (fire_start, fire_last)

    # run the burn severity model 
    pre_processing_params = preprocessing(ee_geom, satellite, preFire_period, postFire_period)
    tile_id = display_map(pre_processing_params)
    return tile_id


@app.route('/statistics', methods=['POST'])
def show_stats(): 
    request_parameters = request.get_json(force=True)
    
    # get the parameters set by the user

    x_min, y_min, x_max, y_max = [float(coords) for coords in request_parameters["bbox"].split(",")]
    pre_start = request_parameters["pre_start"]
    pre_last = request_parameters["pre_last"]
    fire_start= request_parameters["fire_start"]
    fire_last = request_parameters["fire_last"]
    satellite = request_parameters["satellite"]

    # create Google Earth Engine Geometry from the bounding bax parameters
    ee_geom = ee.Geometry.Rectangle([x_min, y_min, x_max, y_max])

    # create the range dates from the date parameters selected by the user
    preFire_period = (pre_start, pre_last)
    postFire_period = (fire_start, fire_last)
    # run the burn severity model 
    pre_processing_params = preprocessing(ee_geom, satellite, preFire_period, postFire_period)
    stats = burnSeverity(pre_processing_params)

    return stats


@app.route('/download', methods=['POST'])
def download(): 
    request_parameters = request.get_json(force=True)
    
    # get the parameters set by the user

    x_min, y_min, x_max, y_max = [float(coords) for coords in request_parameters["bbox"].split(",")]
    pre_start = request_parameters["pre_start"]
    pre_last = request_parameters["pre_last"]
    fire_start= request_parameters["fire_start"]
    fire_last = request_parameters["fire_last"]
    satellite = request_parameters["satellite"]

    # create Google Earth Engine Geometry from the bounding bax parameters
    ee_geom = ee.Geometry.Rectangle([x_min, y_min, x_max, y_max])

    # create the range dates from the date parameters selected by the user
    preFire_period = (pre_start, pre_last)
    postFire_period = (fire_start, fire_last)

    # run the burn severity model 
    pre_processing_params = preprocessing(ee_geom, satellite, preFire_period, postFire_period)


if __name__ == '__main__':
    app.run(debug=True)