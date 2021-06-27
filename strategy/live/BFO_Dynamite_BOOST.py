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
from tabulate import tabulate
from pprint import pformat as pp
from openpyxl import load_workbook
from logging.handlers import TimedRotatingFileHandler

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
os.chdir(r'D:\Python\First_Choice_Git\xts\strategy\live')

from utils.utils import xts_init, \
                        configure_logging, \
                        RepeatedTimer, \
                        data_to_excel, \
                        logger_tab,\
                        bot_init, \
                        bot_sendtext

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


orders = [{'legpair': 1, 'setno': 1, 'ent_txn_type': "sell", 'rpr_txn_type': "buy",
           'idx': "BANKNIFTY", 'otype': "ce", 'status': "Idle", 'expiry': 'week', 'lot': 1,
           'startTime': "09:30:00", 'move': 0.75, 'endTime':"14:45:00"},
          {'legpair': 1, 'setno': 2, 'ent_txn_type': "sell", 'rpr_txn_type': "buy",
           'idx': "BANKNIFTY", 'otype': "pe", 'status': "Idle", 'expiry': 'week', 'lot': 1,
           'startTime': "09:30:00", 'move': 0.75, 'endTime':"14:45:00"},
           {'legpair': 2, 'setno': 3, 'ent_txn_type': "sell", 'rpr_txn_type': "buy",
           'idx': "BANKNIFTY", 'otype': "ce", 'status': "Idle", 'expiry': 'week', 'lot': 1,
           'startTime': "10:00:00", 'move': 0.75, 'endTime':"14:45:00"},
          {'legpair': 2, 'setno': 4, 'ent_txn_type': "sell", 'rpr_txn_type': "buy",
           'idx': "BANKNIFTY", 'otype': "pe", 'status': "Idle", 'expiry': 'week', 'lot': 1,
           'startTime': "10:00:00", 'move': 0.75, 'endTime':"14:45:00"},
           {'legpair': 3, 'setno': 5, 'ent_txn_type': "sell", 'rpr_txn_type': "buy",
           'idx': "BANKNIFTY", 'otype': "ce", 'status': "Idle", 'expiry': 'week', 'lot': 1,
           'startTime': "10:30:00", 'move': 0.75, 'endTime':"14:45:00"},
          {'legpair': 3, 'setno': 6, 'ent_txn_type': "sell", 'rpr_txn_type': "buy",
           'idx': "BANKNIFTY", 'otype': "pe", 'status': "Idle", 'expiry': 'week', 'lot': 1,
           'startTime': "10:30:00", 'move': 0.75, 'endTime':"14:45:00"},
           {'legpair': 4, 'setno': 7, 'ent_txn_type': "sell", 'rpr_txn_type': "buy",
           'idx': "BANKNIFTY", 'otype': "ce", 'status': "Idle", 'expiry': 'week', 'lot': 1,
           'startTime': "11:00:00", 'move': 0.75, 'endTime':"14:45:00"},
          {'legpair': 4, 'setno': 8, 'ent_txn_type': "sell", 'rpr_txn_type': "buy",
           'idx': "BANKNIFTY", 'otype': "pe", 'status': "Idle", 'expiry': 'week', 'lot': 1,
           'startTime': "11:00:00", 'move': 0.75, 'endTime':"14:45:00"}]

universal = {'exit_status': 'Idle', 'exitTime': '15:06:00', 'ext_txn_type': 'buy', 'minPrice': -8000, 'maxPrice': 16000}

# functions
def get_spot(idx):
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
        gl_pnl = round(gdf['pnl'].sum(), 2)
        # logger.info(f'\n\nPositionList: \n {df}')
        # logger.info(f'\n\nCombinedPositionsLists: \n {gdf}')
        # logger.info(f'\n\nGlobal PnL : {gl_pnl} \n')
        # print(f'\n\nPositionList: \n {df}')
        # print(f'\n\nCombinedPositionsLists: \n {gdf}')
        # print(f'\n\nGlobal PnL : {gl_pnl} \n')
        print("PositionList:" + '\n' + tabulate(df, headers='keys', tablefmt='pretty'))
        print("Combined_Position_Lists:" + '\n' + tabulate(gdf, headers='keys', tablefmt='pretty'))
        print("Global PnL:" + '\n' + tabulate([str(gl_pnl)]))
        pnl_dump.append([time.strftime("%d-%m-%Y %H:%M:%S"), gl_pnl])
    else:
        gl_pnl = 0


