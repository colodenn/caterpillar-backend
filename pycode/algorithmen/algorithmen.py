from pm4py.objects.log.importer.xes import importer as xes_importer
import pandas as pd
import numpy as np
import os
from pm4py.statistics.traces.log import case_statistics
from pm4py.statistics.traces.log import case_statistics
from pm4py.objects.log.util import interval_lifecycle
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.visualization.petrinet import visualizer as pn_visualizer

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

def getLog(request,filename):
    """Open Log

    Args:
        request (Request): Request
        filename (String): Filename

    Returns:
        File: returns File
    """
    
    did_token = request.headers.get('api_token')
    issuer, user_meta,did_token = checkLogin(did_token)
    with open('Uploads/log-{}-{}.pickle'.format(filename,issuer), 'rb') as handle:
            b = pickle.load(handle)
    return b

def getDf(request,filename):
    """Open Dataframe

    Args:
        request (Request): Request
        filename (String): Filename

    Returns:
        File: returns File
    """
    did_token = request.headers.get('api_token')
    issuer, user_meta,did_token = checkLogin(did_token)
    with open('Uploads/df-{}-{}.pickle'.format(filename,issuer), 'rb') as handle:
            b = pickle.load(handle)
    return b
