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


def cooleFunktion(df):

    return df