from flask import Flask
from flask import redirect, url_for
from flask import request, jsonify
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

# @app.route('/visualize', method='POST')



if __name__ == '__main__':
    app.run(debug=True)