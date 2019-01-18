from flask import Flask, render_template, request, jsonify
import os
from pyfladesk import init_gui
import sys
import pandas as pd
import feather
import time
import helper_functions

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


if getattr(sys, 'frozen', False):
    template_folder = resource_path('templates')
    static_folder = resource_path('static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)


# Here you go to http://127.0.0.1:5000/
@app.route('/')
def index():
    return render_template('index.html', my_name="Nick")


# Here you go to http://127.0.0.1:5000/data
@app.route('/data')
def data():
    return jsonify(
        {'data': [1, 2, 3, 4, 5]}
    )


@app.route('/load_names')
def load_names():
    load_names = []
    for file_name in os.listdir('data/'):
        load_names.append(file_name)
    return jsonify(load_names)


@app.route('/load_load/<name>')
def load_load(name):
    t0 = time.time()
    load = feather.read_dataframe('data/'+name)
    load = helper_functions.calc_mean_daily_load(load)
    return jsonify({'Time': list(load.READING_DATETIME), "Mean": list(load['mean'])})


@app.route('/filtered_load_data', methods=['POST'])
def filtered_load_data():
    load_request = request.get_json()
    demo_info_file_name = helper_functions.find_loads_demographic_file(load_request['file_name'])
    demo_info = pd.read_csv('data/' + demo_info_file_name, dtype=str)
    load = feather.read_dataframe('data/' + load_request['file_name'])
    for column_name, selected_options in load_request['filter_options'].items():
        if 'All' not in selected_options:
            demo_info = demo_info[demo_info[column_name].isin(selected_options)]
    load = load.loc[:, ['READING_DATETIME'] + list(demo_info['CUSTOMER_KEY'])]
    if len(load.columns) > 1:
        load = helper_functions.calc_mean_daily_load(load)
        load_as_json = jsonify({'Time': list(load.READING_DATETIME), "Mean": list(load['mean'])})
    else:
        load_as_json = jsonify({'Time': [], "Mean": []})
    return load_as_json



@app.route('/demo_options/<name>')
def demo_options(name):
    demo_config_file_name = helper_functions.find_loads_demographic_config_file(name)
    demo_file_name = helper_functions.find_loads_demographic_file(name)
    if demo_config_file_name != '' and demo_config_file_name in os.listdir('data/'):
        demo_config = pd.read_csv('data/'+demo_config_file_name)
        columns_to_use = demo_config[demo_config['use'] == 1]
        n = len(columns_to_use['actual_names']) if len(columns_to_use['actual_names']) < 10 else 10
        actual_names = list(columns_to_use['actual_names'].iloc[:n])
        display_names = list(columns_to_use['display_names'])
    elif demo_file_name != '' and demo_file_name in os.listdir('data/'):
        demo = pd.read_csv('data/' + demo_file_name)
        n = len(demo.columns) if len(demo.columns) < 11 else 11
        actual_names = list(demo.columns[1:n])
        display_names = list(demo.columns[1:n])
    else:
        actual_names = []
        display_names = []

    options = {}
    display_names_dict = {}
    for name, display_name in zip(actual_names, display_names):
        options[name] = ['All'] + list([str(val) for val in demo[name].unique()])
        display_names_dict[name] = display_name

    return jsonify({'actual_names': actual_names, "display_names": display_names_dict, "options": options})


if __name__ == '__main__':
    app.run(debug=True)

    #init_gui(app, width=1200, height=800, window_title='TDA')  # This one runs it as a standalone app