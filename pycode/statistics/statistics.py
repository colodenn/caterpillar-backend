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
import ast


def dictToArray(dic):
    arr = []
    for key in dic:
        arr.append({"name": key, "count": dic[key]})

    return arr


def getUniqueActivities(df):
    return {"count": len(df["concept:name"].unique()), "activities": df["concept:name"].unique().tolist()}


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
    start = df['time:timestamp'].min()
    end = df['time:timestamp'].max()
    return (start, end)


def getCaseCount(df):
    """Get case count

    Args:
        df (Dataframe): Pandas dataframe

    Returns:
        Integer: case count 
    """
    return (len(df['caseid'].unique()))


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


def getMedianDurchlaufzeit(log):
    """Mean throughputtime

    Args:
        log (Eventlog): PM4PY Eventlog

    Returns:
        Float: Mean throughputtime
    """
    median_case_duration = case_statistics.get_median_caseduration(log, parameters={
        case_statistics.Parameters.TIMESTAMP_KEY: "time:timestamp"
    })
    day = median_case_duration // (24 * 3600)
    time = median_case_duration % (24 * 3600)
    hour = time // 3600
    time %= 3600
    minutes = time // 60
    time %= 60
    seconds = time
    return ("%dD:%dH:%dM:%dS" % (day, hour, minutes, seconds))


def getAllDurchlaufzeit(log):
    all_case_durations = case_statistics.get_all_casedurations(log, parameters={
        case_statistics.Parameters.TIMESTAMP_KEY: "time:timestamp"})

    return all_case_durations


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
    """Get Resource Count

    Args:
        df (dataframe): Dataframe

    Returns:
        [array]: [array of dicts (["id": "test", "label": "test", "value": 1337])]
    """
    arr = []
    temp = ast.literal_eval(df['org:resource'].value_counts().to_json())
    for i in temp:
        arr += [{"id": i, "label": i, "value": temp[i]}]
    return (arr)


def getUniqueResource(df):
    return (len(df["org:resource"].unique()), df["org:resource"].unique())


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


def createLog(path, filename):
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


def getPetrinet(log, path):
    # TODO: save as svg not png
    net, im, fm = heuristics_miner.apply(log, parameters={
                                         heuristics_miner.Variants.CLASSIC.value.Parameters.DEPENDENCY_THRESH: 0.1})

    gviz = pn_visualizer.apply(net, im, fm)
    image = pn_visualizer.save(gviz, path)

    return image


# Varianzen von Margarete

def deltaCountActivitiesSame(df1, df2):
    """Anzahl Doppelte Aktivitäten 

    Args:
        df (Dataframe): Pandas dataframe, df (Dataframe): Pandas dataframe

    Returns:
        int
    """

    a = np.concatenate([df1['concept:name'].unique(),
                       df2['concept:name'].unique()])
    return len([item for item, count in collections.Counter(a).items() if count > 1])


def deltaActivitiesSame(df1, df2):
    """ Doppelte Aktivitäten 

    Args:
        df (Dataframe): Pandas dataframe, df (Dataframe): Pandas dataframe

    Returns:

    """
    a = np.concatenate([df1['concept:name'].unique(),
                       df2['concept:name'].unique()])
    return [item for item, count in collections.Counter(a).items() if count > 1]


def deltaCountActivitiesDiff(df1, df2):
    """Anzahl Unteschiedliche Aktivitäten 

    Args:
        df (Dataframe): Pandas dataframe, df (Dataframe): Pandas dataframe

    Returns:
        int
    """

    a = np.concatenate([df1['concept:name'].unique(),
                       df2['concept:name'].unique()])
    return len([item for item, count in collections.Counter(a).items() if count == 1])


