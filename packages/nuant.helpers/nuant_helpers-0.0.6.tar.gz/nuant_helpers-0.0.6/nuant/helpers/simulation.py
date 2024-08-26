import requests
import gzip
import json
from io import BytesIO
import datetime


def fetch_data(simulation_id, file, api_key='', api_url="https://data.ptn.cobrabreiz.services/graphql"):
    try:
        list_files = fetch_list_files(simulation_id, api_key, api_url)

        time_resul_link = list_files[file]

        response_file = requests.request("GET", time_resul_link)

        buffer_data = BytesIO(response_file.content)

        result_file = gzip.GzipFile(fileobj=buffer_data).read()

        return json.loads(result_file)
    except Exception as e:
        print("An exception occurred: %s" % repr(e))


def fetch_list_files(simulation_id, api_key='', api_url="https://data.ptn.cobrabreiz.services/graphql"):
    try:
        payload = ("{\"query\":\" query {\\n    simulationGet(id: \\\"%s\\\") {\\n        id\\n        status\\n        "
                   "startDate\\n        stopDate\\n        links\\n        error\\n        friendlyName\\n        "
                   "metadata\\n       }\\n}\",\"variables\":{}}") % simulation_id

        headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", api_url, headers=headers, data=payload)

        result = response.json()

        return result['data']['simulationGet']['links']
    except Exception as e:
        print("An exception occurred: %s" % repr(e))


def fetch_parameters(simulation_id, api_key='', api_url="https://data.ptn.cobrabreiz.services/graphql"):
    try:
        list_files = fetch_list_files(simulation_id, api_key, api_url)

        time_resul_link = list_files['parameters.json']

        response_file = requests.request("GET", time_resul_link)

        return response_file.json()
    except Exception as e:
        print("An exception occurred: %s" % repr(e))


def convert_to_singletimeseries(timestamps, values, target='mean', sampling=1):
    from pyquantlib import metrics

    _timestamps = []
    _values = []

    for index, time in enumerate(timestamps['time']):
        current_date = datetime.datetime.fromtimestamp(time, datetime.timezone.utc)

        _timestamps.append(current_date)
        _values.append(values[target][index])

    return metrics.SingleTimeseries.from_components(_timestamps, _values).resample(datetime.timedelta(days=sampling))


def convert_from_singletimeseries(singletimeseries, target='mean'):
    _timestamps = singletimeseries.timestamps()
    _values = singletimeseries.values()

    rows = []
    for index, date in enumerate(_timestamps):
        dict = {}
        dict['date'] = date.isoformat().replace('+00:00', 'Z')
        dict[target] = _values[index]

        rows.append(dict)

    return rows
