# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 01:58:19 2021
OHLC_OPT for BankNifty 1min candle
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


def get_index(idx):
    try:
        nifty_ohlc = {}
        instruments = [{'exchangeSegment': 1, 'exchangeInstrumentID': idx}]
        q_resp = xt.get_quote(
            Instruments=instruments,
            xtsMessageCode=1504,
            publishFormat='JSON')
        # print('Quote :', response)
        listQuotes = json.loads(q_resp['result']['listQuotes'][0])
        for k, v in listQuotes.items():
            if 'Index' in k:
                nifty_ohlc[k] = v
    except Exception as e:
        logger.exception(f'Error in getting NIFTY OHLC: {e}')
        return
    return nifty_ohlc


def strike_prc_calc(spot, base):
    return base * round(spot / base)


if __name__ == '__main__':
    weekly_exp, monthly_exp = xt.get_expiry()
    cur_date = datetime.strftime(datetime.now(), "%b %d %Y")
    # cur_week = (datetime.strptime(weekly_exp, '%d%b%Y').strftime('%#m%d'))
    cur_week = (datetime.strptime(weekly_exp, '%d%b%Y'))
    # next_week = ((datetime.strptime(weekly_exp, '%d%b%Y') + relativedelta(weeks=+1))).strftime('%#m%d')
    cur_month = (datetime.strptime(monthly_exp, '%d%b%Y')
                 .strftime('%b').upper())
    next_month = (datetime.strptime(monthly_exp, '%d%b%Y') +
                  relativedelta(months=+1)).strftime('%b').upper()
    df_dump = xt.master_fo_dump()
    df = df_dump[df_dump.Series == 'OPTIDX']
    cur_month_filter = df[(df.Name == 'BANKNIFTY') &
                          (df.Description.str.contains(f'BANKNIFTY21{cur_month}'))]
    next_month_filter = df[(df.Name == 'BANKNIFTY') &
                           (df.Description.str.contains(f'BANKNIFTY21{next_month}'))]
    cur_week_filter = df[(df.Name == 'BANKNIFTY') &
                         (df.Description.str.contains(f"BANKNIFTY21{cur_week.month}"))]
    # next_week_filter = df[(df.Name == 'NIFTY') & \
    #                    (df.Description.str.contains(f"NIFTY21{cur_week}"))]
    expiry_filter = pd.concat(
        [cur_month_filter, next_month_filter, cur_week_filter], ignore_index=True)

    banknifty_ohlc = get_index('NIFTY BANK')
    banknifty_spot = banknifty_ohlc['IndexValue']
    banknifty_h = banknifty_ohlc['HighIndexValue']
    banknifty_l = banknifty_ohlc['LowIndexValue']
    # strikeRange = [str(i) for i in list(range(strikePrice-1000,strikePrice+1000,50))]
    new_strike_range = [str(i) for i in
                        list(range(strike_prc_calc(banknifty_l, 100) - 1000,
                                   strike_prc_calc(banknifty_h, 100) + 1000, 100))]
    #new_strike_range = [11,22,33,44,55]
    strike_range_file = f'../ohlc/banknifty_strike_range_file_{cur_month}.txt'
    if not os.path.exists(strike_range_file):
        with open(strike_range_file, 'w'):
            pass
    f = open(strike_range_file, 'r')
    old_strike_range = f.read()
    #print('lines: ',old_strike_range,'end')
    f.close()
    # new_strike_range.append(strike) for strike in old_strike_range if strike not in new_strike_range
    strike_range = list((old_strike_range.split(','))
                        if old_strike_range != '' else old_strike_range)
    strike_range.extend(str(x)
                        for x in new_strike_range if str(x) not in strike_range)
    with open(strike_range_file, 'w') as f:
        f.write(','.join(strike_range))

    strike_range_filter = expiry_filter[expiry_filter.Description.str.contains(
        '|'.join(strike_range))]
    keyv = dict(zip(strike_range_filter.Description,
                    strike_range_filter.ExchangeInstrumentID))
    skipped = []
    logger.info(f'old strike range : {old_strike_range}')
    logger.info(f'new strike range : {new_strike_range}')
    logger.info(f'strike range for today calulated as : {strike_range}')
    db = sqlite3.connect(f'../ohlc/BANKNIFTY_{cur_month}_OHLC.db')
    cur = db.cursor()
    for name, symbol in keyv.items():
        try:
            logger.info(f'Saving OHLC for - {name} - {symbol}')
            ohlc = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=symbol,
                startTime=cur_date + ' 091500',
                endTime=cur_date + ' 153000',
                compressionValue=60)
            # print("OHLC: " + str(ohlc))
            dataresp = ohlc['result']['dataReponse']
            if dataresp != '':
                spl = dataresp.split(',')
                datadf = pd.DataFrame([sub.split("|") for sub in spl], columns=(
                    ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'OI', 'NA']))
                datadf.drop(datadf.columns[[-1, ]], axis=1, inplace=True)
                datadf['Timestamp'] = pd.to_datetime(
                    datadf['Timestamp'].astype('int'), unit='s')
                datadf.insert(0, 'Name', name)
                datadf.to_sql(
                    (f'BANKNIFTY_{datetime.now().strftime("%B").upper()}'), db, if_exists='append', index=False)
                # pd.read_sql_query("SELECT * from BANKNIFTY_MARCH", db)
                time.sleep(1)
        except ConnectionError:
            skipped.append({name: symbol})
            pass
    logger.warning(f'OHLC data import failed for : {skipped}')
    cur.close()
    db.close()
    logger.info('==================END========================')