def execute(orders):
    global tr_insts
    tr_insts = []
    etr_inst = {}
    rpr_inst = {}
    startTime = datetime.strptime((cdate + " " + orders['startTime']), "%d-%m-%Y %H:%M:%S")
    endTime = datetime.strptime((cdate + " " + orders['endTime']), "%d-%m-%Y %H:%M:%S")
    while True:
        try:
            if startTime >= datetime.now():
                continue
            if universal['exit_status'] == 'Idle' and (endTime > datetime.now()):
                if orders['status'] == 'Idle':
                    etr_inst['legpair'] = orders['legpair']
                    etr_inst['set'] = orders['setno']
                    etr_inst['txn_type'] = orders['ent_txn_type']
                    etr_inst['spot'] = ltp[orders['idx']]
                    etr_inst['strike'] = 100 * round(etr_inst['spot']/100) if orders['idx'] == 'BANKNIFTY' else 50 * round(etr_inst['spot']/50)
                    etr_inst['qty'] = 75 * orders['lot'] if orders['idx'] == 'NIFTY' else 25 * orders['lot']
                    etr_inst['tr_qty'] = -etr_inst['qty'] if orders['ent_txn_type'] == 'sell' else etr_inst['qty']
                    etr_inst['expiry'] = weekly_exp if orders['expiry'] == 'week' else monthly_exp
                    etr_inst['optionType'] = orders['otype'].upper()
                    if weekly_exp == monthly_exp:
                        etr_inst['name'] = orders['idx'] + (datetime.strftime(datetime.strptime(
                            etr_inst['expiry'], '%d%b%Y'), '%y%b')).upper() + str(etr_inst['strike']) + etr_inst['optionType']
                    else:
                        etr_inst['name'] = orders['idx'] + (datetime.strftime(datetime.strptime(
                            etr_inst['expiry'], '%d%b%Y'), '%y%#m%d')) + str(etr_inst['strike']) + etr_inst['optionType']
                    etr_inst['symbol'] = xt.fo_lookup(etr_inst['name'], instrument_df)
                    logger.info(f'Placing entry orders for leg {etr_inst["legpair"]} - set {etr_inst["set"]} - {etr_inst["name"]}')
                    orderID = None
                    if etr_inst['symbol'] != -1:
                        orderID = xt.place_order_id(etr_inst['symbol'], etr_inst['txn_type'], etr_inst['qty'])
                    else:
                        logger.error(f'Symbol is not valid: {etr_inst["symbol"]}')
                        raise Exception('Symbol is not valid')
                    etr_inst['orderID'] = orderID
                    if orderID:
                        etr_inst['tradedPrice'], etr_inst['dateTime'] = xt.get_traded_price(orderID)
                    etr_inst['set_type'] = 'Entry'
                    if etr_inst['tradedPrice']:
                        etr_inst['status'] = 'Success'
                        orders['status'] = 'Entered'
                    else:
                        etr_inst['status'] = 'Fail'
                        orders['status'] = 'Entry_Failed'
                    # logger.info(f"\nEntry order dtls:\n {pp(etr_inst)}")
                    logger_tab(etr_inst, 'Entry Order Details')
                    tr_insts.append(etr_inst.copy())
                    #logger.info(f'order status of leg {etr_inst["legpair"]} - set {etr_inst["set"]} - {etr_inst["name"]} is {orders["status"]}')
                    continue
                if orders['status'] == 'Entered':
                    if ltp[orders['idx']] > (etr_inst['spot'] * (1+(orders["move"]/100))) or ltp[orders['idx']] < (etr_inst['spot'] * (1-(orders["move"]/100))):
                        logger.info(f'{spot} crossed +/- {orders["move"]}.')
                        rpr_inst['legpair'] = orders['legpair']
                        rpr_inst['set'] = orders['setno']
                        rpr_inst['txn_type'] = orders['rpr_txn_type']
                        rpr_inst['strike'] = etr_inst['strike']
                        rpr_inst['qty'] = etr_inst['qty']
                        rpr_inst['tr_qty'] = -rpr_inst['qty'] if orders['rpr_txn_type'] == 'sell' else rpr_inst['qty']
                        rpr_inst['expiry'] = etr_inst['expiry']
                        rpr_inst['optionType'] = etr_inst['optionType']
                        rpr_inst['name'] = etr_inst["name"]
                        rpr_inst['symbol'] = etr_inst["symbol"]
                        logger.info(f'Placing exit orders for leg {rpr_inst["legpair"]} - set {rpr_inst["set"]} - {rpr_inst["name"]} at ')
                        rpr_inst['orderID'] = xt.place_order_id(rpr_inst['symbol'], rpr_inst['txn_type'], rpr_inst['qty'])
                        if rpr_inst['orderID']:
                            rpr_inst['tradedPrice'], rpr_inst['dateTime'] = xt.get_traded_price(rpr_inst['orderID'])
                        rpr_inst['set_type'] = 'Repair'
                        if rpr_inst['tradedPrice']:
                            rpr_inst['status'] = 'Success'
                            orders['status'] = 'Idle' #so that it will again start from the begining
                        else:
                            rpr_inst['status'] = 'Fail'
                            orders['status'] = 'Repair_Failed'
                        # logger.info(f"\nRepair order dtls:\n {pp(rpr_inst)}")
                        logger_tab(rpr_inst, 'Repair Order Details')
                        tr_insts.append(rpr_inst.copy())
                        logger.info(
                            f'order status of leg {rpr_inst["legpair"]} - set {rpr_inst["set"]} - {rpr_inst["name"]} is {orders["status"]}')
                        continue
            elif universal['exit_status'] == 'Exited':
                logger.info(f'Universal exit condition passed. Exiting the leg {orders["legpair"]} - set {orders["setno"]}')
                break
            if orders['status'] == 'Entry_Failed' or orders['status'] == 'Repair_Failed':
                logger.info(f'Exiting todays trade as entry/repair missed. Reason: {orders["status"]}')
                logger.info(f'Order Failed - Order leg {orders["legpair"]} - set: {orders["setno"]}. Exiting the thread')
                break
        except:
            logger.exception(f'API Error in MultiThread - leg {orders["legpair"]} - set: {orders["setno"]}')
            break


