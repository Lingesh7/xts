# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 12:46:43 2020

@author: mling
"""

from XTConnect.Connect import XTSConnect
import pandas as pd

# Trading Interactive Creds
API_KEY = "ebaa4a8cf2de358e53c942"
API_SECRET = "Ojre664@S9"

# MarketData Creds
# API_KEY = "ebaa4a8cf2de358e53c942"
# API_SECRET = "Ojre664@S9"

XTS_API_BASE_URL = "https://xts-api.trading"
source = "WEBAPI"
xt = XTSConnect(API_KEY, API_SECRET, source)

response = xt.interactive_login()
# response = xt.marketdata_login()
print("Login: ", response)

orderList=xt.get_order_book()['result']
orderDf = pd.DataFrame(orderList)

tradeList=xt.get_trade()['result']
tradeDf = pd.DataFrame(tradeList)

positionList=xt.get_position_daywise()['result']['positionList']
posDf = pd.DataFrame(positionList)


placed_order = xt.place_order(exchangeSegment=xt.EXCHANGE_NSEFO,
                   exchangeInstrumentID=41379,
                   productType=xt.PRODUCT_MIS, 
                   orderType=xt.ORDER_TYPE_MARKET,                   
                   orderSide=xt.TRANSACTION_TYPE_SELL,
                   timeInForce=xt.VALIDITY_DAY,
                   disclosedQuantity=0,
                   orderQuantity=75,
                   limitPrice=0,
                   stopPrice=0,
                   orderUniqueIdentifier="dec29_2"
                   )
if placed_order['type'] != 'error':
         placed_orderID = placed_order['result']['AppOrderID']
         print("order id market order", placed_orderID)
placed_SL_order= xt.place_order(exchangeSegment=xt.EXCHANGE_NSEFO,
                   exchangeInstrumentID= 41379 ,
                   productType=xt.PRODUCT_MIS, 
                   orderType="StopMarket",                   
                   orderSide=xt.TRANSACTION_TYPE_BUY,
                   timeInForce=xt.VALIDITY_DAY,
                   disclosedQuantity=0,
                   orderQuantity=75,
                   limitPrice=0,
                   stopPrice=78.35+15,
                   orderUniqueIdentifier="dec29_sl_2"
                   )
if placed_SL_order['type'] != 'error':
         placed_SL_orderID = placed_SL_order['result']['AppOrderID']
         print("order id for StopLoss", placed_SL_orderID)

        
sq_off = xt.squareoff_position(
    exchangeSegment=xt.EXCHANGE_NSEFO,
    exchangeInstrumentID=39992,
    productType=xt.PRODUCT_MIS,
    squareoffMode=xt.SQUAREOFF_DAYWISE,
    positionSquareOffQuantityType=xt.SQUAREOFFQUANTITY_PERCENTAGE,
    squareOffQtyValue=100,
    blockOrderSending=True,
    cancelOrders=True)
print("Position Squareoff: ", sq_off)


orderList=xt.get_order_book()['result']
for i in orderList:
    # print(i)
    if i['OrderStatus'] == 'New':
        trgPen = i["AppOrderID"]
        print(trgPen)
        cancel_order = xt.cancel_order(
        appOrderID=trgPen,
        orderUniqueIdentifier='dec29_cancel_1')
        print("Cancel Order: ", cancel_order)

def get_global_PnL():
    # len(xt.get_position_daywise()['result']['positionList'])
    positionList=xt.get_position_daywise()['result']['positionList']
    totalMTM = 0.0
    for i in positionList:
        eachMTM = float(i['MTM'].replace(',', ''))
        #print(type(eachMTM))
        totalMTM += eachMTM
    print(totalMTM)
         



import time
start = time.time()
get_global_PnL()
print(f'Time: {time.time() - start}')

start = time.time()
get_global_PnL_df()
print(f'Time: {time.time() - start}')
    
from datetime import datetime
now = datetime.now()

import schedule
import time

def job():
    print("I'm working...")

schedule.every(10).minutes.do(job)
schedule.every().hour.do(job)
schedule.every().day.at("10:30").do(job)
schedule.every().monday.do(job)
schedule.every().wednesday.at("13:15").do(job)
schedule.every(10).seconds.do(job)
while True:
    schedule.run_pending()
    time.sleep(1)
         
         
schedule.every(5).seconds.do(job)  
schedule.cancel_job(job)

import datetime

def dummy():
    return 1599

cdate = datetime.datetime.strftime(datetime.datetime.now(), "%d-%m-%Y")

check=True
while check:
    if (dummy() > 1500) or (datetime.datetime.now() >= datetime.datetime.strptime(cdate + " 15:00:00", "%d-%m-%Y %H:%M:%S")):
        print('trigger stop loss')
        check=False
    else:
        print('PNL')
        time.sleep(5)


    
positionList= [{'AccountID': 'IIFL24',
    'TradingSymbol': 'NIFTY 24DEC2020 CE 13650',
    'ExchangeSegment': 'NSEFO',
    'ExchangeInstrumentId': '39972',
    'ProductType': 'MIS',
    'Marketlot': '75',
    'Multiplier': '1',
    'BuyAveragePrice': '23.90',
    'SellAveragePrice': '31.80',
    'OpenBuyQuantity': '75',
    'OpenSellQuantity': '75',
    'Quantity': '0',
    'BuyAmount': '1,792.50',
    'SellAmount': '2,385.00',
    'NetAmount': '592.50',
    'UnrealizedMTM': '0.00',
    'RealizedMTM': '592.50', 
    'MTM': '592.50',
    'BEP': '0.00',
    'SumOfTradedQuantityAndPriceBuy': '1,792.50',
    'SumOfTradedQuantityAndPriceSell': '2,385.00',
    'MessageCode': 9002,
    'MessageVersion': 1,
    'TokenID': 0,
    'ApplicationType': 0,
    'SequenceNumber': 307029544564651}]

pos_df = pd.DataFrame(positionList)
for i in range(len(pos_df)):
    symbol = pos_df["ExchangeInstrumentId"].values[i]
    if pos_df["OpenBuyQuantity"].values[i] != pos_df["OpenSellQuantity"].values[i]:
        print("success")
            
    


















