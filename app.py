import os
from flask_cors import CORS, cross_origin
from pycode.statistics.statistics import *
import pandas as pd
import pickle
import numpy as np
from flask import Flask, json, render_template, request, redirect, url_for, abort, send_from_directory, send_file
from werkzeug.utils import secure_filename
from flask import jsonify
from flask_pymongo import PyMongo
import urllib
from bson.json_util import dumps
from magic_admin import Magic
from magic_admin.utils.http import parse_authorization_header_value
from magic_admin.error import DIDTokenError
from magic_admin.error import RequestError
from magic_admin.error import BadRequestError
import hashlib

# config
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://Random:" + urllib.parse.quote(
    "123qwe")+"@cluster0.ec6t5.mongodb.net/Cluster0?retryWrites=true&w=majority"
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MAX_CONTENT_LENGTH'] = 50000 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.csv', '.xes']
app.config['UPLOAD_PATH'] = 'Uploads'
mongo = PyMongo(app)


@app.route('/api/test')
def test():
    return "<h1>test</h1>"


@app.after_request
def add_headers(response):
    response.headers.add('Content-Type', 'application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods',
                         'PUT, GET, POST, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Expose-Headers',
                         'Content-Type,Content-Length,Authorization,X-Pagination')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


@app.route('/api/uploadFile', methods=['POST', 'OPTIONS'])
def uploadFile():
    try:
        did_token1 = request.cookies.get('api_token')[:-3] + "="
        issuer, user_meta, did_token = checkLogin(did_token1)
    except:
        return "401"

    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            return 400
    uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    log = createLog(app.config['UPLOAD_PATH'], filename)
    with open('Uploads/log-{}-{}.pickle'.format(filename, issuer), 'wb') as handle:
        pickle.dump(log, handle)
    df = createDataFrame(log)
    with open('Uploads/df-{}-{}.pickle'.format(filename, issuer), 'wb') as handle:
        pickle.dump(df, handle)

    getPetrinet(log, 'Uploads/petrinet-{}-{}.png'.format(filename, issuer))
    string = str(filename) + str(issuer)
    result = hashlib.md5(string.encode())
    mydict = {"filename": filename,
              "user":  issuer, "slug": result.hexdigest()}
    mongo.db.files.insert_one(mydict)

    data = {"i": "0", "x": 0, "y": 0, "w": 2, "h": 1,
            "name": "choose template", "type": "template"}

    mongo.db.tiles.insert_one(
        {"user": issuer, "filename": filename, "data": [data]})
    return "200"


