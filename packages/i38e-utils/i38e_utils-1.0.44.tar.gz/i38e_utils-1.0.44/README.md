## i38e-utils

i38e-utils is a collection of utility functions and classes that I use in my BI projects. 
It is a work in progress and will be updated as I add more functionality.

The utilities are designed to work with Django, OpenStreetMaps and NetworkX

Currently, it includes the following:

1. DfHelper: A class designed to facilitate data handling and operations within a Django project, particularly focusing on loading data from both parquet files and a database, and potentially saving data to parquet format.
2. GeoLocationService: A class that provides a set of utility functions for working with GeoPy and Nominatim.
3. OsmxHelper: A class that provides a set of utility functions for working with Osmnx maps.
4. data_utils: A set of utility functions/classes for working with data.
5. date_utils: A set of utility functions for working with dates.
6. df_utils: A set of utility functions for working with pandas DataFrames.
7. file_utils: A set of utility functions for working with files.
8. log_utils: A set of utility functions for working with logs.

## Installation

To install this project, follow these steps:

```bash
pip install i38e-utils
```

## Usage
# DfHelper: Dataframe Helper Class

DfHelper is designed to be subclassed.  For example, the following use case, connects to a table containing gps transactions
and encapsulates data cleaning operations.  The resulting object can be queried via the "load" method using Django's query 
language syntax. The object can also be instantiated in debug and verbose mode. 

The object returns Dataframe objects either as pandas (by default) or dask.  It is recommended to use dask for large datasets
which may benefit from dask parallelization architecture.
Scenarios:

- Connect to a database table using a Django's ORM connection, query, transform and convert the data to a pandas DataFrame.

```python
import pandas as pd
import numpy as np
from i38e_utils.df_helper import DfHelper

phone_mobile_gps_fields = {
    'id_tracking': 'id',
    'id_producto': 'product_id',
    'pk_empleado': 'associate_id',
    'latitud': 'latitude',
    'longitud': 'longitude',
    'fecha_hora_servidor': 'server_dt',
    'fecha_hora': 'date_time',
    'accion': 'action',
    'descripcion': 'description',
    'imei': 'imei'
}


class GpsCube(DfHelper):
    df: pd.DataFrame = None
    live: bool = False
    save_parquet = True
    
    config={
        'connection_name': 'replica',
        'table': 'asm_tracking_movil_gps',
        'field_map': phone_mobile_gps_fields,
        'legacy_filters': True,
    }

    def __init__(self, **opts):
        config = {**self.config, **opts}
        super().__init__(**config)
        
    def load(self, **kwargs):
        self.df = super().load(**kwargs)
        self.fix_data()
        return self.df

    def fix_data(self):
        self.df['latitude'] = self.df['latitude'].astype(np.float64)
        self.df['longitude'] = self.df['longitude'].astype(np.float64)```python

gps_cube=GpsCube(live=True, debug=False,df_as_dask=True)
df=gps_cube.load(date_time__date='2023-03-04').compute()
# to save to a parquet file
gps_cube.save_to_parquet(df, parquet_full_path='gpscube.parquet')
```

- Use a parquet storage file or folder structure to load data and perform some transformations.

```python
import pandas as pd
from i38e_utils.df_helper import DfHelper

class GpsParquetCube(DfHelper):
    df: pd.DataFrame = None
    
    config={
        'use_parquet': True,
        'df_as_dask': True,
        'parquet_storage_path': '/storage/data/parquet/gps',
        'parquet_start_date': '2024-01-01',
        'parquet_end_date': '2024-03-31',
    }

    def __init__(self, **opts):
        config = {**self.config, **opts}
        super().__init__(**config)
        
    def load(self, **kwargs):
        self.df = super().load(**kwargs)
        return self.df


# The following example would load all the parquet files in the folder structure described in parquet_storage_path matching the date range and return a single dask dataframe for associate_id 27 for the month of March.
# The class converts Django style filters to dask compatible filters.
# The class also converts the parquet files to a dask dataframe for faster processing.

params = {
    'associate_id': 27,
    'date_time__date__range': ['2024-03-01','2024-03-31']
}

dask_df = GpsParquetCube().load(**params)
# to convert to a pandas dataframe
df = dask_df.compute()

```

# Usage
# osmnx_helper: Base Map and Utilities
# Use case: Create a heat map with time using a DfHelper cube with gps data
```python
from i38e_utils.osmnx_helper import BaseOsmMap
from i38e_utils.osmnx_helper.utils import get_graph
import folium

options = {
    'ox_files_save_path': 'path/to/pbf/files',
    'network_type': 'all',
    'place': 'Costa Rica',
    'files_prefix': 'costa-rica-',
    'rebuild': False,
    'verbose': False
}

class ActivityHeatMapWithTime(BaseOsmMap):
    def __init__(self, df, **kwargs):
        kwargs.setdefault('dt_field', 'date_time')
        G, _, _ = get_graph(**options)
        self.heat_time_index = []
        super().__init__(G, df, **kwargs)

    def process_map(self):
        self.heat_time_index = sorted(list(self.df[self.dt_field].dt.hour.unique()))
        heat_data_time = [[[row[self.lat_col], row[self.lon_col]] for index, row in
                           self.df[self.df[self.dt_field].apply(lambda x: x.hour == j)].iterrows()] for j in self.heat_time_index]

        hm = folium.plugins.HeatMapWithTime(heat_data_time, index=self.heat_time_index)
        # hm = HeatMap(gps_points)
        hm.add_to(self.osm_map)
```
to create a heatmap using a Dataframe of GPS Data

```python

df=GpsCube().load(date_time__date="2024-06-30")
map_options={}
map_options.setdefault("map_html_title","Activity Heatmap")
map_options.setdefault("dt_field", "date_time")
map_options.setdefault("max_bounds", False)
heat_map=ActivityHeatMapWithTime(df, **map_options)
heat_map.generate_map()

```
