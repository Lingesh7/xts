# -*- coding: utf-8 -*-
"""
Created on Thu Jun 3 23:50:22 2021
Strategy : ATM Short Straddle at 01:00 pM
Banknifty ATM short straddle
Entry time 1.00 pm
Exit time 02.55 PM
SL 30% points in CE
SL 30% points in PE
https://www.youtube.com/watch?v=O0PDivTMZXE
@author: lmahendran
"""
from datetime import datetime
import XTConnect.Exception as ex
from pathlib import Path
import time
import json
import logging
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
# pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', -1)
import configparser
import argparse
from threading import Thread
from openpyxl import load_workbook
from logging.handlers import TimedRotatingFileHandler
from sys import exit
import os
from pprint import pformat as pp
from tabulate import tabulate

try:
    os.chdir(r'D:\Python\First_Choice_Git\xts\strategy\live')
except:
    pass

from utils.utils import xts_init, \
                        configure_logging, \
                        RepeatedTimer, \
                        data_to_excel, \
                        logger_tab,\
                        bot_init, \
                        bot_sendtext

############## parsing args ##############

parser = argparse.ArgumentParser(description='Optionables Script')
parser.add_argument('-t', '--ticker',type=str, required=True, help='NIFTY or BANKNIFTY')
parser.add_argument('-st', '--startTime',type=str, required=True, help='start time of the script')
parser.add_argument('-et', '--endTime',type=str, default="15:05:00", help='end time')
# parser.add_argument('-rt', '--repairTime',type=str, default="14:40:00", help='reapir time')
# parser.add_argument('-sl', '--stopLoss',type=int, default=-1500, help='stopLoss amount')
# parser.add_argument('-tgt', '--target',type=int, default=3000, help='Target amount')
args = parser.parse_args()

ticker = args.ticker
startTime = args.startTime
endTime = args.endTime
# repairTime = args.repairTime
# stopLoss = args.stopLoss
# target = args.target

# logger settings
script_name = os.path.basename(__file__).split('.')[0]
logger = configure_logging(script_name, startTime)


# inits
xt = xts_init(interactive=True)
if not xt:
    logger.exception('XT initialization failed. Exiting..')
    exit()
b_tok = bot_init()
cdate = xt.CDATE


orders = [{'refId': 10001, 'setno': 1, 'ent_txn_type': "sell", 'rpr_txn_type': "buy",
           'idx': ticker, 'otype': "ce", 'status': "Idle", 'expiry': 'week', 'lot': 1,
           'startTime': startTime, 'sl_points': 1.30},
          {'refId': 10002, 'setno': 2, 'ent_txn_type': "sell", 'rpr_txn_type': "buy",
           'idx': ticker, 'otype': "pe", 'status': "Idle", 'expiry': 'week', 'lot': 1,
           'startTime': startTime, 'sl_points': 1.30}]

universal = {'exit_status': 'Idle',
             'ext_txn_type': 'buy', 'exitTime': endTime}

etr_inst = None
rpr_inst = None
ext_inst = None
tr_insts = None
ltp = {}
gl_pnl = None
pnl_dump = []
df = None

# functions
def round_nearest(x,a=0.05):
  return round(round(x/a)*a ,2)