def exitCheck(universal):
    global tr_insts
    ext_inst = {}
    exitTime = datetime.strptime((cdate + " " + universal['exitTime']), "%d-%m-%Y %H:%M:%S")
    while universal['exit_status'] == 'Idle':
        if (datetime.now() >= exitTime) or (gl_pnl <= universal['minPrice']) or (gl_pnl >= universal['maxPrice']):
            logger.info('Exit time condition passed. Squaring off all open positions')
            if gdf is None:
                continue
            for i in range(len(gdf)):
                if gdf["tr_qty"].values[i] == 0:
                    continue
                ext_inst['symbol'] = int(gdf['symbol'].values[i])
                ext_inst['qty'] = abs(int(gdf['tr_qty'].values[i]))
                ext_inst['tr_qty'] = -ext_inst['qty'] if universal['ext_txn_type'] == 'sell' else ext_inst['qty']
                ext_inst['txn_type'] = universal['ext_txn_type']
                ext_inst['name'] = str(gdf['name'].values[i])
                ext_inst['optionType'] = ext_inst['name'][-2:]
                ext_inst['strike'] = ext_inst['name'][-7:-2]
                ext_inst['orderID'] = xt.place_order_id(ext_inst['symbol'], ext_inst['txn_type'], ext_inst['qty'])
                ext_inst['tradedPrice'], ext_inst['dateTime']  = xt.get_traded_price(ext_inst['orderID'])
                ext_inst['set_type'] = 'Universal_Exit'
                if ext_inst['orderID'] and ext_inst['tradedPrice']:
                    ext_inst['status'] = 'Success'
                else:
                    ext_inst['status'] = 'Fail'
                    logger.error(f"Error while exiting the order set {orders['setno']}, Exit Immediately")
                # logger.info(f'Universal Exit order dtls: {ext_inst}')
                # logger.info(f"\nUniversal Exit order dtls:\n {pp(ext_inst)}")
                logger_tab(ext_inst, 'Universal Exit Order Details')
                tr_insts.append(ext_inst.copy())
            # logger.info('Universal exit func completed. Breaking the main loop')
            universal['exit_status'] = 'Exited'
            #logger.info(f'order status of leg {etr_inst["legpair"]} - set {etr_inst["set"]} - {etr_inst["name"]} is {orders["status"]}')
            logger.info('Universal exit func completed. Breaking the main loop')
        else:
            time.sleep(1)

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
    get_spot(spot)
    fetch_spot = RepeatedTimer(3, get_spot, spot)
    # all the sets will execute in parallel with threads
    for i in range(len(orders)):
        t = Thread(target=execute, args=(orders[i],))
        t.start()
        threads.append(t)
     # below function runs in background
    logger.info('Starting a timer based thread to fetch LTP of traded instruments..')
    getGlobalPnL()
    fetchLtp = RepeatedTimer(5, getLTP)
    fetchPnL = RepeatedTimer(5, getGlobalPnL)
    try:
        exitCheck(universal)
        time.sleep(5)
    except KeyboardInterrupt:
        logger.error('\n\nKeyboard exception received. Exiting.')
        universal['exit_status'] = 'Exited' #todo write dead case here to stop the threads in case of exitcheck exception
        # exit()
    except Exception:
        universal['exit_status'] = 'Exited'
        logger.exception('Error Occured..')
    finally:
        logger.info('Cleaning up..')
        fetch_spot.stop()
        fetchLtp.stop()
        fetchPnL.stop()
        _ = [t.join() for t in threads]
        time.sleep(5)
        # prints dump to excel
        getGlobalPnL()  # getting latest data
        if isinstance(df, pd.DataFrame):
            data_to_excel(pnl_dump, df, gdf, gl_pnl, script_name)
        # logger.info('--------------------------------------------')
        # logger.info(f'Total Orders and its status: \n {tr_insts} \n')
        # logger.info('********** Summary **********')
        # logger.info(f'\n\n PositionList: \n {df}')
        # logger.info(f'\n\n CombinedPositionsLists: \n {gdf}')
        # logger.info(f'\n\n Global PnL : {gl_pnl} \n')
        # logger.info('--------------------------------------------')
        logger_tab(tr_insts, 'Total Orders')
        logger_tab(df, 'PositionList')
        logger_tab(gdf, 'Combined_Position_Lists')
        logger_tab(gl_pnl, 'Global PnL')

