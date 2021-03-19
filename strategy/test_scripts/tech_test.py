# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 11:41:46 2021

@author: Welcome
"""

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

try:
    os.chdir(r'D:\Python\First_Choice_Git\xts\strategy\scripts')
except:
    pass

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

filename='../logs/techTest_log.txt'

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

################ functions ###############

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
    
nowtime= datetime.now().strftime('%H%M%S')




ohlc=xt.get_ohlc(exchangeSegment=xt.EXCHANGE_NSECM,
                    exchangeInstrumentID=1333,
                    startTime='Mar 15 2021 091500',
                    endTime=f'Mar 15 2021 {nowtime}',
                    compressionValue=60)

dataresp = ohlc['result']['dataReponse']
spl = dataresp.split(',')
spl_df = pd.DataFrame([sub.split("|") for sub in spl],columns=(['Timestamp','Open','High','Low','Close','Volume','OI','NA']))
spl_df.drop(spl_df.columns[[-1,-2]], axis=1, inplace=True)

# spl_df = pd.read_excel('hdfs_12Mar2021.xlsx')
# spl_df = pd.read_excel('SBI_04Mar2021.xlsx')
# spl_df = pd.read_excel('INFY_01Mar2021.xlsx')

spl_df = spl_df.astype(dtype={'Open': float, 'High': float, 'Low': float, 'Close': float, 'Volume': int})
spl_df['Timestamp'] = pd.to_datetime(spl_df['Timestamp'].astype('int'), unit='s')
df = spl_df.copy()
# df1 = df1.set_index(['Timestamp'])
# df1.index = pd.to_datetime(df1.index, format='%d-%m-%Y %H:%M:%S')
# df = pd.DataFrame()

# df['Open'] = df1['Open'].resample('5min').first()
# df['High'] = df1['High'].resample('5min').max()
# df['Low'] = df1['Low'].resample('5min').min()
# df['Close'] = df1['Close'].resample('5min').last()
# df['Volume'] = df1['Volume'].resample('5min').sum()
# df.reset_index(inplace=True)

df['vwap'] = (df.Volume*(df.High+df.Low+df.Close)/3).cumsum() / df.Volume.cumsum()
df['uB'] = df.vwap * 1.002
df['lB'] = df.vwap * 0.998

startTime = datetime.strptime(('15-03-2021 09:30:00' ),"%d-%m-%Y %H:%M:%S")
startTime = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
flop=[]
mark=[]


def fetchOHLC(ticker,duration):
    # symbol = instrumentLookup(instrument_df,ticker)
    cur_date = datetime.strftime(datetime.now(), "%b %d %Y")
    nowtime = datetime.now().strftime('%H%M%S')
    ohlc = xt.get_ohlc(exchangeSegment=xt.EXCHANGE_NSECM,
                    exchangeInstrumentID=ticker,
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

new_df = fetchOHLC(1333,60)
df1 = vWAP(new_df)

if pd.Timestamp(df['Timestamp'].values[i]) >= pd.Timestamp(startTime):
    # print(f'Length of flop is: {len(flop)}')
    idx = len(flop)-1
    if df['Close'].iloc[-1] >= df['uB'].iloc[-1] :
            
         # print('Long', df['Timestamp'].values[i])
         if not flop:
             flop.append('Long')
             mark.append({'set':1, 'side': 'Long', 
                              'time': df['Timestamp'].values[i],
                                 'price': df['Close'].values[i]})
             print(flop)
             print(mark)
         elif flop[-1] != 'Long':
             lowPriceAfterFlop = df[df.Timestamp.between(mark[idx]['time'],df['Timestamp'].values[i])]['Close'].min()
             if (mark[idx]['price'] - lowPriceAfterFlop) < (mark[idx]['price'] * (0.5/100)):
                 flop.append('Long')
                 mark.append({'set':2, 'side': 'Long', 
                              'time': df['Timestamp'].values[i],
                                 'price': df['Close'].values[i]})
                 print(flop)
                 print(mark)
                 
                 if len(flop) >= 3:
                     print('placing Buy order')
                     placeOrder()
                     
             else:
                 flop=[]
                 mark=[]
        
     if df['Close'].values[i] <= df['lB'].values[i]:
         # print('Short', df['Timestamp'].values[i])
         # print(f'Length of flop is: {len(flop)}')
         idx = len(flop)-1
         if not flop:
             flop.append('Short')
             mark.append({'set':1, 'side': 'Short', 
                              'time': df['Timestamp'].values[i],
                                 'price': df['Close'].values[i]})
             print(flop)
             print(mark)
         elif flop[-1] != 'Short':
             highPriceAfterFlop = df[df.Timestamp.between(mark[idx]['time'],df['Timestamp'].values[i])]['High'].max()
             if ( highPriceAfterFlop - mark[idx]['price']) < (mark[idx]['price'] * (0.5/100)):
                 flop.append('Short')
                 mark.append({'set':2, 'side': 'Short', 
                              'time': df['Timestamp'].values[i],
                                 'price': df['Close'].values[i]})
                 print(flop)
                 print(mark)
                 if len(flop) >= 3:
                     print('placing Sell order')
             else:
                 flop=[]
                 mark=[]
     time.sleep(0.5)
    
    
    
import time
# import schedule
import requests
userids = ['1245301878','1647735620']
#https://api.telegram.org/bot1635591509:AAFC3kNVnTONZ1NU4JJx_kqfFfCoJEoEJ50/getUpdates
def telegram_bot_sendtext(bot_message,userids):
    for i in userids:
        bot_token = '1635591509:AAFC3kNVnTONZ1NU4JJx_kqfFfCoJEoEJ50'
        bot_chatID = i
        send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    
        response = requests.get(send_text)
    
    return response.json()


def report():
    # my_balance = 10   ## Replace this number with an API call to fetch your account balance
    my_message = "2nd message"   ## Customize your message
    telegram_bot_sendtext(my_message,userids)


report()   
# schedule.every().day.at("12:00").do(report)

# while True:
#     schedule.run_pending()
#     time.sleep(1)