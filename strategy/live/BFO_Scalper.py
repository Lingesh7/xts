# -*- coding: utf-8 -*-
"""
Strategy : BFO Scalper
Entry time : 0920
Exit time : 1505 
X= +300 friday to Wednesday ( Expiry - 1 day) , +200 for expiry day  ( in case of CE)
X= -300 friday to Wednesday ( Expiry - 1 day) , -200 for expiry day  ( in case of PE)
Long Set up
SMA 8 cross over 0.2% abv VWAP
SELL short straddle ATM + X points

Short Set up
SMA 8 cross over 0.2% blw VWAP
SELL short straddle ATM - X points

Day SL : -3000
Day TGT : + 7500
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

try:
    os.chdir(r'D:\Python\First_Choice_Git\xts\strategy\live')
except:
    pass

from utils.utils import xts_init, \
    configure_logging, \
    RepeatedTimer, \
    data_to_excel

# logger settings
script_name = os.path.basename(__file__).split('.')[0]
logger = configure_logging(script_name)


# inits
xt = xts_init(interactive=True)
if not xt:
    logger.exception('XT initialization failed. Exiting..')
    exit()

cdate = xt.CDATE
# tickers = ['JINDALSTEL','IBULHSGFIN','TATASTEEL','TATAMOTORS']
# startTime = '09:20:00'
# orders = [{'refId':10001, 'setno':1, 'name':"TATAMOTORS", 'symbol':3456, 'status': "Idle",
#           'startTime':"09:20:01", 'capital':50000}]

orders = [{'refId': 10001, 'setno': 1, 'ent_txn_type': "sell", 'rpr_txn_type': "buy",
           'idx': "BANKNIFTY", 'otype': "ce", 'status': "Idle", 'expiry': 'week', 'lot': 1, 'startTime': "09:59:00" },
          {'refId': 10002, 'setno': 2, 'ent_txn_type': "sell", 'rpr_txn_type': "buy",
           'idx': "BANKNIFTY", 'otype': "pe", 'status': "Idle", 'expiry': 'week', 'lot': 1, 'startTime': "09:59:00"}]
universal = {'exit_status': 'Idle', 'exitTime': '15:06:00', 'ext_txn_type': 'buy','minPrice': -3000, 'maxPrice': 7500}

etr_inst = None
rpr_inst = None
ext_inst = None
tr_insts = None
ltp = {}
gl_pnl = None
pnl_dump = []
df = None
data_df = None
gdf = None

# functions

def wait():
    now = datetime.now()
    sec = now.second
    if sec != 0:
        time.sleep(60-sec)


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
        logger.info(f'\n\nPositionList: \n {df}')
        logger.info(f'\n\nCombinedPositionsLists: \n {gdf}')
        gl_pnl = round(gdf['pnl'].sum(), 2)
        logger.info(f'\n\nGlobal PnL : {gl_pnl} \n')
        pnl_dump.append([time.strftime("%d-%m-%Y %H:%M:%S"), gl_pnl])
    else:
        gl_pnl = 0


def fetchOHLC(ticker, duration):
    global data_df
    try:
        # symbol = xt.fo_lookup(ticker, instrument_df)
        cur_date = datetime.strftime(datetime.now(), "%b %d %Y")
        nowtime = datetime.now().strftime('%H%M%S')
        ohlc = xt.get_ohlc(exchangeSegment=xt.EXCHANGE_NSEFO,
                        exchangeInstrumentID=ticker,
                        startTime=f'{cur_date} 091500',
                        endTime=f'{cur_date} {nowtime}',
                        compressionValue=duration)
        dataresp= ohlc['result']['dataReponse']
        data = dataresp.split(',')
        data_df = pd.DataFrame([sub.split("|") for sub in data],columns=(['Timestamp','open','high','low','close','volume','oi','na']))
        data_df.drop(data_df.columns[[-1,-2]], axis=1, inplace=True)
        data_df = data_df.astype(dtype={'open': float, 'high': float, 'low': float, 'close': float, 'volume': int})
        data_df['timestamp'] = pd.to_datetime(data_df['Timestamp'].astype('int'), unit='s')
    except Exception:
        logger.exception(f'Error in fetching OHLC for {ticker}')
    return data_df


def vWAP(DF):
    #calculating VWAP and UB , LB values
    df = DF.copy()
    df['vwap'] = (df.volume*(df.high+df.low+df.close)/3).cumsum() / df.volume.cumsum()
    df['uB'] = df.vwap * 1.002
    df['lB'] = df.vwap * 0.998
    return df


def execute(orders):
    global tr_insts, data_df
    tr_insts = []
    etr_inst = {}
    # idx = orders['idx']
    # cur_month = (datetime.strptime(monthly_exp,'%d%b%Y').strftime('%b').upper())
    # fut_symbol = 'BANKNIFTY21'+cur_month+'FUT' if idx == 'NIFTYBANK' else 'NIFTY21'+cur_month+'FUT'
    startTime = datetime.strptime((cdate + " " + orders['startTime']), "%d-%m-%Y %H:%M:%S")
    weekday = datetime.today().weekday()
    while True:
        try:
            # time.sleep(30)
            if startTime >= datetime.now():
                continue
            # logger.info('Time window attained..')
            if orders['status'] == 'Idle' and universal['exit_status'] == 'Idle':
                # data_df = fetchOHLC(fut_symbol, 60)
                df = vWAP(data_df)
                sma_8 = df.rolling(window=8).mean()
                # strike_price = xt.strike_price(orders['idx'])
                logger.info(f"{df['uB'].iloc[-2]} - {sma_8['close'].iloc[-2]}")
                if (df['uB'].iloc[-2] < sma_8['close'].iloc[-2]):
                    logger.info(f'SMA-8 breaks Upper bound of VWAP in {spot}')
                    strike_price = xt.strike_price(orders['idx'])
                    etr_inst['strike'] = strike_price + 300 if weekday != 3 else strike_price + 200
                elif (df['lB'].iloc[-2] > sma_8['close'].iloc[-2]):
                    logger.info(f'SMA-8 breaks Lower bound of VWAP in {spot}')
                    strike_price = xt.strike_price(orders['idx'])
                    etr_inst['strike'] = strike_price - 300 if weekday != 3 else strike_price - 200
                else:
                    continue
                etr_inst['set'] = orders['setno']
                etr_inst['txn_type'] = orders['ent_txn_type']
                # etr_inst['strike'] = strike_price + 300 if weekday != 3 else strike_price + 200
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
                orderID = None
                tradedPrice = None
                logger.info(f'Placing orders for {etr_inst["set"]}. {etr_inst["name"]} at {orders["startTime"]}..')
                if etr_inst['symbol'] != -1:
                    orderID = xt.place_order_id(etr_inst['symbol'], etr_inst['txn_type'], etr_inst['qty'])
                else:
                    logger.error(f'Symbol is not valid: {etr_inst["symbol"]}')
                    raise Exception('Symbol is not valid')
                etr_inst['orderID'] = orderID
                if orderID:
                    tradedPrice, dateTime = xt.get_traded_price(orderID)
                etr_inst['tradedPrice'] = tradedPrice
                etr_inst['dateTime'] = dateTime
                etr_inst['set_type'] = 'Entry'
                if orderID and tradedPrice:
                    etr_inst['status'] = 'Sucess'
                    orders['status'] = 'Entered'
                else:
                    etr_inst['status'] = 'Fail'
                    orders['status'] = 'Entry_Failed'
                logger.info(f'Entry order dtls: {etr_inst}')
                tr_insts.append(etr_inst)
                logger.info(f'order status of {etr_inst["set"]}.{etr_inst["name"]} is {orders["status"]}')
                continue
    
            elif universal['exit_status'] == 'Exited':
                logger.info('Universal exit condition passed. Exiting the loop')
                break
    
            if orders['status'] == 'Entered':
                logger.info(f'Order Success - Order set: {orders["setno"]}. Exiting the thread')
                break
    
            elif orders['status'] == 'Entry_Failed':
                logger.info(f'Exiting todays trade as entry missed. Reason: {orders["status"]}')
                logger.info(f'Order Failed - Order set: {orders["setno"]}. Exiting the thread')
                break
            time.sleep(30)
        except Exception:
            logger.exception(f'API Error in MultiThread - set no: {orders["setno"]}')
            break


def exitCheck(universal):
    global tr_insts
    ext_inst = {}
    exitTime = datetime.strptime((cdate + " " + universal['exitTime']), "%d-%m-%Y %H:%M:%S")
    # print('exitTime:', exitTime)
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
                # ext_inst['orderID'] = None
                # ext_inst['tradedPrice'] = None
                orderID = xt.place_order_id(ext_inst['symbol'], ext_inst['txn_type'], ext_inst['qty'])
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
                    logger.error(f"Error while exiting the order set {orders['setno']}, Exit Immediately")
                logger.info(f'Universal Exit order dtls: {ext_inst}')
                tr_insts.append(ext_inst.copy())
            logger.info('Universal exit func completed. Breaking the main loop')
            universal['exit_status'] = 'Exited'
        else:
            time.sleep(1)


if __name__ == '__main__':
    threads = []
    try:
        instrument_df = xt.master_fo_dump()
        weekly_exp, monthly_exp = xt.get_expiry()
        if not all((isinstance(instrument_df, pd.DataFrame), weekly_exp, monthly_exp)):
            raise Exception('Initial setup failed')
    except Exception as e:
        logger.exception(f'Failed to get masterDump/ expiryDates. Reason --> {e} \n Exiting..')
        exit()
    
    spot = 'BANKNIFTY'
    cur_month = (datetime.strptime(monthly_exp,'%d%b%Y').strftime('%b').upper())
    fut_name = 'BANKNIFTY21'+cur_month+'FUT' if spot == 'BANKNIFTY' else 'NIFTY21'+cur_month+'FUT'
    fut_symbol = xt.fo_lookup(fut_name, instrument_df)
    wait()
    fetchOHLC(fut_symbol, 60)
    fetch_ohlc = RepeatedTimer(59, fetchOHLC, fut_symbol, 60)
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
        fetchLtp.stop()
        fetchPnL.stop()
        fetch_ohlc.stop()
        _ = [t.join() for t in threads]
        time.sleep(5)
        # prints dump to excel
        getGlobalPnL()  # getting latest data
        if isinstance(df, pd.DataFrame):
            data_to_excel(pnl_dump, df, gdf, gl_pnl, script_name, '09:59')
        logger.info('--------------------------------------------')
        logger.info(f'Total Orders and its status: \n {tr_insts} \n')
        logger.info('********** Summary **********')
        logger.info(f'\n\n PositionList: \n {df}')
        logger.info(f'\n\n CombinedPositionsLists: \n {gdf}')
        logger.info(f'\n\n Global PnL : {gl_pnl} \n')
        logger.info('--------------------------------------------')