def getLTP():
    global ltp
    # ltp={}
    if tr_insts:
        # logger.info('inside tr_insts cond - getLTP')
        symbols = [i['symbol'] for i in tr_insts if i['set_type'] == 'Entry' and i['tradedPrice'] != 0]
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
                price = listQuotes['Touchline']['LastTradedPrice']
                ltp[symbol] = price


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
        # logger.info(f'\n\nPositionList: \n {df}')
        # logger.info(f'\n\nCombinedPositionsLists: \n {gdf}')
        gl_pnl = round(gdf['pnl'].sum(), 2)
        # logger.info(f'\n\nGlobal PnL : {gl_pnl} \n')
        print("PositionList:" + '\n' + tabulate(df, headers='keys', tablefmt='pretty'))
        print("Combined_Position_Lists:" + '\n' + tabulate(gdf, headers='keys', tablefmt='pretty'))
        print("Global PnL:" + '\n' + tabulate([gl_pnl]))
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
        if orders['status'] == 'Idle':
            if (datetime.now() >= startTime):
                etr_inst['set'] = orders['setno']
                etr_inst['txn_type'] = orders['ent_txn_type']
                etr_inst['strike'] = xt.strike_price(orders['idx'])
                etr_inst['qty'] = 75 * \
                    orders['lot'] if orders['idx'] == 'NIFTY' else 25 * \
                    orders['lot']
                etr_inst['tr_qty'] = - \
                    etr_inst['qty'] if orders['ent_txn_type'] == 'sell' else etr_inst['qty']

                if orders['expiry'] == 'week':
                    etr_inst['expiry'] = weekly_exp
                etr_inst['optionType'] = orders['otype'].upper()

                if weekly_exp == monthly_exp:
                    etr_inst['name'] = orders['idx'] + (datetime.strftime(datetime.strptime(
                        etr_inst['expiry'], '%d%b%Y'), '%y%b')).upper() + str(etr_inst['strike']) + etr_inst['optionType']
                else:
                    etr_inst['name'] = orders['idx'] + (datetime.strftime(datetime.strptime(
                        etr_inst['expiry'], '%d%b%Y'), '%y%#m%d')) + str(etr_inst['strike']) + etr_inst['optionType']
                etr_inst['symbol'] = xt.fo_lookup(
                    etr_inst['name'], instrument_df)
                etr_inst['orderID'] = None
                etr_inst['tradedPrice'] = None
                logger.info(
                    f'Placing orders for {etr_inst["set"]}. {etr_inst["name"]} at {orders["startTime"]}..')
                orderID = xt.place_order_id(
                    etr_inst['symbol'], etr_inst['txn_type'], etr_inst['qty'])
                etr_inst['orderID'] = orderID
                if orderID:
                    tradedPrice, dateTime = xt.get_traded_price(orderID)
                    etr_inst['tradedPrice'] = tradedPrice
                    etr_inst['dateTime'] = dateTime
                etr_inst['set_type'] = 'Entry'
                if orderID and tradedPrice:
                    etr_inst['status'] = 'Success'
                    orders['status'] = 'Entered'
                else:
                    etr_inst['status'] = 'Fail'
                    orders['status'] = 'Entry_Failed'
                # logger.info(f'Entry order dtls: {etr_inst}')
                logger.info(f"\nEntry order dtls:\n {pp(etr_inst)}")
                tr_insts.append(etr_inst)
                logger.info(
                    f'order status of {etr_inst["set"]}.{etr_inst["name"]} is {orders["status"]}')

        if orders['status'] == 'Entered':
            logger.info(
                f'Placing SL order for {etr_inst["set"]}. {etr_inst["name"]}')
            rpr_inst['set'] = orders['setno']
            rpr_inst['txn_type'] = orders['rpr_txn_type']
            # rpr_inst['strike'] = strikePrice(orders['idx'])
            rpr_inst['strike'] = etr_inst['strike']
            rpr_inst['qty'] = etr_inst['qty']
            rpr_inst['tr_qty'] = - \
                rpr_inst['qty'] if orders['rpr_txn_type'] == 'sell' else rpr_inst['qty']
            # if orders['expiry'] == 'week':
            #     rpr_inst['expiry'] = weekly_exp
            rpr_inst['expiry'] = etr_inst['expiry']
            rpr_inst['optionType'] = etr_inst['optionType']
            rpr_inst['name'] = etr_inst["name"]
            rpr_inst['symbol'] = etr_inst["symbol"]
            sl = round_nearest(etr_inst['tradedPrice'] * orders["sl_points"])
            orderID_sl = xt.place_order_id(
                rpr_inst['symbol'], rpr_inst['txn_type'], rpr_inst['qty'], sl=sl)
            rpr_inst['orderID'] = orderID_sl
            rpr_inst['status'] = 'TriggerPending'
            orders['status'] = 'SL_Placed'
            logger.info(
                f'order status of {rpr_inst["set"]}.{rpr_inst["name"]} is {orders["status"]}')
            logger.info(f"\nRepair order dtls:\n {pp(rpr_inst)}")
            continue

        if universal['exit_status'] == 'Idle':
            if orders['status'] == 'SL_Placed':
                orderLists = xt.get_order_list()
                if orderLists:
                    new_sl_orders = [ol for ol in orderLists if ol['AppOrderID']
                                     == rpr_inst['orderID'] and ol['OrderStatus'] != 'Filled']
                    if not new_sl_orders:
                        logger.info(
                            f'Stop Loss Order Triggered for {rpr_inst["set"]}. {rpr_inst["name"]}')
                        sl_tradedPrice = float(next((orderList['OrderAverageTradedPrice']
                                                     for orderList in orderLists
                                                     if orderList['AppOrderID'] == rpr_inst['orderID'] and
                                                     orderList['OrderStatus'] == 'Filled'), None).replace(',', ''))
                        LastUpdateDateTime = datetime.fromisoformat(next(
                            (orderList['LastUpdateDateTime'] for orderList in orderLists if orderList['AppOrderID'] == rpr_inst['orderID'] and orderList['OrderStatus'] == 'Filled'))[0:19])
                        sl_dateTime = LastUpdateDateTime.strftime(
                            "%Y-%m-%d %H:%M:%S")
                        logger.info(
                            f"Stop Loss traded price is: {sl_tradedPrice} and ordered time is: {sl_dateTime}")
                        rpr_inst['tradedPrice'] = sl_tradedPrice
                        rpr_inst['dateTime'] = sl_dateTime
                        rpr_inst['set_type'] = 'Repair'
                        rpr_inst['status'] = 'Success'
                        orders['status'] = 'SL_Hit'
                        # logger.info(f'Repair order dtls: {rpr_inst}')
                        logger.info(f"\nRepair order dtls:\n {pp(rpr_inst)}")
                        bot_sendtext(f'SL HIT on {rpr_inst["set"]}. {rpr_inst["name"]}', b_tok)
                        tr_insts.append(rpr_inst)
                        logger.info(
                            f'order status of {rpr_inst["set"]}.{rpr_inst["name"]} is {orders["status"]}')
                        continue

        elif universal['exit_status'] == 'Exited':
            orders['status'] = 'Universal_Exit'
            logger.info(
                f'Univ Exit cond passed for {etr_inst["set"]}. {etr_inst["name"]}, hence cancelling SL order')
            xt.cancel_order_id(rpr_inst['orderID'])
            break

        if orders['status'] == 'SL_Hit' or orders['status'] == 'Entry_Failed':
            logger.info(
                f'Order must hit SL/Tgt. Exiting. Reason: {orders["status"]}')
            logger.info(
                f'Completed - Order set: {orders["setno"]}. Exiting the thread')
            break
        time.sleep(2)


