# imports
import os
from flask_cors import CORS
from pycode.statistics.statistics import *
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, abort, send_from_directory, send_file
from werkzeug.utils import secure_filename
from flask import jsonify

# config
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.csv','.xes']
app.config['UPLOAD_PATH'] = 'Uploads'
CORS(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            print('400')
            return 400
        
    uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
   
    log = createLog(app.config['UPLOAD_PATH'],filename)
    
    df = createDataFrame(log)

    activitiesCount = getActivitesCount(df).to_dict()
    activitiesCount = dictToArray(activitiesCount)
    eventCount = getEventCount(df)
    meanDurchlaufzeit = getMeanDurchlaufzeit(log)
    resourceCount = getResourceCount(df).to_dict()
    resourceCount = dictToArray(resourceCount)
    durchlaufzeit = getDurchlaufzeit(log)
    print(getPetrinet(log,'Uploads/petrinet/%s.png' % filename))
    return {
     "activitiesCount": activitiesCount,
     "eventCount": eventCount, 
     "meanDurchlaufzeit": meanDurchlaufzeit,
     "resourceCount": resourceCount,
     "durchlaufzeit" : durchlaufzeit,
     "image": os.path.join(app.config['UPLOAD_PATH'],'petrinet','%s.png' % filename)
      }


@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

@app.route('/uploads/petrinet/<filename>')
def petrinet(filename):
    string = 'Uploads/petrinet/%s' % filename
    print(string)
    return send_file(string, mimetype='image/svg')


if __name__ == "__main__":
    app.run(debug=True)