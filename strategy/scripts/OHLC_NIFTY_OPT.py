# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 01:58:19 2021
OHLC_FUT
@author: lmahendran
"""
from datetime import datetime
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
    os.chdir(r'D:\Python\First_Choice_Git\xts\strategy\test_scripts')
except:
    pass

from utils.utils import xts_init, configure_logging


# this is referring the main script logger
log_name = os.path.basename(__file__).split('.')[0]
# print(log_name)
logger = configure_logging(log_name)

xt = xts_init(market=True)
from dateutil.relativedelta import relativedelta, TH, WE

def get_index(idx):
    try:
        nifty_ohlc = {}
        instruments = [{'exchangeSegment': 1, 'exchangeInstrumentID': 'NIFTY 50'}]
        q_resp = xt.get_quote(
        Instruments=instruments,
        xtsMessageCode=1504,
        publishFormat='JSON')
        # print('Quote :', response)
        listQuotes = json.loads(q_resp['result']['listQuotes'][0])
        for k,v in listQuotes.items():
            if 'Index' in k:
                nifty_ohlc[k] = v
    except Exception as e:
        logger.exception(f'Error in getting NIFTY OHLC: {e}')
        return
    return nifty_ohlc


def strike_prc_calc(spot,base):
    return base * round(spot/base)
    

if __name__ == '__main__':
    weekly_exp,monthly_exp = xt.get_expiry()
    cur_date = datetime.strftime(datetime.now(), "%b %d %Y")
    cur_week = (datetime.strptime(weekly_exp, '%d%b%Y').strftime('%#m%d'))
    #next_week = ((datetime.strptime(weekly_exp, '%d%b%Y') + relativedelta(weeks=+1))).strftime('%#m%d')
    cur_month = (datetime.strptime(monthly_exp,'%d%b%Y')
                     .strftime('%b').upper())
    next_month = (datetime.strptime(monthly_exp,'%d%b%Y') + 
                  relativedelta(months=+1)).strftime('%b').upper()
    df = xt.master_fo_dump()
    
    cur_month_filter = df[(df.Name == 'NIFTY') & \
                        (df.Description.str.contains(f'NIFTY21{cur_month}'))]
    next_month_filter = df[(df.Name == 'NIFTY') & \
                         (df.Description.str.contains(f'NIFTY21{next_month}'))]
    cur_week_filter = df[(df.Name == 'NIFTY') & \
                       (df.Description.str.contains(f"NIFTY21{cur_week.month}"))]
    # next_week_filter = df[(df.Name == 'NIFTY') & \
    #                    (df.Description.str.contains(f"NIFTY21{cur_week}"))]
    total_df = pd.concat([cur_month_filter, next_month_filter, cur_week_filter], ignore_index=True)
    
    nifty_ohlc = get_index('NIFTY 50')
    nifty_spot = nifty_ohlc['IndexValue']
    nifty_h = nifty_ohlc['HighIndexValue']
    nifty_l = nifty_ohlc['LowIndexValue']
    # strikeRange = [str(i) for i in list(range(strikePrice-1000,strikePrice+1000,50))]
    new_strike_range = [str(i) for i in 
                    list(range(strike_prc_calc(nifty_l, 50) - 500,
                               strike_prc_calc(nifty_h, 50) + 500
                               ,50))]
    # strike_range_file = open(
    #                     "strike_range_file.txt",mode="r+",encoding="utf-8")
    
    new_strike_range = [11,22,33,44,55]
    #new_strike_range = [55,66,77,88,22]
    f = open("../ohlc/strike_range_file.txt",'w+')
    old_strike_range = f.read()
    print('lines: ',old_strike_range,'end')
    #new_strike_range.append(strike) for strike in old_strike_range if strike not in new_strike_range 
    strike_range = list((old_strike_range.split(',')) if old_strike_range != '' else old_strike_range)
    strike_range.extend(str(x) for x in new_strike_range if str(x) not in strike_range)
    with open("../ohlc/strike_range_file.txt",'w') as f:
        f.write(','.join(strike_range))

    

