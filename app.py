import imghdr
from flask_cors import CORS
from pm4py.objects.log.importer.xes import importer as xes_importer
import pandas as pd
import numpy as np
from pm4py.statistics.traces.log import case_statistics
from pm4py.statistics.traces.log import case_statistics
from pm4py.objects.log.util import interval_lifecycle

import os
from flask import Flask, render_template, request, redirect, url_for, abort, \
    send_from_directory
from werkzeug.utils import secure_filename
from flask import jsonify
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.csv','.xes']
app.config['UPLOAD_PATH'] = 'Uploads'
CORS(app)


@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413

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
    from pm4py.objects.log.importer.xes import importer as xes_importer
    variant = xes_importer.Variants.ITERPARSE
    parameters = {variant.value.Parameters.TIMESTAMP_SORT: True}
    log = xes_importer.apply(os.path.join(app.config['UPLOAD_PATH'], filename),
                            variant=variant, parameters=parameters)
    def createDataFrame(log):
        newlog = []
        caseid = 0
        df = []
        for l in log:
            caseid += 1
            for i in l:
                i['caseid'] = caseid
                newlog = newlog + [i] 
        df = pd.DataFrame(newlog)
        return df

    df = createDataFrame(log)

    activitiesCount = getActivitesCount(df).to_dict()
    activitiesCount = dictToArray(activitiesCount)
    print(type(activitiesCount))
    eventCount = getEventCount(df)
    print(type(eventCount))

    meanDurchlaufzeit = getMeanDurchlaufzeit(log)
    print(type(meanDurchlaufzeit))

    resourceCount = getResourceCount(df).to_dict()
    resourceCount = dictToArray(resourceCount)


    durchlaufzeit = getDurchlaufzeit(log)
    print(type(durchlaufzeit))



    return {
     "activitiesCount": activitiesCount,
     "eventCount": eventCount, 
     "meanDurchlaufzeit": meanDurchlaufzeit,
     "resourceCount": resourceCount,
     "durchlaufzeit" : durchlaufzeit
      }

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


def dictToArray(dic):
    arr = []
    for key in dic:
        arr.append({"name": key, "count": dic[key]})

    return arr

def getUniqueActivities(df):
    return (len(df["concept:name"].unique()),df["concept:name"].unique())

def getActivitesCount(df):
    return df["concept:name"].value_counts()

def getEventCount(df):
    return len(df)

def getStartEnd(df):
    start = df.iloc[0]['time:timestamp']
    end = df.iloc[-1]['time:timestamp']
    return (start,end)

def getEventCount(df):
    return (len(df['caseid']))

def getDurchlaufzeit(log):
    all_case_durations = case_statistics.get_all_casedurations(log, parameters={
    case_statistics.Parameters.TIMESTAMP_KEY: "time:timestamp"})
    return all_case_durations

def getMeanDurchlaufzeit(log):
    median_case_duration = case_statistics.get_median_caseduration(log, parameters={
        case_statistics.Parameters.TIMESTAMP_KEY: "time:timestamp"
    })
    
    return median_case_duration
              
def getWaitingtime(log):
    enriched_log = interval_lifecycle.assign_lead_cycle_time(log)
    return enriched_log

def getResourceCount(df):
    return (df['org:resource'].value_counts())

def getUniqueResource(df):
    return (len(df["org:resource"].unique()),df["org:resource"].unique())

if __name__ == "__main__":
    app.run()