def deltaActivitiesDiff(df1, df2):
    """ Unteschiedliche Aktivitäten 

    Args:
        df (Dataframe): Pandas dataframe, df (Dataframe): Pandas dataframe

    Returns:

    """
    a = np.concatenate([df1['concept:name'].unique(),
                       df2['concept:name'].unique()])
    return [item for item, count in collections.Counter(a).items() if count == 1]


def deltaActivitiesCount(df1, df2):  # funtioniert noch nicht
    """Häufigkeit je Doppelte Aktivität

    Args:
        df (Dataframe): Pandas dataframe, df (Dataframe): Pandas dataframe

    Returns:

    """
    a = np.concatenate([df1['concept:name'].unique(),
                       df2['concept:name'].unique()])
    dublicate = [item for item, count in collections.Counter(
        a).items() if count > 1]


def deltaEvents(df1, df2):
    """Differenz Anzahl Events 

    Args:
        df (Dataframe): Pandas dataframe, df (Dataframe): Pandas dataframe

    Returns:
        int
    """
    x = (getEventCount(df1) - getEventCount(df2))
    if x > 0:
        return x
    return -x


def deltaStartEnd(df1, df2):  # schönere Ausgabe, vielleicht nur Zeitunterschied
    """jeweils Start,End

    Args:
        df (Dataframe): Pandas dataframe, df (Dataframe): Pandas dataframe

    Returns:
        Tupel: (Tuple: (Start timestamp, End timestamp),Tuple: (Start timestamp, End timestamp))
    """
    return (getStartEnd(df1), getStartEnd(df2))


def deltaCases(df1, df2):
    """Differenz Anzahl Cases 

    Args:
        df (Dataframe): Pandas dataframe, df (Dataframe): Pandas dataframe

    Returns:
        int
    """
    x = (getCaseCount(df1) - getCaseCount(df2))
    if x > 0:
        return x
    return -x


def deltaMeanDurchlaufzeit(log1, log2):
    """Differnz Mean Durchlaufzeit

    Args:
        log (Eventlog): PM4PY Eventlog,log (Eventlog): PM4PY Eventlog

    Returns:
        float
    """
    x = getMeanDurchlaufzeit(log1) - getMeanDurchlaufzeit(log2)
    if x > 0:
        return x
    return -x


# def zu Waitingtime

def deltaCountResourcesSame(df1, df2):
    """Anzahl Doppelte Resourcen 

    Args:
        df (Dataframe): Pandas dataframe, df (Dataframe): Pandas dataframe

    Returns:
        int
    """

    a = np.concatenate([df1['org:resource'].unique(),
                       df2['org:resource'].unique()])
    return len([item for item, count in collections.Counter(a).items() if count > 1])


def deltaResourcesSame(df1, df2):
    """ Gleiche Resourcen 

    Args:
        df (Dataframe): Pandas dataframe, df (Dataframe): Pandas dataframe

    Returns:

    """
    a = np.concatenate([df1['org:resource'].unique(),
                       df2['org:resource'].unique()])
    return [item for item, count in collections.Counter(a).items() if count > 1]


def deltaCountResourcesDiff(df1, df2):
    """Anzahl unterschieldiche Resourcen 

    Args:
        df (Dataframe): Pandas dataframe, df (Dataframe): Pandas dataframe

    Returns:
        int
    """

    a = np.concatenate([df1['org:resource'].unique(),
                       df2['org:resource'].unique()])
    return len([item for item, count in collections.Counter(a).items() if count == 1])


def deltaResourcesDiff(df1, df2):
    """ Unterschiedliche Resourcen 

    Args:
        df (Dataframe): Pandas dataframe, df (Dataframe): Pandas dataframe

    Returns:

    """
    a = np.concatenate([df1['org:resource'].unique(),
                       df2['org:resource'].unique()])
    return [item for item, count in collections.Counter(a).items() if count == 1]


def getTable(df):
    df['time:timestamp'] = df['time:timestamp'].apply(
        lambda x: x.strftime('%Y-%m-%d '))
    return df.head(10).to_dict('records')