def exitCheck(universal):
    global tr_insts
    ext_inst = {}
    exitTime = datetime.strptime(
        (cdate + " " + universal['exitTime']), "%d-%m-%Y %H:%M:%S")
    # print('exitTime:', exitTime)
    while True:
        if universal['exit_status'] == 'Idle':
            # Exit condition check
            # logger.info(f'exitcheck - {gl_pnl}') #todo comment this line after execution
            if (datetime.now() >= exitTime):
                logger.info(
                    'Exit time condition passed. Squaring off all open positions')
                for i in range(len(gdf)):
                    if gdf["tr_qty"].values[i] == 0:
                        continue
                    ext_inst['symbol'] = int(gdf['symbol'].values[i])
                    # ext_inst['tr_qty'] = -int(gdf['tr_qty'].values[i])
                    # ext_inst['qty'] = abs(ext_inst['tr_qty'])
                    ext_inst['qty'] = abs(int(gdf['tr_qty'].values[i]))
                    ext_inst['tr_qty'] = - \
                        ext_inst['qty'] if universal['ext_txn_type'] == 'sell' else ext_inst['qty']
                    ext_inst['txn_type'] = universal['ext_txn_type']
                    ext_inst['name'] = str(gdf['name'].values[i])
                    ext_inst['optionType'] = ext_inst['name'][-2:]
                    ext_inst['strike'] = ext_inst['name'][-7:-2]
                    ext_inst['orderID'] = None
                    ext_inst['tradedPrice'] = None
                    orderID = xt.place_order_id(
                        ext_inst['symbol'], ext_inst['txn_type'], ext_inst['qty'])
                    ext_inst['orderID'] = orderID
                    tradedPrice, dateTime = xt.get_traded_price(orderID)
                    ext_inst['tradedPrice'] = tradedPrice
                    ext_inst['dateTime'] = dateTime
                    ext_inst['set_type'] = 'Universal_Exit'
                    if orderID and tradedPrice:
                        ext_inst['status'] = 'Success'
                        # universal['exit_status'] = 'Exited'
                    else:
                        ext_inst['status'] = 'Fail'
                        logger.error(f"Error while exiting the order set \
                                     {orders['setno']}, Exit Immediately")
                    # logger.info(f'Universal Exit order dtls: {ext_inst}')
                    logger.info(
                        f"\nUniversal Exit order dtls:\n {pp(ext_inst)}")
                    tr_insts.append(ext_inst.copy())
                logger.info(
                    'Universal exit func completed. Breaking the main loop')
                universal['exit_status'] = 'Exited'
                break
            elif [order['status'] for order in orders].count('SL_Hit') == len(orders):
                logger.info('All sets hit stop loss. Closing the exitCheck func..')
                universal['exit_status'] = 'Exited'
                break
            else:
                time.sleep(2)


