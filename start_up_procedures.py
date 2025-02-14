from nemosis import data_fetch_methods
import datetime
import requests
import json


def update_nemosis_cache():
    start_time = "{}/01/01 00:00:00".format(2012,)
    end_time = "{}/01/01 00:00:00".format(int(datetime.datetime.now().year,) + 1)
    table = "TRADINGPRICE"
    raw_data_cache = 'data/aemo_raw_cache/'
    price_data = data_fetch_methods.dynamic_data_compiler(start_time, end_time, table, raw_data_cache)


def update_tariffs():
    network_version = update_tariff_set('network')
    retail_version = update_tariff_set('retail')
    return network_version, retail_version


def update_tariff_set(type):
    try:
        response = requests.get('http://api.ceem.org.au/electricity-tariffs/{}'.format(type))
        if response.status_code != 404:
            tariffs = response.json()
            version = tariffs[0]['Version']
            folder_and_name = 'data/{a}_tariff_set_versions/{a}Tariffs_{b}.json'.format(a=type.title(), b=version)
            # Write contents to the file in the 'data' folder that acts as the active tariff data set.
            with open(folder_and_name, 'wt') as json_file:
                json.dump(tariffs, json_file)
            return tariffs[0]['Version']
    except:
        return None
