# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 19:25:24 2021

@author: WELCOME
"""

from datetime import datetime
import time
import json
import pandas as pd
pd.set_option('display.max_rows', None)
import os
import sqlite3
import psycopg2
import psycopg2.extras
import re
import numpy as np


try:
    os.chdir(r'D:\Python\First_Choice_Git\xts\strategy\live')
except:
    pass


#to load nifty, bankNifty and futures:
dbfile='D:\\Python\\First_Choice_Git\\xts\\strategy\\ohlc\\Archive\\BANKNIFTY_AUG_OHLC.db'
sql_db = sqlite3.connect(dbfile)
sql_cur = sql_db.cursor()
sql_cur.execute("SELECT * FROM BANKNIFTY_AUGUST;")
rows=sql_cur.fetchall()
# pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';",sql_db)
df = pd.DataFrame(rows, columns=(['instrument_name','datetime', 'open', 'high', 'low', 'close', 'volume', 'oi']))
# df_columns = list(df)

pattern3= r'(?P<index>NIFTY|BANKNIFTY)(?P<year>\d{2})(?P<month>(0?[1-9]|1[0-2]))(?P<date>(0?[1-9]|[12]\d|30|31))(?P<strike>\d{5})(?P<otype>CE|PE)$'
pattern4 = r'(?P<index>NIFTY|BANKNIFTY)(?P<year>\d{2})(?P<month>JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)(?P<strike>\d{4,5})(?P<otype>CE|PE)$'


def get_strike(name):
    if re.search(pattern3, name):
        mm = re.search(pattern3, name)
        # print('Weekly Expiry - ', 'date', mm.group('date'),'month', mm.group('month') , 'year', mm.group('year'), 'strike', mm.group('strike'))
        strike = mm.group('strike')
    elif re.search(pattern4, name):
        mm = re.search(pattern4, name)
        # print('4 ',idx[i], 'strike', re.search(pattern4, idx[i]).group('strike'))
        # print('Monthly Expiry - ', 'month', mm.group('month') , 'year', mm.group('year'), 'strike', mm.group('strike'))
        strike = mm.group('strike')
    else:
        strike = None
    return strike


def get_expiry_nft(name):
    if name.startswith('NIFTY21MAR'):
        return pd.to_datetime('2021-03-25').replace(microsecond=0)
    elif name.startswith('NIFTY21APR'):
        return pd.to_datetime('2021-04-29').replace(microsecond=0)
    elif name.startswith('NIFTY21MAY'):
        return pd.to_datetime('2021-05-27').replace(microsecond=0)
    elif name.startswith('NIFTY21JUN'):
        return pd.to_datetime('2021-06-24').replace(microsecond=0)
    elif name.startswith('NIFTY21JUL'):
        return pd.to_datetime('2021-07-29').replace(microsecond=0)
    elif name.startswith('NIFTY21AUG'):
        return pd.to_datetime('2021-08-26').replace(microsecond=0)
    elif name.startswith('NIFTY21SEP'):
        return pd.to_datetime('2021-09-24').replace(microsecond=0)
    elif name.startswith('NIFTY21408'):
        return pd.to_datetime('2021-04-08').replace(microsecond=0)
    elif name.startswith('NIFTY21415'):
        return pd.to_datetime('2021-04-15').replace(microsecond=0)
    elif name.startswith('NIFTY21422'):
        return pd.to_datetime('2021-04-22').replace(microsecond=0)
    elif name.startswith('NIFTY21506'):
        return pd.to_datetime('2021-05-06').replace(microsecond=0)
    elif name.startswith('NIFTY21512'):
        return pd.to_datetime('2021-05-12').replace(microsecond=0)
    elif name.startswith('NIFTY21520'):
        return pd.to_datetime('2021-06-20').replace(microsecond=0)
    elif name.startswith('NIFTY21603'):
        return pd.to_datetime('2021-06-03').replace(microsecond=0)
    elif name.startswith('NIFTY21610'):
        return pd.to_datetime('2021-06-10').replace(microsecond=0)
    elif name.startswith('NIFTY21617'):
        return pd.to_datetime('2021-06-17').replace(microsecond=0)
    elif name.startswith('NIFTY21722'):
        return pd.to_datetime('2021-07-22').replace(microsecond=0)
    elif name.startswith('NIFTY21715'):
        return pd.to_datetime('2021-07-15').replace(microsecond=0)
    elif name.startswith('NIFTY21701'):
        return pd.to_datetime('2021-07-01').replace(microsecond=0)
    elif name.startswith('NIFTY21708'):
        return pd.to_datetime('2021-07-08').replace(microsecond=0)
    elif name.startswith('NIFTY21805'):
        return pd.to_datetime('2021-08-05').replace(microsecond=0)
    elif name.startswith('NIFTY21812'):
        return pd.to_datetime('2021-08-12').replace(microsecond=0)
    elif name.startswith('NIFTY21818'):
        return pd.to_datetime('2021-08-18').replace(microsecond=0)

def get_expiry_bnft(name):
    if name.startswith('BANKNIFTY21MAR'):
        return pd.to_datetime('2021-03-25').replace(microsecond=0)
    elif name.startswith('BANKNIFTY21APR'):
        return pd.to_datetime('2021-04-29').replace(microsecond=0)
    elif name.startswith('BANKNIFTY21MAY'):
        return pd.to_datetime('2021-05-27').replace(microsecond=0)
    elif name.startswith('BANKNIFTY21JUN'):
        return pd.to_datetime('2021-06-24').replace(microsecond=0)
    elif name.startswith('BANKNIFTY21JUL'):
        return pd.to_datetime('2021-07-29').replace(microsecond=0)
    elif name.startswith('BANKNIFTY21AUG'):
        return pd.to_datetime('2021-08-26').replace(microsecond=0)
    elif name.startswith('BANKNIFTY21SEP'):
        return pd.to_datetime('2021-09-24').replace(microsecond=0)
    elif name.startswith('BANKNIFTY21408'):
        return pd.to_datetime('2021-04-08').replace(microsecond=0)
    elif name.startswith('BANKNIFTY21415'):
        return pd.to_datetime('2021-04-15').replace(microsecond=0)
    elif name.startswith('BANKNIFTY21422'):
        return pd.to_datetime('2021-04-22').replace(microsecond=0)
    elif name.startswith('BANKNIFTY21506'):
        return pd.to_datetime('2021-05-06').replace(microsecond=0)
    elif name.startswith('BANKNIFTY21512'):
        return pd.to_datetime('2021-05-12').replace(microsecond=0)
    elif name.startswith('BANKNIFTY21520'):
        return pd.to_datetime('2021-06-20').replace(microsecond=0)
    elif name.startswith('BANKNIFTY21603'):
        return pd.to_datetime('2021-06-03').replace(microsecond=0)
    elif name.startswith('BANKNIFTY21610'):
        return pd.to_datetime('2021-06-10').replace(microsecond=0)
    elif name.startswith('BANKNIFTY21617'):
        return pd.to_datetime('2021-06-17').replace(microsecond=0)
    elif name.startswith('BANKNIFTY21722'):
        return pd.to_datetime('2021-07-22').replace(microsecond=0)
    elif name.startswith('BANKNIFTY21715'):
        return pd.to_datetime('2021-07-15').replace(microsecond=0)
    elif name.startswith('BANKNIFTY21701'):
        return pd.to_datetime('2021-07-01').replace(microsecond=0)
    elif name.startswith('BANKNIFTY21708'):
        return pd.to_datetime('2021-07-08').replace(microsecond=0)
    elif name.startswith('BANKNIFTY21805'):
        return pd.to_datetime('2021-08-05').replace(microsecond=0)
    elif name.startswith('BANKNIFTY21812'):
        return pd.to_datetime('2021-08-12').replace(microsecond=0)
    elif name.startswith('BANKNIFTY21818'):
        return pd.to_datetime('2021-08-18').replace(microsecond=0)    
    

def get_exp_fut(name):
    if 'APR' in name:
        return pd.to_datetime('2021-04-29').replace(microsecond=0)
    elif 'MAY' in name:
        return pd.to_datetime('2021-05-27').replace(microsecond=0)
    elif 'JUN' in name:
        return pd.to_datetime('2021-06-24').replace(microsecond=0)
    elif 'JUL' in name:
        return pd.to_datetime('2021-07-29').replace(microsecond=0)
    elif 'AUG' in name:
        return pd.to_datetime('2021-08-26').replace(microsecond=0)
    elif 'SEP' in name:
        return pd.to_datetime('2021-09-24').replace(microsecond=0)
        
    
    
df["underlying"] = df.instrument_name.apply(lambda x: pd.Series(str(x).split("21")[0]))
df["instrument_type"] = 2
df['series'] = 'OPTIDX'
# df.insert(12, 'expiry', pd.to_datetime('2021-03-27').replace(microsecond=0))
df["expiry"] = df.apply(lambda row: get_expiry_bnft(str(row["instrument_name"])), axis =1)
df["strike_price"] = df.apply(lambda row: get_strike(str(row["instrument_name"])), axis =1)
df["option_type"] = df['instrument_name'].str[-2:]
# df = df.replace({np.NaN: None})
df_columns = list(df)

table = 'banknifty_options'
columns = ",".join(df_columns)
values = "VALUES({})".format(",".join(["%s" for _ in df_columns]))
insert_stmt = "INSERT INTO {} ({}) {}".format(table,columns,values)

# NIFTY_MARCH
pg_conn = psycopg2.connect(database="fcdb", user="postgres", password="postgres", host="127.0.0.1", port="5432")
pg_cur = pg_conn.cursor()
psycopg2.extras.execute_batch(pg_cur, insert_stmt, df.values)
pg_conn.commit()
pg_cur.close()
pg_conn.close()
sql_cur.close()
sql_db.close()

#to load eq

# dbfile='D:\\Python\\First_Choice_Git\\xts\\strategy\\ohlc\\Archive\\EQ_AUGUST_OHLC.db'
# sql_db = sqlite3.connect(dbfile)
# sql_cur = sql_db.cursor()

# sql_cur.execute('SELECT name FROM sqlite_master  WHERE type IN ("table","view") AND name NOT LIKE "sqlite_%" ORDER BY 1')
# table_names = sql_cur.fetchall()
# tables = []
# ticker_dict = {}
# for i in range(len(table_names)):
#     tables.append(table_names[i][0])
# pg_conn = psycopg2.connect(database="fcdb", user="postgres", password="postgres", host="127.0.0.1", port="5432")
# pg_cur = pg_conn.cursor()

# for ticker in tables:
#     sql_cur.execute(f"SELECT '{ticker}' as name,* FROM '{ticker}';")
#     rows=sql_cur.fetchall()
#     df = pd.DataFrame(rows, columns=(['instrument_name', 'datetime', 'open', 'high', 'low', 'close', 'volume']))
#     df_columns = list(df)
#     table = 'nifty_equity'
#     columns = ",".join(df_columns)
#     values = "VALUES({})".format(",".join(["%s" for _ in df_columns]))
#     insert_stmt = "INSERT INTO {} ({}) {}".format(table,columns,values)
#     psycopg2.extras.execute_batch(pg_cur, insert_stmt, df.values)








