# -*- coding: utf-8 -*-
"""
BFO Dynamite BOOST  ( Very Good like NFO Panther)

SET 1 : Sell ATM CE  & PE in BN @ 9.30 am
If BN moves +/- 0.75% of its latest entry price, exit current both legs & SELL latest ATM CE & PE ( repair continous)
It means for +/- 0.75% it keeps abv action till 2.45 pm

Example at 930 am BN spot = 35000 ( Latest BN entry price in SET 1)
SELL 35000 ce & 35000 PE
if BN spot moves +/- 0.75%  ( ie 35000 x .1.0075  or  35000 x 0.9925 ), exit both legs
add SELL latest SPOT ATM CE  & PE
for example : if BN moves +0.755 ..........latest BN spot entry = 35000 x 1.0075.....   35262
Exit old legs & SELL 35300 CE & PE
if again BN moves +/- 0.75% from latest BN spot entry price ( 35262), do repeat  process
SET 2 : SAME entry time 1000 am
SET 3 : SAME entry time 1030 am
SET 4 : SAME entry time 1100 am
SET 5 : SAME entry time 1330 am
Global SL : Rs. 8000
TGT     16000
@author: lmahendran
"""

import os
import time
import json
import logging
import configparser
import pandas as pd
from sys import exit
from pathlib import Path
from threading import Thread
from datetime import datetime
from pprint import pformat as pp
from openpyxl import load_workbook
from logging.handlers import TimedRotatingFileHandler

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
os.chdir(r'D:\Python\First_Choice_Git\xts\strategy\live')

from utils.utils import xts_init, configure_logging, RepeatedTimer, data_to_excel

# logger settings
script_name = os.path.basename(__file__).split('.')[0]
logger = configure_logging(script_name)

# inits
xt = xts_init(interactive=True)
if not xt:
    logger.exception('XT initialization failed. Exiting..')
    exit()

df = None
gdf = None
gl_pnl = None
etr_inst = None
rpr_inst = None
ext_inst = None
tr_insts = None
data_df = None
cdate = xt.CDATE
spot = 'BANKNIFTY'
ltp = {}
pnl_dump = []
threads = []


# orders = [{'legpair': 1, 'setno': 1, 'ent_txn_type': "sell", 'rpr_txn_type': "buy",
#            'idx': "BANKNIFTY", 'otype': "ce", 'status': "Idle", 'expiry': 'week', 'lot': 1, 'startTime': "09:30:00" },
#           {'legpair': 1, 'setno': 2, 'ent_txn_type': "sell", 'rpr_txn_type': "buy",
#            'idx': "BANKNIFTY", 'otype': "pe", 'status': "Idle", 'expiry': 'week', 'lot': 1, 'startTime': "09:30:00"}]

orders = [{'legpair': 1, 'setno': 1, 'ent_txn_type': "sell", 'rpr_txn_type': "buy",
           'idx': "BANKNIFTY", 'otype': ["ce", "pe"], 'status': "Idle", 'expiry': 'week', 'lot': 1, 'startTime': "09:30:00"},
          {'legpair': 2, 'setno': 2, 'ent_txn_type': "sell", 'rpr_txn_type': "buy",
           'idx': "BANKNIFTY", 'otype': ["ce", "pe"], 'status': "Idle", 'expiry': 'week', 'lot': 1, 'startTime': "10:00:00"}]


universal = {'exit_status': 'Idle', 'exitTime': '15:06:00',
             'ext_txn_type': 'buy', 'minPrice': -8000, 'maxPrice': 16000}

# functions


def get_spot(spot):
    global ltp
    ids = 'NIFTY 50' if idx == 'NIFTY' else 'NIFTY BANK' if idx == 'BANKNIFTY' else None
    try:
        idx_instruments = [{'exchangeSegment': 1, 'exchangeInstrumentID': ids}]
        spot_resp = xt.get_quote(
            Instruments=idx_instruments,
            xtsMessageCode=1504,
            publishFormat='JSON')
        if spot_resp['type'] != 'error':
            listQuotes = json.loads(spot_resp['result']['listQuotes'][0])
            ltp[idx] = listQuotes['IndexValue']
        else:
            logger.error(spot_resp['description'])
            raise Exception(spot_resp['description'])
    except Exception:
        logger.exception(f'Unable to getSpot from index {ids}')


def getLTP():
    global ltp
    # ltp={}
    if tr_insts:
        # logger.info('inside tr_insts cond - getLTP')
        symbols = [i['symbol'] for i in tr_insts if i['set_type'] == 'Entry']
        instruments = []
        for symbol in symbols:
            instruments.append(
                {'exchangeSegment': 2, 'exchangeInstrumentID': symbol})
        xt.send_unsubscription(Instruments=instruments, xtsMessageCode=1502)
        subs_resp = xt.send_subscription(
            Instruments=instruments, xtsMessageCode=1502)
        if subs_resp['type'] == 'success':
            for symbol, i in zip(symbols, range(len(symbols))):
                listQuotes = json.loads(subs_resp['result']['listQuotes'][i])
                ltp[symbol] = listQuotes['Touchline']['LastTradedPrice']


