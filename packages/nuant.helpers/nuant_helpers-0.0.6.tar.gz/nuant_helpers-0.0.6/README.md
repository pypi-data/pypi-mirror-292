<div align="center">
  <img src="https://cdn.prod.website-files.com/6645c2bf1d8a88dfb078b41d/6645d629b58f71cda23ae53e_Logotype-Nuant.svg" alt="Logo">
  <h1>Nuant Helpers</h1>
</div>

# Introduction

This python library can help you manipulate Nuant data more easily.
This module is automatically available on your Nuant development environment (IDE / Dashboard).

# Helpers

List of all helpers available

## Simulation

### fetch_list_files

List all files available as result for this simulation

```python
from nuant.helpers import simulation

all_files = simulation.fetch_list_files("YOUR_SIMULATION_ID", api_key="YOUR_API_KEY")
```

### fetch_data

Fetch a result of the simulation with the timeseries preformatted with the merge of time and values files.

```python
from nuant.helpers import simulation

data = simulation.fetch_data("YOUR_SIMULATION_ID", "DATA_FILE_NAME", api_key="YOUR_API_KEY")
```

### fetch_parameters

Fetch parameters file of the simulation

```python
from nuant.helpers import simulation

parameters = simulation.fetch_parameters("YOUR_SIMULATION_ID", api_key="YOUR_API_KEY")
```

### convert_to_singletimeseries

Convert raw data from the simulator to Nuant Quantlib's SingleTimeseries

```python
from nuant.helpers import simulation

# Examples values but you probably want to pass simulator's data
timestamps = { 'time': [1724139765] }
values = { 'mean': [1] }

parameters = simulation.convert_to_singletimeseries(timestamps, values, target='mean')
```

### convert_from_singletimeseries

Convert Nuant Quantlib's SingleTimeseries to array of dict for the dashboard visualisation

```python
from nuant.helpers import simulation

my_rows = simulation.convert_from_singletimeseries(singletimeseries, target='mean')
```
