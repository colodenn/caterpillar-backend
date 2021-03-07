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
    """Get event count of dataframe

    Args:
        df (Dataframe): Pandas dataframe

    Returns:
        Integer: Number of Events
    """
    return len(df)

def getStartEnd(df):
    """Get Start and End timestamp from dataframe

    Args:
        df (Dataframe): Pandas dataframe

    Returns:
        Tuple: (Start timestamp, End timestamp)
    """
    start = df.iloc[0]['time:timestamp']
    end = df.iloc[-1]['time:timestamp']
    return (start,end)

def getCaseCount(df):
    """Get case count

    Args:
        df (Dataframe): Pandas dataframe

    Returns:
        Integer: case count 
    """
    return (len(df['caseid']))

def getDurchlaufzeit(log):
    """Get Throughputtime

    Args:
        log (Eventlog): PM4PY Eventlog

    Returns:
        [list]: Returns throughputtime per case
    """
    all_case_durations = case_statistics.get_all_casedurations(log, parameters={
    case_statistics.Parameters.TIMESTAMP_KEY: "time:timestamp"})
    return all_case_durations

def getMeanDurchlaufzeit(log):
    """Mean throughputtime

    Args:
        log (Eventlog): PM4PY Eventlog

    Returns:
        Float: Mean throughputtime
    """
    median_case_duration = case_statistics.get_median_caseduration(log, parameters={
        case_statistics.Parameters.TIMESTAMP_KEY: "time:timestamp"
    })
    return median_case_duration
      
def getWaitingtime(log):
    """Get Waitingtime

    Args:
        log (EventLog): PM4PY Eventlog

    Returns:
        Eventlog: Returns enrichedlog with additional information about waiting time
    """
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

def createLog(path,filename):
    variant = xes_importer.Variants.ITERPARSE
    parameters = {variant.value.Parameters.TIMESTAMP_SORT: True}
    log = xes_importer.apply(os.path.join(path, filename),
                            variant=variant, parameters=parameters)
    return log

def dictToArray(dic):
    arr = []
    for key in dic:
        arr.append({"name": key, "count": dic[key]})

    return arr

def getPetrinet(log,path):
    net, im, fm = heuristics_miner.apply(log, parameters={heuristics_miner.Variants.CLASSIC.value.Parameters.DEPENDENCY_THRESH: 0.99})
    gviz = pn_visualizer.apply(net, im, fm)
    image = pn_visualizer.save(gviz,path)

    return image