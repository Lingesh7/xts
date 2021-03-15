# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 11:41:46 2021
Flop Strategey on EQ
@author: Welcome
"""
############## imports ##############
from datetime import datetime,date
from dateutil.relativedelta import relativedelta, TH, WE
from XTConnect.Connect import XTSConnect
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
import timer
from threading import Thread
from openpyxl import load_workbook
from logging.handlers import TimedRotatingFileHandler
from sys import exit
import os
import numpy as np

# try:
#     os.chdir(r'D:\Python\First_Choice_Git\xts\strategy\scripts')
# except:
#     pass

############## logging ##############
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

filename='../logs/techTest_testrun_log.txt'

#file_handler = logging.FileHandler(filename)
file_handler = TimedRotatingFileHandler(filename, when='d', interval=1, backupCount=3)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


############## XTS Initialisation ##############
cfg = configparser.ConfigParser()
cfg.read('../../XTConnect/config.ini')
source = cfg['user']['source']
appKey = cfg.get('user', 'interactive_appkey')
secretKey = cfg.get('user', 'interactive_secretkey')
xt = XTSConnect(appKey, secretKey, source)

global cdate
cdate = datetime.strftime(datetime.now(), "%d-%m-%Y")
token_file=f'../scripts/access_token_{cdate}.txt'
file = Path(token_file)
if file.exists() and (date.today() == date.fromtimestamp(file.stat().st_mtime)):
    logger.info('Token file exists and created today')
    in_file = open(token_file,'r').read().split()
    access_token = in_file[0]
    userID=in_file[1]
    isInvestorClient=in_file[2]
    logger.info('Initializing session with token..')
    xt._set_common_variables(access_token, userID, isInvestorClient)
else:
    logger.error('Wrong with token file. Generate separately.. Aborting script!..')
    exit()

################ variables ###############
ticker = 'HDFCBANK'
refid=1
flop=[]
mark=[]
tr_insts = []
etr_inst = {}
################ functions ###############
def masterEqDump():
    global instrument_df
    filename=f'../ohlc/NSE_EQ_Instruments_{cdate}.csv'
    file = Path(filename)
    if file.exists() and (date.today() == date.fromtimestamp(file.stat().st_mtime)):
        logger.info('MasterDump already exists.. reading directly')
        instrument_df=pd.read_csv(filename,header='infer')
    else:
        logger.info('Creating MasterDump..')
        exchangesegments = [xt.EXCHANGE_NSECM]
        mastr_resp = xt.get_master(exchangeSegmentList=exchangesegments)
        # print("Master: " + str(mastr_resp))
        master=mastr_resp['result']
        spl=master.split('\n')
        mstr_df = pd.DataFrame([sub.split("|") for sub in spl],columns=(['ExchangeSegment','ExchangeInstrumentID','InstrumentType','Name','Description','Series','NameWithSeries','InstrumentID','PriceBand.High','PriceBand.Low','FreezeQty','TickSize',' LotSize']))
        instrument_df = mstr_df[mstr_df.Series == 'EQ']
        instrument_df.to_csv(f"../ohlc/NSE_EQ_Instruments_{cdate}.csv",index=False)        
            
def instrumentLookup(instrument_df,ticker):
    """Looks up instrument token for a given script from instrument dump"""
    try:
        return instrument_df[instrument_df.Name==ticker].ExchangeInstrumentID.values[0]
    except:
        return -1

def fetchOHLC(ticker,duration):
    symbol = instrumentLookup(instrument_df,ticker)
    cur_date = datetime.strftime(datetime.now(), "%b %d %Y")
    nowtime = datetime.now().strftime('%H%M%S')
    ohlc = xt.get_ohlc(exchangeSegment=xt.EXCHANGE_NSECM,
                    exchangeInstrumentID=symbol,
                    startTime=f'{cur_date} 091500',
                    endTime=f'{cur_date} {nowtime}',
                    compressionValue=duration)
    dataresp= ohlc['result']['dataReponse']
    data = dataresp.split(',')
    data_df = pd.DataFrame([sub.split("|") for sub in data],columns=(['Timestamp','Open','High','Low','Close','Volume','OI','NA']))
    data_df.drop(data_df.columns[[-1,-2]], axis=1, inplace=True)
    data_df = data_df.astype(dtype={'Open': float, 'High': float, 'Low': float, 'Close': float, 'Volume': int})
    data_df['Timestamp'] = pd.to_datetime(data_df['Timestamp'].astype('int'), unit='s')
    return data_df

def vWAP(DF):
    #calculating VWAP and UB , LB values
    df = DF.copy()
    df['vwap'] = (df.Volume*(df.High+df.Low+df.Close)/3).cumsum() / df.Volume.cumsum()
    df['uB'] = df.vwap * 1.002
    df['lB'] = df.vwap * 0.998
    return df
    
def getOrderList():
    aa = 0
    logger.info('Checking OrderBook for order status..') 
    while aa < 5:
        try:
           oBook_resp = xt.get_order_book()
           if oBook_resp['type'] != "error":
               orderList =  oBook_resp['result']
               # logger.info('OrderBook result retreived success')
               return orderList
               break
           else:
               raise Exception("Unkonwn error in getOrderList func")           
        except Exception:
            logger.exception("Can't extract order data..retrying")
            # traceback.print_exc()
            time.sleep(2)
            aa+=1
                   
def cancelOrder(OrderID):
    logger.info(f'Cancelling order: {OrderID} ')
    cancel_resp = xt.cancel_order(
        appOrderID=OrderID,
        orderUniqueIdentifier='FC_Cancel_Orders_1') 
    if cancel_resp['type'] != 'error':
        cancelled_SL_orderID = cancel_resp['result']['AppOrderID']
        logger.info(f'Cancelled SL order id : {cancelled_SL_orderID}')
    if cancel_resp['type'] == 'error':
        logger.error(f'Cancel order not processed for : {OrderID}')

def placeOrder(symbol,txn_type,qty):
    logger.info('Placing Orders..')
    # Place an intraday stop loss order on NSE
    if txn_type == "buy":
        t_type=xt.TRANSACTION_TYPE_BUY
    elif txn_type == "sell":
        t_type=xt.TRANSACTION_TYPE_SELL
    try:
        order_resp = xt.place_order(exchangeSegment=xt.EXCHANGE_NSEFO,
                         exchangeInstrumentID= symbol ,
                         productType=xt.PRODUCT_MIS, 
                         orderType=xt.ORDER_TYPE_MARKET,                   
                         orderSide=t_type,
                         timeInForce=xt.VALIDITY_DAY,
                         disclosedQuantity=0,
                         orderQuantity=qty,
                         limitPrice=0,
                         stopPrice=0,
                         orderUniqueIdentifier="FC_MarketOrder"
                         )
        if order_resp['type'] != 'error':
            orderID = order_resp['result']['AppOrderID']            #extracting the order id from response
            logger.info(f'Order ID for {t_type} {symbol} is: {orderID}')
            time.sleep(2)
            a=0
            while a<12:
                orderLists = getOrderList()
                if orderLists:
                    new_orders = [ol for ol in orderLists if ol['AppOrderID'] == orderID and ol['OrderStatus'] != 'Filled']  
                    if not new_orders:
                        tradedPrice = float(next((orderList['OrderAverageTradedPrice'] \
                                            for orderList in orderLists \
                                                if orderList['AppOrderID'] == orderID and \
                                                    orderList['OrderStatus'] == 'Filled'),None).replace(',', ''))
                        LastUpdateDateTime=datetime.fromisoformat(next((orderList['LastUpdateDateTime'] for orderList in orderLists if orderList['AppOrderID'] == orderID and orderList['OrderStatus'] == 'Filled'))[0:19])
                        dateTime = LastUpdateDateTime.strftime("%Y-%m-%d %H:%M:%S")
                        logger.info(f"traded price is: {tradedPrice} and ordered  time is: {dateTime}")
                        return orderID, tradedPrice, dateTime
                        break
                        # loop = False
                    else:
                        logger.info(f' Placed order {orderID} might be in Open or New Status, Hence retrying..{a}')
                        a+=1
                        time.sleep(2.5)
                        if a==11:
                            logger.info('Placed order is still in New or Open Status..Hence Cancelling the placed order')
                            cancelOrder(orderID)
                            return None, None, None
                            break
                else:
                    logger.info('\n  Unable to get OrderList inside place order function..')
                    logger.info('..Hence traded price will retun as Zero \n ')
        elif order_resp['type'] == 'error':
            logger.error(order_resp['description'])
            logger.info(f'Order not placed for - {symbol} ')
            raise Exception('Order not placed - ')
    except Exception():
        raise ex.XTSOrderException('Unable to place order in placeOrder func...')
        logger.exception('Unable to place order in placeOrder func...')
        time.sleep(1)

def main(capital):
    global refid, flop, mark

    logger.info(f"Checking for..{ticker} at {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    try:
        data_df = fetchOHLC(ticker, 60)
        df = vWAP(data_df)
        logger.info(f"tick {df['Timestamp'].iloc[-2]}")
        quantity = int(capital/df["Close"].iloc[-1])
        if pd.Timestamp(df['Timestamp'].iloc[-1]) >= pd.Timestamp(cdate+" "+'09:30:00'):
            idx = len(flop)-1
            if df['Close'].iloc[-2] >= df['uB'].iloc[-2] :
                logger.info('Upper bound break..')
                # print('Long', df['Timestamp'].values[i])
                if not flop:
                    flop.append('Long')
                    mark.append({'refid':refid, 'side': 'Long', 'time': df['Timestamp'].iloc[-2], 'price': df['Close'].iloc[-2]})
                    refid += 1
                    logger.info(flop)
                    logger.info(mark)
                elif flop[-1] != 'Long':
                    lowPriceAfterFlop = df[df.Timestamp.between(mark[idx]['time'],df['Timestamp'].values[-2])]['Close'].min()
                    if (mark[idx]['price'] - lowPriceAfterFlop) < (mark[idx]['price'] * (0.5/100)):
                        flop.append('Long')
                        mark.append({'set':refid, 'side': 'Long', 'time': df['Timestamp'].values[-2], 'price': df['Close'].values[-2]})
                        refid += 1
                        logger.info(flop)
                        logger.info(mark)
                        if len(flop) >= 3:
                            logger.info('===================')
                            logger.info('placing Buy order')
                            logger.info('===================')
                            # placeOrder()
                            etr_inst['txn_type'] = 'BUY'
                            etr_inst['qty'] = quantity
                            etr_inst['tr_qty'] = quantity
                            etr_inst['name'] = ticker
                            etr_inst['symbol'] = ticker #todo symbol should be calculated here
                            etr_inst['orderID'] = None
                            etr_inst['tradedPrice'] = None
                            orderID, tradedPrice, dateTime = placeOrder(ticker, 'buy', quantity)
                            etr_inst['orderID'] = orderID
                            etr_inst['tradedPrice'] = tradedPrice
                            etr_inst['dateTime'] = dateTime
                            if orderID and tradedPrice:
                                tr_insts.append(etr_inst)
                    else:
                        logger.info('Previous break is not a flop.. strting from begining')
                        flop=[]
                        mark=[]
               
            if df['Close'].values[-2] <= df['lB'].values[-2]:
                idx = len(flop)-1
                if not flop:
                    flop.append('Short')
                    mark.append({'set':refid, 'side': 'Short', 'time': df['Timestamp'].values[-2], 'price': df['Close'].values[-2]})
                    refid += 1
                    logger.info(flop)
                    logger.info(mark)
                elif flop[-1] != 'Short':
                    highPriceAfterFlop = df[df.Timestamp.between(mark[idx]['time'],df['Timestamp'].values[-2])]['High'].max()
                    if ( highPriceAfterFlop - mark[idx]['price']) < (mark[idx]['price'] * (0.5/100)):
                        flop.append('Short')
                        mark.append({'set':refid, 'side': 'Short', 'time': df['Timestamp'].values[-2], 'price': df['Close'].values[-2]})
                        refid += 1
                        logger.info(flop)
                        logger.info(mark)
                        if len(flop) >= 3:
                            logger.info('===================')
                            logger.info('placing Sell order')
                            logger.info('===================')
                            # placeOrder()
                            placeOrder(ticker, 'sell', quantity)
                    else:
                        flop=[]
                        mark=[]
    except:
        logger.info("API error for ticker :",ticker)

if __name__ == '__main__':
    masterEqDump()
    startin=time.time()
    timeout = time.time() + 60*60*1  # 60 seconds times 360 meaning 6 hrs
    while time.time() <= timeout:
        try:
            main()
            time.sleep(60 - ((time.time() - startin) % 60.0))
        except KeyboardInterrupt:
            print('\n\nKeyboard exception received. Exiting.')
            exit()
    
# AUROPHARMA
# AXIS BANK
# BPCL
# BANDHANBNK
# BAJFINANCE
# DLF
# HINDALCO
# IBULHSGFIN
# INDUSINDBK
# ICICIBANK
# INDIGO
# JINDALSTEL
# L&TFH
# LICHSGFIN
# MANAPPURAM
# MARUTI
# RBLBANK
# SBIN
# TATAMOTORS
# TATASTEEL
# VEDL