def getGlobalPnL():
    global gl_pnl, df, gdf, pnl_dump
    # pnl_dump = []
    if tr_insts:
        # logger.info('inside tr_insts cond - getGlobalLTP')
        df = pd.DataFrame(tr_insts)
        df['tr_amount'] = df['tr_qty'] * df['tradedPrice']
        df = df.fillna(0)
        df = df.astype(dtype={'set': int, 'txn_type': str, 'strike': int, 'qty': int, 'tr_qty': int, 'expiry': str,
                              'name': str, 'symbol': int, 'orderID': int, 'tradedPrice': float, 'dateTime': str,
                              'set_type': str, 'tr_amount': float, 'optionType': str})
        gdf = df.groupby(['name', 'symbol'], as_index=False).sum()[
            ['symbol', 'name', 'tr_qty', 'tradedPrice', 'tr_amount']]
        gdf['ltp'] = gdf['symbol'].map(ltp)
        gdf['cur_amount'] = gdf['tr_qty'] * gdf['ltp']
        gdf['pnl'] = gdf['cur_amount'] - gdf['tr_amount']
        logger.info(f'\n\nPositionList: \n {df}')
        logger.info(f'\n\nCombinedPositionsLists: \n {gdf}')
        gl_pnl = round(gdf['pnl'].sum(), 2)
        logger.info(f'\n\nGlobal PnL : {gl_pnl} \n')
        pnl_dump.append([time.strftime("%d-%m-%Y %H:%M:%S"), gl_pnl])
    else:
        gl_pnl = 0


def execute(orders):
    global tr_insts
    tr_insts = []
    etr_inst = {}
    rpr_inst = {}
    startTime = datetime.strptime(
        (cdate + " " + orders['startTime']), "%d-%m-%Y %H:%M:%S")
    while True:
        try:
            if startTime >= datetime.now():
                continue
            if orders['status'] == 'Idle':
                etr_inst['legpair'] = orders['legpair']
                etr_inst['set'] = orders['setno']
                etr_inst['txn_type'] = orders['ent_txn_type']
                etr_inst['spot']
                etr_inst['strike'] = xt.strike_price(orders['idx'])
                etr_inst['qty'] = 75 * \
                    orders['lot'] if orders['idx'] == 'NIFTY' else 25 * \
                    orders['lot']
                etr_inst['tr_qty'] = - \
                    etr_inst['qty'] if orders['ent_txn_type'] == 'sell' else etr_inst['qty']
                etr_inst['expiry'] = weekly_exp if orders['expiry'] == 'week' else monthly_exp
                # etr_inst['optionType'] = orders['otype'].upper()
                if weekly_exp == monthly_exp:
                    etr_inst['name'] = orders['idx'] + (datetime.strftime(datetime.strptime(
                        etr_inst['expiry'], '%d%b%Y'), '%y%b')).upper() + str(etr_inst['strike']) + etr_inst['optionType']
                else:
                    etr_inst['name'] = orders['idx'] + (datetime.strftime(datetime.strptime(
                        etr_inst['expiry'], '%d%b%Y'), '%y%#m%d')) + str(etr_inst['strike']) + etr_inst['optionType']
                etr_inst['symbol'] = xt.fo_lookup(
                    etr_inst['name'], instrument_df)
                logger.info(
                    f'Placing orders for {etr_inst["set"]}. {etr_inst["name"]} at {orders["startTime"]}..')
                if etr_inst['symbol'] != -1:
                    orderID = xt.place_order_id(
                        etr_inst['symbol'], etr_inst['txn_type'], etr_inst['qty'])
                else:
                    logger.error(f'Symbol is not valid: {etr_inst["symbol"]}')
                    raise Exception('Symbol is not valid')
                etr_inst['orderID'] = orderID
                if orderID:
                    etr_inst['tradedPrice'], etr_inst['dateTime'] = xt.get_traded_price(
                        orderID)
                etr_inst['set_type'] = 'Entry'
                if etr_inst['tradedPrice']:
                    etr_inst['status'] = 'Sucess'
                    orders['status'] = 'Entered'
                else:
                    etr_inst['status'] = 'Fail'
                    orders['status'] = 'Entry_Failed'
                logger.info(f"\nEntry order dtls:\n {pp(etr_inst)}")
                tr_insts.append(etr_inst)
                logger.info(
                    f'order status of {etr_inst["set"]}.{etr_inst["name"]} is {orders["status"]}')
                continue


if __name__ == '__main__':
    try:
        instrument_df = xt.master_fo_dump()
        weekly_exp, monthly_exp = xt.get_expiry()
        if not all((isinstance(instrument_df, pd.DataFrame), weekly_exp, monthly_exp)):
            raise Exception('Initial setup failed')
    except Exception as e:
        logger.exception(
            f'Failed to get masterDump/ expiryDates. Reason --> {e} \n Exiting..')
        exit()
