# imports
import os
from flask_cors import CORS
from pycode.statistics.statistics import *
import pandas as pd
import pickle
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, abort, send_from_directory, send_file
from werkzeug.utils import secure_filename
from flask import jsonify
from flask_pymongo import PyMongo
import urllib 

# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string

from magic_admin import Magic
# A util provided by `magic_admin` to parse the auth header value.
from magic_admin.utils.http import parse_authorization_header_value
from magic_admin.error import DIDTokenError
from magic_admin.error import RequestError


# config
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://Random:"+ urllib.parse.quote("123qwe")+"@cluster0.ec6t5.mongodb.net/Cluster0?retryWrites=true&w=majority"

app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.csv','.xes']
app.config['UPLOAD_PATH'] = 'Uploads'
CORS(app)
mongo = PyMongo(app)


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
    
    with open('log-%s.pickle'%filename, 'wb') as handle:
        pickle.dump(log, handle)

    df = createDataFrame(log)

    with open('df-%s.pickle'%filename, 'wb') as handle:
        pickle.dump(df, handle)


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
    string = 'Uploads/petrinet/%s.png' % filename
    print(string)
    return send_file(string, mimetype='image/svg')

@app.route('/api/eventcount/<filename>')
def eventcount(filename):
    with open('df-%s.pickle'%filename, 'rb') as handle:
        b = pickle.load(handle)

    return {'data':getEventCount(b)}

@app.route('/api/uniqueActivitiesCount/<filename>')
def activities(filename):
    with open('df-%s.pickle'%filename, 'rb') as handle:
            b = pickle.load(handle)
    temp = getUniqueActivities(b)
    print(temp['count'])
    return {'data':temp['count']}

@app.route('/api/activitesArray/<filename>')
def activitiesArray(filename):
    with open('df-%s.pickle'%filename, 'rb') as handle:
            b = pickle.load(handle)
    arr = []
    for index, value in getActivitesCount(b).items():
        arr = arr + [{'id': index,'label':index ,'value':value}]
    print(arr)
    return {'data':arr}

@app.route('/v1/user/login', methods=['POST'])
def user_login():
    did_token = parse_authorization_header_value(
        request.headers.get('Authorization'),
    )
    if did_token is None:
        raise BadRequest(
            'Authorization header is missing or header value is invalid',
        )

    magic = Magic(api_secret_key='sk_test_5EBD84CF6985F693')

    # Validate the did_token.
    try:
        magic.Token.validate(did_token)
        issuer = magic.Token.get_issuer(did_token)
        user_meta = magic.User.get_metadata_by_issuer(issuer)

    except DIDTokenError as e:
        raise BadRequest('DID Token is invalid: {}'.format(e))
    except RequestError as e:
        # You can also remap this error to your own application error.
        return HttpError(str(e))



    email = user_meta.data['email']
    issuer = user_meta.data['issuer']
    public_address =  user_meta.data['public_address']
    
    # Call your appilication logic to load the user.
        
    user_info = mongo.db.users.find_one({"email":email})
    if(user_info == None):
        dic = {"public_address": public_address, "email":email, "issuer": issuer}
        user_info = mongo.db.users.insert_one(dic)
    
    
    if user_info['issuer'] != issuer:
        return UnAuthorizedError('UnAuthorized user login')


    return jsonify({"did_token":did_token,"ok": True})

# @app.route('/files', methods=['GET'])
# def getFiles():
#     print(request.headers)
#     did_token = parse_authorization_header_value(
#         request.headers.get('Authorization'),
#     )
#     print(did_token)
#     if did_token is None:
#         raise BadRequest(
#             'Authorization header is missing or header value is invalid',
#         )

#     magic = Magic(api_secret_key='sk_test_5EBD84CF6985F693')

#     # Validate the did_token.
#     try:
#         magic.Token.validate(did_token)
#         issuer = magic.Token.get_issuer(did_token)
#         user_meta = magic.User.get_metadata_by_issuer(issuer)

#     except DIDTokenError as e:
#         raise BadRequest('DID Token is invalid: {}'.format(e))
#     except RequestError as e:
#         # You can also remap this error to your own application error.
#         return HttpError(str(e))

#     if user_info['issuer'] != issuer:
#         return UnAuthorizedError('UnAuthorized user login')


  
    
#     # Call your appilication logic to load the user.
        
#     files = mongo.db.files.find({"email":email})
    
#     print(files)
    
   

#     return files,200



if __name__ == "__main__":
    app.run(debug=True)