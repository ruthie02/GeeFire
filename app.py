from flask import Flask
from flask import request
from flask_cors import CORS
from src.ee_utils import *
from flask import render_template
import ee
import os

app = Flask(__name__)

CORS(app, support_credentials=True)

# @app.before_request
# def before():
#     ee.Initialize()

app = Flask(__name__)


@app.route('/')
def map():
    return render_template("map.html")

@app.route('/visualize', methods=["ROUTE"])
def display(request):
    request_parameters = request.get_json()

    # get the parameters set by the user

    x_min, y_min, x_max, y_max = [float(coords) for coords in request_parameters["bbox"].split(",")]
    pre_start = request_parameters["pre_start"]
    pre_last = request_parameters["pre_last"]
    fire_start= request_parameters["fire_start"]
    fire_last = request_parameters["fire_last"]
    satellite = request_parameters["satellite"]

    # create Google Earth Engine Geometry from the bounding bax parameters
    ee_geom = ee.Geometry.Rectange([x_min, y_min, x_max, y_max])

    # create the range dates from the date parameters selected by the user
    preFire_period = (pre_start, pre_last)
    postFire_period = (fire_start, fire_last)

    # run the burn severity model 

    return pre_start





if __name__ == '__main__':
    app.run(debug=True)