@app.route('/api/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


@app.route('/api/uploads/petrinet/<filename>')
def petrinet(filename):
    did_token = request.cookies.get('api_token')[:-3] + "="
    print(request.cookies.get('api_token')[:-3] + "=")
    issuer, user_meta, did_token = checkLogin(did_token)
    string = 'Uploads/petrinet-{}-{}.png'.format(filename, issuer)
    return send_file(string, mimetype='image/svg')


@app.route('/api/eventcount/<filename>', methods=['GET', 'OPTIONS'])
def eventcount(filename):
    b = getDf(request, filename)
    return {'data': getEventCount(b)}


@app.route('/api/uniqueActivitiesCount/<filename>')
def activities(filename):
    did_token = request.cookies.get('api_token')[:-3] + "="
    print(request.cookies.get('api_token')[:-3] + "=")
    issuer, user_meta, did_token = checkLogin(did_token)
    with open('Uploads/df-{}-{}.pickle'.format(filename, issuer), 'rb') as handle:
        b = pickle.load(handle)
    temp = getUniqueActivities(b)
    return {'data': temp['count']}


@app.route('/api/activitesArray/<filename>')
def activitiesArray(filename):
    did_token = request.cookies.get('api_token')[:-3] + "="
    issuer, user_meta, did_token = checkLogin(did_token)
    with open('Uploads/df-{}-{}.pickle'.format(filename, issuer), 'rb') as handle:
        b = pickle.load(handle)
    arr = []
    for index, value in getActivitesCount(b).items():
        arr = arr + [{'id': index, 'label': index, 'value': value}]
    return {'data': arr}


@app.route('/api/medianThroughputtime/<filename>')
def medianThroughputtime(filename):
    did_token = request.cookies.get('api_token')[:-3] + "="
    issuer, user_meta, did_token = checkLogin(did_token)
    with open('Uploads/log-{}-{}.pickle'.format(filename, issuer), 'rb') as handle:
        b = pickle.load(handle)
    arr = getMedianDurchlaufzeit(b)
    return {'data': arr}


@app.route('/api/StartEnd/<filename>')
def StartEnd(filename):
    b = getDf(request, filename)
    arr = getStartEnd(b)
    return {'data': arr}


@app.route('/api/CaseCount/<filename>')
def CaseCount(filename):
    did_token = request.cookies.get('api_token')[:-3] + "="
    issuer, user_meta, did_token = checkLogin(did_token)
    with open('Uploads/df-{}-{}.pickle'.format(filename, issuer), 'rb') as handle:
        b = pickle.load(handle)
    arr = getCaseCount(b)
    return {'data': arr}


@app.route('/api/Throughputtime/<filename>')
def Throughputtime(filename):
    did_token = request.cookies.get('api_token')[:-3] + "="
    issuer, user_meta, did_token = checkLogin(did_token)
    with open('Uploads/log-{}-{}.pickle'.format(filename, issuer), 'rb') as handle:
        b = pickle.load(handle)
    arr = getAllDurchlaufzeit(b)
    print(len(arr))
    print(arr)
    arr = []
    return {'data': arr}


@app.route('/api/UniqueResource/<filename>')
def UniqueResource(filename):
    b = getDf(request, filename)
    arr = getUniqueResource(b)
    return {'data': arr}


@app.route('/api/columns/<filename>')
def columns(filename):
    b = getDf(request, filename)
    columns = b.columns.values.tolist()
    return {'columns': columns}


@app.route('/api/ResourceCount/<filename>')
def Ressource(filename):
    b = getDf(request, filename)
    arr = getResourceCount(b)
    return {'data': arr}


@app.route('/api/customPieChart/<filename>')
def custom(filename):
    return {'data': []}


@app.route('/api/getTable/<filename>')
def table(filename):
    b = getDf(request, filename)
    arr = getTable(b)
    print(arr[0])
    print(type(arr[0]))

    return {'data': arr}


@app.route('/api/v1/user/login', methods=['POST'])
def user_login():
    did_token = parse_authorization_header_value(
        request.headers.get('Authorization'),
    )
    if did_token is None:
        raise BadRequestError(
            'Authorization header is missing or header value is invalid',
        )
    magic = Magic(api_secret_key='sk_test_5EBD84CF6985F693')

    # Validate the did_token.
    try:
        magic.Token.validate(did_token)
        issuer = magic.Token.get_issuer(did_token)
        user_meta = magic.User.get_metadata_by_issuer(issuer)

    except DIDTokenError as e:
        raise BadRequestError('DID Token is invalid: {}'.format(e))
    except RequestError as e:
        # You can also remap this error to your own application error.
        return HttpError(str(e))
    email = user_meta.data['email']
    issuer = user_meta.data['issuer']
    public_address = user_meta.data['public_address']
    # Call your appilication logic to load the user.
    user_info = mongo.db.users.find_one({"email": email})
    if(user_info == None):
        dic = {"public_address": public_address,
               "email": email, "issuer": issuer}
        user_info = mongo.db.users.insert_one(dic)
    if user_info['issuer'] != issuer:
        return UnAuthorizedError('UnAuthorized user login')
    return jsonify({"did_token": did_token, "ok": True})


@app.route('/api/tiles/add/<filename>', methods=['POST', 'OPTIONS'])
def postTiles(filename):
    try:
        did_token1 = request.cookies.get('api_token')[:-3] + "="
    except:
        return "401"

    issuer, user_meta, did_token = checkLogin(did_token1)
    string = str(filename) + str(issuer)
    result = hashlib.md5(string.encode())
    print(request.json)
    if(mongo.db.tiles.count({"user": issuer, "filename": filename}) > 0):
        tiles = mongo.db.tiles.update_one({"user": issuer, "filename": filename}, {"$set": {
            "data": request.json['data']}})
    else:
        print(request.json['data'])
        mongo.db.tiles.insert_one(
            {"user": issuer, "filename": filename, "data": request.json['data']})
    return "200"


@app.route('/api/tiles/all/<filename>', methods=['POST', 'OPTIONS'])
def postTilesAll(filename):
    try:
        did_token1 = request.cookies.get('api_token')[:-3] + "="
    except:
        return "401"

    issuer, user_meta, did_token = checkLogin(did_token1)
    string = str(filename) + str(issuer)
    result = hashlib.md5(string.encode())
    if(mongo.db.tiles.count({"user": issuer, "filename": filename}) > 0):
        tiles = mongo.db.tiles.update_one({"user": issuer, "filename": filename}, {"$set": {
            "data": request.json['data']}})
    else:
        print(request.json['data'])
        mongo.db.tiles.insert_one(
            {"user": issuer, "filename": filename, "data": request.json['data']})
    return "200"


@app.route('/api/share/create/<filename>', methods=['GET', 'OPTIONS'])
def createShare(filename):
    did_token = request.cookies.get('api_token')[:-3] + "="
    issuer, user_meta, did_token = checkLogin(did_token)
    string = str(filename) + str(issuer)
    result = hashlib.md5(string.encode())

    tiles = mongo.db.tiles.update_one({"user": issuer, "filename": filename}, {"$set": {
        "slug": result.hexdigest()}})
    print(tiles)
    return {"data": result.hexdigest()}


@app.route('/api/tiles/<filename>', methods=['GET', 'OPTIONS'])
def getTiles(filename):
    did_token = request.cookies.get('api_token')[:-3] + "="
    issuer, user_meta, did_token = checkLogin(did_token)
    tiles = mongo.db.tiles.find_one({"user": issuer, "filename": filename})
    try:
        return {"data": tiles.get('data')}
    except:
        return {"data": []}


@app.route('/api/share/<filename>', methods=['GET', 'OPTIONS'])
def getShare(filename):
    tiles = mongo.db.tiles.find_one({"slug": filename})
    print(tiles)
    try:
        return {"data": tiles.get('data')}
    except:
        return "500"


@app.route('/api/files', methods=['GET', 'OPTIONS'])
def getFiles():
    try:
        did_token = request.cookies.get('api_token')[:-3] + "="
        issuer, user_meta, did_token = checkLogin(did_token)
    except:
        return jsonify({"files": []}), 401
    files = mongo.db.files.find({"user": issuer})
    arr = []
    for f in files:
        arr.append({"name": f['filename']})
    return jsonify({"files": arr})


@app.route('/api/file/<filename>', methods=['DELETE', 'OPTIONS'])
def deleteFile(filename):
    did_token = request.cookies.get('api_token')[:-3] + "="
    issuer, user_meta, did_token = checkLogin(did_token)
    files = mongo.db.files.delete_one({"filename": filename, "user": issuer})
    if os.path.exists('Uploads/log-{}-{}.pickle'.format(filename, issuer)):
        os.remove('Uploads/log-{}-{}.pickle'.format(filename, issuer))
    else:
        print("The file does not exist")
    if os.path.exists('Uploads/df-{}-{}.pickle'.format(filename, issuer)):
        os.remove('Uploads/df-{}-{}.pickle'.format(filename, issuer))
    else:
        print("The file does not exist")
    if os.path.exists('Uploads/{}'.format(filename)):
        os.remove('Uploads/{}'.format(filename))
    else:
        print("The file does not exist")
    try:
        mongo.db.tiles.delete_one({"filename": filename, "user": issuer})
    except:
        print("cant delete entry")
    return "200"
    return issuer, user_meta, did_token


def checkLogin(did_token):
    if did_token is None:
        raise BadRequestError(
            'Authorization header is missing or header value is invalid',
        )

    magic = Magic(api_secret_key='sk_test_5EBD84CF6985F693')

    # Validate the did_token.
    try:
        magic.Token.validate(did_token)
        issuer = magic.Token.get_issuer(did_token)
        user_meta = magic.User.get_metadata_by_issuer(issuer)

    except DIDTokenError as e:
        raise BadRequestError('DID Token is invalid: {}'.format(e))
    except RequestError as e:
        # You can also remap this error to your own application error.
        print('requesterror')
        return HttpError(str(e))

    # if user_meta['issuer'] != issuer:
    #     return UnAuthorizedError('UnAuthorized user login')

    return issuer, user_meta, did_token


def getLog(request, filename):
    """Open Log
    Args:
        request (Request): Request
        filename (String): Filename
    Returns:
        File: returns File
    """

    did_token = request.cookies.get('api_token')[:-3] + "="
    issuer, user_meta, did_token = checkLogin(did_token)
    with open('Uploads/log-{}-{}.pickle'.format(filename, issuer), 'rb') as handle:
        b = pickle.load(handle)
    return b


def getDf(request, filename):
    """Open Dataframe
    Args:
        request (Request): Request
        filename (String): Filename
    Returns:
        File: returns File
    """
    did_token = request.cookies.get('api_token')[:-3] + "="
    issuer, user_meta, did_token = checkLogin(did_token)
    with open('Uploads/df-{}-{}.pickle'.format(filename, issuer), 'rb') as handle:
        b = pickle.load(handle)
    return b


if __name__ == "__main__":
    app.run(debug=True, host='localhost')
