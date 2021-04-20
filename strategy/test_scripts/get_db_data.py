# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 17:08:21 2021
utils for getting data from db sqlite3
@author: WELCOME
"""
from datetime import datetime
import pandas as pd
import sqlite3

def get_db_data(ticker, date_str):
    # month = month.upper()
    # date_str = '2019-4-7'
    date = datetime.strptime(date_str, "%Y-%m-%d")
    try:    
        db = sqlite3.connect(f'../ohlc/EQ_{date.strftime("%B")[0:3].upper()}_OHLC.db')
        # print(f'../ohlc/EQ_{date.strftime("%B")[0:3].upper()}_OHLC.db')
        cur = db.cursor()
        # df = pd.read_sql_query(f"SELECT * from {ticker}", db)
        # df = cur.execute(f"SELECT * FROM {ticker}").fetchall()
        # df = pd.read_sql_query(f"SELECT name FROM sqlite_master WHERE type='table'", db)
        data_list = cur.execute(f"SELECT * FROM {ticker} \
                                WHERE date(Timestamp) = \
                                date('2021-{date.month:02d}-{date.day:02d}');")\
                                    .fetchall()
        if data_list:
            data_df = pd.DataFrame(data_list,columns=['timestamp','open','high','low','close','volume'])
            data_df['timestamp'] = pd.to_datetime(data_df['timestamp'])
            data_df = data_df.astype(dtype={'open': float, 'high': float, 
                                            'low': float, 'close': float, 
                                            'volume': int})
            return data_df
        else:
            print('No data available')
            return
    except Exception as e:
        print(e)
        print('issue in reading .db file')
    finally:
        cur.close()
        db.close()  
        
# df = get_db_data('ZEEL','2021-04-20')
