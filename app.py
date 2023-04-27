from flask import Flask, request, render_template
from flask_cors import CORS
from flask_restful import Api, Resource
from src.model import preprocessing, display_map, burnSeverity
import ee

app = Flask(__name__)
api = Api(app)
CORS(app)

@app.before_request
def before():
    ee.Initialize()

class Visualize(Resource):
    def post(self):
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

class Statistics(Resource):
    def post(self):
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

api.add_resource(Visualize, '/visualize')
api.add_resource(Statistics, '/statistics')

@app.route('/')
def map():
    return render_template("map.html")

if __name__ == '__main__':
    app.run(debug=True)
