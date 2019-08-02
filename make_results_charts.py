import plotly
import plotly.graph_objs as go
import pandas as pd
import json
import numpy as np
from time import time


def bill_distribution(results, name):
    chart = go.Histogram(x=results['Bill'], histnorm='probability', name=name)
    return chart


results_chart_methods = {'Bill Distribution': bill_distribution}


def dual_variable_chart_method(data, x_axis, y_axis, name):
    chart = go.Scattergl(x=data[x_axis], y=data[y_axis], mode='markers', name=name)
    return chart


def is_component(suffixes, name_to_check):
    for suffix in suffixes:
        if suffix in name_to_check:
            return True
    return False


def bill_components(data):
    data = data.sort_values('Bill', ascending=False)
    data = data.reset_index(drop=True)
    traces = []
    compenent_suffixes = ['Retailer', 'DUOS', 'NUOS', 'TUOS', 'DTOUS']
    potential_components = [col for col in data.columns if is_component(compenent_suffixes, col)]
    for component in potential_components:
        trace = dict(
            name=component,
            x=data.index.values,
            y=data[component],
            mode='lines',
            stackgroup='one'
        )
        traces.append(trace)
    return traces


single_case_chart_methods = {'bill_components': bill_components}