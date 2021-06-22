# -*- coding: utf-8 -*-
"""
Created on Tue Jun 22 18:57:14 2021
Script to load data from / postgres or sqlite3 data to BigQuery
@author: L7
"""

import pandas as pd
import json
import os
from google.cloud import bigquery
import sqlite3
import psycopg2

key = r"C:\Users\WELCOME\Downloads\algo-trading-311005-a5cb9c86cf98.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key

gcp_project = 'algo-trading-311005'
dataset = 'fcdb'
table_ref = 'nifty_equity'

client = bigquery.Client(project=gcp_project)
# ds = client.dataset(dataset)

pg_conn = psycopg2.connect(database="fcdb", user="postgres", password="postgres", host="127.0.0.1", port="5432")
pg_cur = pg_conn.cursor()
query = ''' select * from public.nifty_equity'''
pg_cur.execute(query)
pg_rows = pg_cur.fetchall()
## df for options/futures
# df = pd.DataFrame(pg_rows, columns=(['name','datetime', 'open', 'high', 'low', 'close', 'volume', 'oi']))
# df = df.astype(dtype={'name': str, 'datetime':'datetime64[ns]', 'open': float, 'high': float,  \
#                                  'low': float, 'close': float, 'volume': int, 'oi': int})

# job_config = bigquery.LoadJobConfig(
#     schema=[
#         bigquery.SchemaField("name", bigquery.enums.SqlTypeNames.STRING),
#         bigquery.SchemaField("datetime", bigquery.enums.SqlTypeNames.DATETIME),
#         bigquery.SchemaField("open", bigquery.enums.SqlTypeNames.FLOAT64),
#         bigquery.SchemaField("high", bigquery.enums.SqlTypeNames.FLOAT64),
#         bigquery.SchemaField("low", bigquery.enums.SqlTypeNames.FLOAT64),
#         bigquery.SchemaField("close", bigquery.enums.SqlTypeNames.FLOAT64),
#         bigquery.SchemaField("volume", bigquery.enums.SqlTypeNames.INT64),
#         bigquery.SchemaField("oi", bigquery.enums.SqlTypeNames.INT64)
#     ], write_disposition="WRITE_APPEND", 
#     source_format=bigquery.SourceFormat.CSV
# )    
    
# df for equity  
df = pd.DataFrame(pg_rows, columns=(['name','symbol','datetime', 'open', 
                                     'high', 'low', 'close', 'volume']))
df = df.astype(dtype={'name': str, 'symbol': int , 'datetime':'datetime64[ns]', 'open': float, 'high': float,  \
                                 'low': float, 'close': float, 'volume': int})


job_config = bigquery.LoadJobConfig(
    schema=[
        bigquery.SchemaField("name", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("symbol", bigquery.enums.SqlTypeNames.INT64),
        bigquery.SchemaField("datetime", bigquery.enums.SqlTypeNames.DATETIME),
        bigquery.SchemaField("open", bigquery.enums.SqlTypeNames.FLOAT64),
        bigquery.SchemaField("high", bigquery.enums.SqlTypeNames.FLOAT64),
        bigquery.SchemaField("low", bigquery.enums.SqlTypeNames.FLOAT64),
        bigquery.SchemaField("close", bigquery.enums.SqlTypeNames.FLOAT64),
        bigquery.SchemaField("volume", bigquery.enums.SqlTypeNames.INT64)
    ], write_disposition="WRITE_APPEND", 
    source_format=bigquery.SourceFormat.CSV
)

table_id = f'{gcp_project}.{dataset}.{table_ref}'

job = client.load_table_from_dataframe(
    df, table_id, job_config=job_config
)  # Make an API request.
# job = client.load_table_from_dataframe(df, table_id)
job.result()  # Wait for the job to complete.

table = client.get_table(table_id)  # Make an API request.
print(
    "Loaded {} rows and {} columns to {}".format(
        table.num_rows, len(table.schema), table_id
    )
)