# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 22:30:01 2021

@author: lmahendran
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import sqlite3
import time
import os
# from XTConnect import XTSConnect
# import configparser
# from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
import logging
import json

try:
    os.chdir(r'D:\Python\First_Choice_Git\xts\strategy\scripts')
except:
    pass

from utils.utils import xts_init, configure_logging


# this is referring the main script logger
log_name = os.path.basename(__file__).split('.')[0]
# print(log_name)
logger = configure_logging(log_name)

xt = xts_init(market=True)

if __name__ == '__main__':
    filtered_names = []
    weekly_exp, monthly_exp = xt.get_expiry()
    cur_date = datetime.strftime(datetime.now(), "%b %d %Y")
    df_dump = xt.master_fo_dump()
    df = df_dump[(df_dump.Series == 'FUTIDX') | (df_dump.Series == 'FUTSTK')]
    fut_names = df.Name.unique().tolist()
    cur_month = (datetime.strptime(monthly_exp,'%d%b%Y')
                     .strftime('%b').upper())
    next_month = (datetime.strptime(monthly_exp,'%d%b%Y') +
                  relativedelta(months=+1)).strftime('%b').upper()
    for name in fut_names:
        filtered_names.append(name+'21'+cur_month+'FUT')
        filtered_names.append(name+'21'+next_month+'FUT')
        
    filtered_df = df[df.Description.isin(filtered_names)]
    keyv = dict(zip(filtered_df.Description,
                    filtered_df.ExchangeInstrumentID))
    skipped = []
    db = sqlite3.connect(f'../ohlc/FUT_{cur_month}_OHLC.db')
    cur = db.cursor()
    for name,symbol in keyv.items():
        try:
            logger.info(f'Saving OHLC for - {name} - {symbol}')
            ohlc = xt.get_ohlc(
                    exchangeSegment=xt.EXCHANGE_NSEFO,
                    exchangeInstrumentID=symbol,
                    startTime=cur_date+' 091500',
                    endTime=cur_date+' 153000',
                    compressionValue=60)
                    # print("OHLC: " + str(ohlc))
            dataresp= ohlc['result']['dataReponse']
            if dataresp != '':
                spl = dataresp.split(',')
                datadf = pd.DataFrame([sub.split("|") for sub in spl],columns=(['Timestamp','Open','High','Low','Close','Volume','OI','NA']))
                datadf.drop(datadf.columns[[-1,]], axis=1, inplace=True)
                datadf['Timestamp'] = pd.to_datetime(datadf['Timestamp'].astype('int'), unit='s')
                datadf.insert(0, 'Name', name)
                datadf.to_sql((f'FUT_{cur_month}_2021'),db,if_exists='append',index=False)
                # pd.read_sql_query("SELECT * from FUT_APR_2021 where Name='TCS21MAYFUT'", db)
                time.sleep(1)
        except ConnectionError:
            skipped.append({name:symbol})
            pass
    logger.warning(f'OHLC data import failed for : {skipped}')
    cur.close()
    db.close()
    logger.info('==================END========================')
        
    