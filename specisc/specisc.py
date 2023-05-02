"""Main module."""

import cdsapi
import yaml
import os

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

c = cdsapi.Client(url=os.getenv("ADSAPIURL"), key=os.getenv("ADSCREDS"))

latitude = 52.52
longitude = 13.4

# c.retrieve(
#     'cams-solar-radiation-timeseries',
#     {
#         'sky_type': 'observed_cloud',
#         'location': {
#             'latitude': 52.52,
#             'longitude': 13.4,
#         },
#         'altitude': '-999.',
#         'date': '2023-01-01/2023-01-02',
#         'time_step': '1minute',
#         'time_reference': 'universal_time',
#         'format': 'csv_expert',
#     },
#     'test.csv')

start_date = pd.to_datetime('2020-01-01')
end_date = pd.to_datetime('2020-12-31')

# Generate a DatetimeIndex with the first day of every month
first_days = pd.date_range(start_date, end_date, freq='MS')

# Generate a DatetimeIndex with the last day of every month
last_days = pd.date_range(start_date, end_date, freq='M')

# Combine the first and last days into a DataFrame
month_starts_ends = pd.DataFrame({'start_date': first_days, 'end_date': last_days})

pqwriter = None

for i, month in month_starts_ends.iterrows():
    print(month)
    c.retrieve(
        'cams-solar-radiation-timeseries',
        {
            'sky_type': 'observed_cloud',
            'location': {
                'latitude': 52.52,
                'longitude': 13.4,
            },
            'altitude': '-999.',
            'date': f'{month.start_date.strftime("%Y-%m-%d")}/{month.start_date.strftime("%Y-%m-%d")}',
            'time_step': '1minute',
            'time_reference': 'universal_time',
            'format': 'csv_expert',
        },
        'cams_tmp.csv')
    
    df_tmp = pd.read_csv("cams_tmp.csv", sep=';', skiprows=67)
    df_tmp.columns = ['Observation period', 'TOA', 'Clear sky GHI', 'Clear sky BHI',
           'Clear sky DHI', 'Clear sky BNI', 'GHI', 'BHI', 'DHI', 'BNI',
           'Reliability', 'sza', 'summer/winter split', 'tco3', 'tcwv', 'AOD BC',
           'AOD DU', 'AOD SS', 'AOD OR', 'AOD SU', 'AOD NI', 'AOD AM', 'alpha',
           'Snow probability', 'fiso', 'fvol', 'fgeo', 'albedo',
           'Cloud optical depth', 'Cloud coverage', 'Cloud type', 'GHI no corr',
           'BHI no corr', 'DHI no corr', 'BNI no corr']
    
    df_tmp.index = pd.to_datetime(df_tmp['Observation period'].str.slice(0,21), format="%Y-%m-%dT%H:%M:%S.%f")
    df_tmp.drop("Observation period", axis=1, inplace=True)
    
    df_tmp.resample("15min").mean()
    
    table = pa.Table.from_pandas(df_tmp)
    # for the first chunk of records
    if i == 0:
        # create a parquet write object giving it an output file
        pqwriter = pq.ParquetWriter('sample.parquet', table.schema)            
    pqwriter.write_table(table)
    
 
# close the parquet writer
if pqwriter:
    pqwriter.close()