if __name__ == '__main__':
    threads = []
    try:
        instrument_df = xt.master_fo_dump()
        weekly_exp, monthly_exp = xt.get_expiry()
        if not all((isinstance(instrument_df, pd.DataFrame), weekly_exp, monthly_exp)):
            raise Exception('Initial setup failed')
    except Exception as e:
        logger.exception(
            f'Failed to get masterDump/ expiryDates. Reason --> {e} \n Exiting..')
        exit()
    # all the sets will execute in parallel with threads
    for i in range(len(orders)):
        t = Thread(target=execute, args=(orders[i],))
        t.start()
        threads.append(t)
     # below function runs in background
    logger.info(
        'Starting a timer based thread to fetch LTP of traded instruments..')
    getGlobalPnL()
    fetchLtp = RepeatedTimer(59, getLTP)
    fetchPnL = RepeatedTimer(60, getGlobalPnL)
    try:
        exitCheck(universal)
        time.sleep(5)
    except KeyboardInterrupt:
        logger.error('\n\nKeyboard exception received. Exiting.')
        # todo write dead case here to stop the threads in case of exitcheck exception
        universal['exit_status'] = 'Exited'
        exit()
    except Exception:
        universal['exit_status'] = 'Exited'
        logger.exception('Error Occured..')
    finally:
        logger.info('Cleaning up..')
        fetchLtp.stop()
        fetchPnL.stop()
        _ = [t.join() for t in threads]
        time.sleep(5)
        # prints dump to excel
        getGlobalPnL()  # getting latest data
        msg_df = pd.DataFrame(pnl_dump, columns=['date', 'pl'])
        msg_df = msg_df.set_index(['date'])
        msg_df.index = pd.to_datetime(msg_df.index, format='%d-%m-%Y %H:%M:%S')
        t_df = msg_df['pl'].resample('1min').ohlc()
        minp, maxp = t_df['close'].min(), t_df['close'].max()
        bot_sendtext(
            f'\n {script_name}: {startTime} \n Min PnL:{minp} \n Max PnL:{maxp} \n Final PnL:{gl_pnl}', b_tok)
        data_to_excel(pnl_dump, df, gdf, gl_pnl, script_name, startTime)
        # logging the orders and data to log file
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
