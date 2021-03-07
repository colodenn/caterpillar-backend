from pm4py.objects.log.importer.xes import importer as xes_importer
import pandas as pd
import numpy as np
from pm4py.statistics.traces.log import case_statistics
from pm4py.statistics.traces.log import case_statistics
from pm4py.objects.log.util import interval_lifecycle
from pm4py.objects.log.importer.xes import importer as xes_importer

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

def createLog(path):
    variant = xes_importer.Variants.ITERPARSE
    parameters = {variant.value.Parameters.TIMESTAMP_SORT: True}
    log = xes_importer.apply(os.path.join(path, filename),
                            variant=variant, parameters=parameters)

def dictToArray(dic):
    arr = []
    for key in dic:
        arr.append({"name": key, "count": dic[key]})

    return arr