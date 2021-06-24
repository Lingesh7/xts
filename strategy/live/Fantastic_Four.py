# -*- coding: utf-8 -*-
"""
Created on Thu May 27 23:50:22 2021
Strategy : Fantastic Four

JINDALSTEL
IBULHSGFIN
TATASTEEL
TATAMOTORS

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
from threading import Thread
from openpyxl import load_workbook
from logging.handlers import TimedRotatingFileHandler
from sys import exit
import os
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

#logger settings
script_name = os.path.basename(__file__).split('.')[0]
logger = configure_logging(script_name)


#inits
xt = xts_init(interactive=True)
if not xt:
    logger.exception('XT initialization failed. Exiting..')
    exit()


cdate = xt.CDATE
# tickers = ['JINDALSTEL','IBULHSGFIN','TATASTEEL','TATAMOTORS']
# startTime = '09:20:00'
# orders = [{'refId':10001, 'setno':1, 'name':"TATAMOTORS", 'symbol':3456, 'status': "Idle",
#           'startTime':"09:20:01", 'capital':50000}]

orders = [{'refId':10001, 'setno':1, 'name':"TATAMOTORS", 'symbol':3456, 'status': "Idle",
          'startTime':"09:20:01", 'capital':50000},
          {'refId':10002, 'setno':2, 'name':"TATASTEEL", 'symbol':3499, 'status': "Idle",
          'startTime':"09:20:01", 'capital':50000},
          {'refId':10003, 'setno':3, 'name':"IBULHSGFIN", 'symbol':30125, 'status': "Idle",
          'startTime':"09:20:01", 'capital':50000},
          {'refId':10004, 'setno':4, 'name':"JINDALSTEL", 'symbol':6733, 'status': "Idle",
          'startTime':"09:20:01", 'capital':50000}]
etr_inst = None
rpr_inst = None
ext_inst = None
tr_insts = None
universal = {'exit_status': 'Idle', 'exitTime':'15:06:00'}
ltp = {}
gl_pnl = None
pnl_dump = []
df = None
gdf = None

#functions

def round_nearest(x,a=0.05):
  return round(round(x/a)*a ,2)


def getLTP():
    global ltp
    # ltp={}
    # if tr_insts:
    # logger.info('inside tr_insts cond - getLTP')
    symbols = [i['symbol'] for i in orders]
    instruments=[]
    for symbol in symbols:
        instruments.append({'exchangeSegment': 1, 'exchangeInstrumentID': symbol})
    xt.send_unsubscription(Instruments=instruments,xtsMessageCode=1502)
    subs_resp=xt.send_subscription(Instruments=instruments,xtsMessageCode=1502)
    if subs_resp['type'] == 'success':
        for symbol,i in zip(symbols,range(len(symbols))):
            listQuotes = json.loads(subs_resp['result']['listQuotes'][i])
            price=listQuotes['Touchline']['LastTradedPrice']
            ltp[symbol]=price


def getGlobalPnL():
    global gl_pnl, df, gdf, pnl_dump
    # pnl_dump = []
    if tr_insts:
        # logger.info('inside tr_insts cond - getGlobalLTP')
        df = pd.DataFrame(tr_insts)
        df['tr_amount'] = df['tr_qty']*df['tradedPrice']
        df = df.fillna(0)
        df = df.astype(dtype={'set': int, 'txn_type': str, 'qty': int, 'tr_qty': int,  \
                                 'name': str, 'symbol': int, 'orderID': int, 'tradedPrice': float, 'dateTime': str, \
                                 'set_type': str, 'tr_amount': float})
        gdf = df.groupby(['name','symbol'],as_index=False).sum()[['symbol','name','tr_qty','tradedPrice','tr_amount']]
        gdf['ltp'] = gdf['symbol'].map(ltp)
        gdf['cur_amount'] = gdf['tr_qty']*gdf['ltp']
        gdf['pnl'] = gdf['cur_amount'] - gdf['tr_amount']
        gl_pnl = round(gdf['pnl'].sum(),2)
        # logger.info(f'\n\nPositionList: \n {df}')
        # logger.info(f'\n\nCombinedPositionsLists: \n {gdf}')
        # logger.info(f'\n\nGlobal PnL : {gl_pnl} \n')
        print("PositionList:" + '\n' + tabulate(df, headers='keys', tablefmt='pretty'))
        print("Combined_Position_Lists:" + '\n' + tabulate(gdf, headers='keys', tablefmt='pretty'))
        print("Global PnL:" + '\n' + tabulate([str(gl_pnl)]))
        pnl_dump.append([time.strftime("%d-%m-%Y %H:%M:%S"),gl_pnl])
    else:
        gl_pnl = 0


def fetchOHLC(symbol,duration):
    # symbol = xt.eq_lookup(ticker,instrument_df)
    cur_date = datetime.strftime(datetime.now(), "%b %d %Y")
    # nowtime = datetime.now().strftime('%H%M%S')
    ohlc = xt.get_ohlc(exchangeSegment=xt.EXCHANGE_NSECM,
                    exchangeInstrumentID=symbol,
                    startTime=f'{cur_date} 091500',
                    endTime=f'{cur_date} 092000',
                    compressionValue=duration)
    dataresp= ohlc['result']['dataReponse']
    data = dataresp.split(',')
    data_df = pd.DataFrame([sub.split("|") for sub in data],columns=(['Timestamp','Open','High','Low','Close','Volume','OI','NA']))
    data_df.drop(data_df.columns[[-1,-2]], axis=1, inplace=True)
    data_df = data_df.astype(dtype={'Open': float, 'High': float, 'Low': float, 'Close': float, 'Volume': int})
    data_df['Timestamp'] = pd.to_datetime(data_df['Timestamp'].astype('int'), unit='s')
    return data_df


def execute(orders):
    global tr_insts
    tr_insts = []
    etr_inst = {}
    rpr_inst = {}
    ext_inst = {}
    startTime = datetime.strptime((cdate+" "+orders['startTime']),"%d-%m-%Y %H:%M:%S")

    while True:
        time.sleep(2)
        # print(f'{orders["name"]}: {ltp[orders["symbol"]]}')
        # logger.info(f'{orders["status"]}')
        if orders['status'] == 'Idle':
            # logger.info('idle block')
            if (datetime.now() >= startTime):
                # symbol = orders['symbol']
                df = fetchOHLC(orders["symbol"], 60)
                # logger.info(df)
                logger.info(f"{orders['name']} - Entered at {df['Timestamp'].iloc[-1]}")
                mark_price = round(float(df['Close'].iloc[-1]),2)
                le = round_nearest(mark_price*1.01)
                lt1 = round_nearest(mark_price*1.02)
                lt2 = round_nearest(mark_price*1.03)
                se = round_nearest(mark_price*0.99)
                st1 = round_nearest(mark_price*0.98)
                st2 = round_nearest(mark_price*0.97)
                if all([le,se,st1,st2,lt1,lt2,mark_price]):
                    orders['status'] = 'active'
                    logger.info(f'{orders["status"]} , {orders["symbol"]} {orders["name"]} {mark_price} {le} {lt1} {lt2} {se} {st1} {st2} ')
                else:
                    continue
        
        if orders['status'] == 'active':
            # logger.info('active block')
            if orders["symbol"] in ltp.keys():
                ltpsymbol = ltp[orders["symbol"]]
                etr_inst['set'] = orders['setno']
                etr_inst['qty'] = int(orders['capital']/le)
                etr_inst['name'] = orders['name']
                etr_inst['symbol'] = orders['symbol']
                etr_inst['orderID'] = None
                etr_inst['tradedPrice'] = None
                if ltpsymbol > le or ltpsymbol < se:
                    if ltpsymbol > le:
                        logger.info(f'{orders["name"]} ltp {ltpsymbol} crossed above {le}')
                        logger.info(f'Placing buy order for {orders["setno"]} {orders["name"]}..')
                        etr_inst['txn_type'] = 'buy'
                    if ltpsymbol < se:
                        logger.info(f'{orders["name"]} ltp {ltpsymbol} crossed below {se}')
                        logger.info(f'Placing sell order for {orders["setno"]} {orders["name"]}..')
                        etr_inst['txn_type'] = 'sell'
                    etr_inst['tr_qty'] = -etr_inst['qty'] if etr_inst['txn_type'] == 'sell' else etr_inst['qty']
                    orderID = xt.place_order_id(etr_inst['symbol'],etr_inst['txn_type'], etr_inst['qty'], xseg='eq')
                    etr_inst['orderID'] = orderID
                    tradedPrice, dateTime = xt.get_traded_price(orderID)
                    etr_inst['tradedPrice'] = tradedPrice
                    etr_inst['dateTime'] = dateTime
                    if orderID and tradedPrice:
                        etr_inst['set_type'] = 'Entry'
                        orders['status'] = 'Entered'
                    else:
                        etr_inst['set_type'] = 'Entry'
                        orders['status'] = 'Entry_Failed'
                    logger.info(f'order status of {orders["name"]} is {orders["status"]}')
                    logger.info(f'Entry order dtls: {etr_inst}')
                    tr_insts.append(etr_inst)
                    logger.info(f'tr_insts order dtls: {tr_insts}')


        if orders['status'] == 'Entered':
            rpr_inst['set'] = orders['setno']
            rpr_inst['txn_type'] = 'sell' if etr_inst['txn_type'] == 'buy' else 'buy'
            rpr_inst['qty'] = etr_inst['qty']
            rpr_inst['tr_qty'] = -rpr_inst['qty'] if rpr_inst['txn_type'] == 'sell' else rpr_inst['qty']
            rpr_inst['name'] = orders['name']
            rpr_inst['symbol'] = orders['symbol']
            rpr_inst['orderID'] = None
            rpr_inst['tradedPrice'] = None
            orderID = xt.place_order_id(rpr_inst['symbol'],rpr_inst['txn_type'], rpr_inst['qty'], sl=mark_price, xseg='eq')
            rpr_inst['orderID'] = orderID
            orders['status'] = 'SL_Placed'
            logger.info(f'order status of {orders["name"]} is {orders["status"]}')

        if universal['exit_status'] == 'Idle' and orders['status'] != 'Idle':
            if orders['status'] == 'SL_Placed' or orders['status'] == 'SL_Modified':
                # logger.info(f'checking SL_Hit condtions for {orders["name"]}')
                orderLists = xt.get_order_list()
                if orderLists:
                    new_sl_orders = [ol for ol in orderLists if ol['AppOrderID'] == rpr_inst['orderID'] and ol['OrderStatus'] != 'Filled']
                    if not new_sl_orders:
                        logger.info(f'Stop Loss Order Triggered for {orders["name"]}')
                        sl_tradedPrice = float(next((orderList['OrderAverageTradedPrice'] \
                                            for orderList in orderLists\
                                                  if orderList['AppOrderID'] == rpr_inst['orderID'] and\
                                                      orderList['OrderStatus'] == 'Filled'),None).replace(',', ''))
                        LastUpdateDateTime=datetime.fromisoformat(next((orderList['LastUpdateDateTime'] for orderList in orderLists if orderList['AppOrderID'] == rpr_inst['orderID'] and orderList['OrderStatus'] == 'Filled'))[0:19])
                        sl_dateTime = LastUpdateDateTime.strftime("%Y-%m-%d %H:%M:%S")
                        logger.info(f"traded price is: {sl_tradedPrice} and ordered time is: {sl_dateTime}")
                        rpr_inst['tradedPrice'] = sl_tradedPrice
                        rpr_inst['dateTime'] = sl_dateTime
                        rpr_inst['set_type'] = 'Repair'
                        etr_inst['set_type'] = [ 'Repaired' for trade in tr_insts if trade["set"] == rpr_inst["set"] ][0]
                        orders['status'] = 'SL_Hit'
                        logger.info(f'order status of {orders["name"]} is {orders["status"]}')
                        logger.info(f'Repair order dtls: {rpr_inst}')
                        tr_insts.append(rpr_inst)
                        continue

            if (ltp[orders['symbol']] > lt1 or ltp[orders['symbol']] < st1) and \
                                                    orders['status'] == 'SL_Placed':
                # xt.modify_order(rpr_inst['orderID'],modifiedStopPrice=lt1)
                if ltp[orders['symbol']] > lt1:
                    logger.info(f'{orders["name"]} ltp {ltpsymbol} crossed above {lt1}, \
                                Hence modifying the SL')
                    modifiedStopPrice = lt1
                elif ltp[orders['symbol']] < st1:
                    logger.info(f'{orders["name"]} ltp {ltpsymbol} crossed below {st1}, \
                                Hence modifying the SL')
                    modifiedStopPrice = st1
                sl_mod_resp = xt.modify_order(
                            appOrderID=rpr_inst['orderID'],
                            modifiedProductType=xt.PRODUCT_MIS,
                            modifiedOrderType='StopMarket',
                            modifiedOrderQuantity=rpr_inst['qty'],
                            modifiedDisclosedQuantity=0,
                            modifiedLimitPrice=0,
                            modifiedStopPrice=modifiedStopPrice,
                            modifiedTimeInForce=xt.VALIDITY_DAY,
                            orderUniqueIdentifier="SL_modify"
                            )
                if sl_mod_resp['type'] == 'success':
                    logger.info(f'Modify order success {rpr_inst["orderID"]} - {orders["name"]}')
                    orders['status'] = 'SL_Modified'
                    logger.info(f'order status of {orders["name"]} is {orders["status"]}')
                continue

            if (ltp[orders['symbol']] >= lt2 or ltp[orders['symbol']] <= st2) and \
                (orders['status'] == 'SL_Placed' or orders['status'] == 'SL_Modified'):
                logger.info(f'{orders["name"]} ltp {ltpsymbol} crossed target2 {lt2}/{st2}')
                ext_inst['set'] = orders['setno']
                ext_inst['symbol'] = orders['symbol']
                ext_inst['qty'] = etr_inst['qty']
                ext_inst['txn_type'] = 'sell' if etr_inst['txn_type'] == 'buy' else 'buy'
                ext_inst['tr_qty'] = -ext_inst['qty'] if ext_inst['txn_type'] == 'sell' else ext_inst['qty']
                ext_inst['name'] = orders['name']
                ext_inst['orderID'] = None
                ext_inst['tradedPrice'] = None
                orderID = xt.place_order_id(ext_inst['symbol'],ext_inst['txn_type'], ext_inst['qty'], xseg='eq')
                ext_inst['orderID'] = orderID
                tradedPrice, dateTime = xt.get_traded_price(orderID)
                ext_inst['tradedPrice'] = tradedPrice
                ext_inst['dateTime'] = dateTime
                if orderID and tradedPrice:
                    ext_inst['set_type']='Target_Hit'
                    etr_inst['set_type'] = [ 'Target_Hit' for trade in tr_insts if trade["set"] == ext_inst["set"] ][0]
                    # universal['exit_status'] = 'Exited'
                else:
                    ext_inst['set_type']='Target_Hit'
                    logger.error(f"Error while exiting the order set \
                                  {orders['setno']}, Exit Immediately")
                logger.info(f'Target exit order dtls: {ext_inst}')
                tr_insts.append(ext_inst)
                orders['status'] = 'Target_Hit'
                logger.info(f'order status of {orders["name"]} is {orders["status"]}')
                continue

        elif universal['exit_status'] == 'Exited':
            orders['status'] = 'Universal_Exit'
            logger.info('Orders must be square-off by Universal Exit Func')
            break

        if orders['status'] == 'SL_Hit' or orders['status'] == 'Entry_Failed':
            logger.info(f'Order must hit SL/Tgt. Exiting. Reason: {orders["status"]}')
            logger.info(f'Completed - Order set: {orders["setno"]}. Exiting the thread')
            break

        if orders['status'] == 'Target_Hit':
            logger.info(f'Target Hit for {orders["name"]}, cancelling SL order')
            xt.cancel_order_id(rpr_inst['orderID'])
            break


def exitCheck(universal):
    global tr_insts
    # pnl_dump=[]
    ext_inst = {}
    exitTime = datetime.strptime((cdate+" "+universal['exitTime']),"%d-%m-%Y %H:%M:%S")
    # print('exitTime:', exitTime)
    while True:
        if universal['exit_status'] == 'Idle':
            #Exit condition check
            if (datetime.now() >= exitTime):
                logger.info('Exit time condition passed. Squaring off all open positions')
                for trade in tr_insts:
                    if trade['set_type'] == 'Entry':
                        if trade['txn_type'] == 'buy':
                            ext_inst['set'] = trade['set']
                            ext_inst['txn_type'] = 'sell'
                            ext_inst['qty'] = trade['qty']
                            ext_inst['tr_qty'] = -ext_inst['qty']
                            ext_inst['name'] = trade['name']
                            ext_inst['symbol'] = trade['symbol']
                            ext_inst['orderID'] = None
                            ext_inst['tradedPrice'] = None
                            orderID = xt.place_order_id(ext_inst['symbol'],ext_inst['txn_type'], ext_inst['qty'], xseg='eq')
                            ext_inst['orderID'] = orderID
                            tradedPrice, dateTime = xt.get_traded_price(orderID)
                            ext_inst['tradedPrice'] = tradedPrice
                            ext_inst['dateTime'] = dateTime
                            if orderID and tradedPrice:
                                ext_inst['set_type'] = 'Exit'
                                trade['set_type'] = 'Exited'
                                logger.info(f'Unive Exit sell order details : {ext_inst}')
                                tr_insts.append(ext_inst.copy())
                                logger.info(f' Ext tr_insts: {tr_insts}')
                        if trade['txn_type'] == 'sell':
                            ext_inst['txn_type'] = 'buy'
                            ext_inst['qty'] = trade['qty']
                            ext_inst['tr_qty'] = ext_inst['qty']
                            ext_inst['name'] = trade['name']
                            ext_inst['symbol'] = trade['symbol']
                            ext_inst['orderID'] = None
                            ext_inst['tradedPrice'] = None
                            orderID = xt.place_order_id(ext_inst['symbol'],ext_inst['txn_type'], ext_inst['qty'], xseg='eq')
                            ext_inst['orderID'] = orderID
                            tradedPrice, dateTime = xt.get_traded_price(orderID)
                            ext_inst['tradedPrice'] = tradedPrice
                            ext_inst['dateTime'] = dateTime
                            if orderID and tradedPrice:
                                ext_inst['set_type'] = 'Exit'
                                trade['set_type'] = 'Exited'
                                logger.info(f'Univ Exit Buy details : {ext_inst}')
                                tr_insts.append(ext_inst.copy())
                                logger.info(f'tr_insts: {tr_insts}')
                logger.info('breaking from exitCheck function loop')
                universal['exit_status'] = 'Exited'
                logger.info(f'Universal exit status : {universal["exit_status"]}')
                break
            elif [order['status'] for order in orders].count('SL_Hit') == len(orders):
                logger.info('All sets hit stop loss. Closing the exitCheck func..')
                universal['exit_status'] = 'Exited'
                break
            else:
                time.sleep(5)


if __name__ == '__main__':
    threads=[]
    # all the sets will execute in parallel with threads
    getLTP()
    for i in range(len(orders)):
        t = Thread(target=execute,args=(orders[i],))
        t.start()
        threads.append(t)
    # below function runs in background
    logger.info('Starting a timer based thread to fetch LTP of traded instruments..')
    getGlobalPnL()
    fetchLtp = RepeatedTimer(5, getLTP)
    fetchPnL = RepeatedTimer(60, getGlobalPnL)
    try:
        exitCheck(universal)
        time.sleep(5)
    except KeyboardInterrupt:
        logger.error('\n\nKeyboard exception received. Exiting.')
        universal['exit_status'] = 'Exited' #todo write dead case here to stop the threads in case of exitcheck exception
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
        #prints dump to excel
        getGlobalPnL()      #getting latest data
        data_to_excel(pnl_dump, df, gdf, gl_pnl, script_name,'09:20')
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

