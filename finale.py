# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 17:11:25 2020
Proper lineup
@author: mling
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta, TH
from XTConnect.Connect import XTSConnect
import time
import pandas as pd
from sys import exit

# Trading Interactive Creds
API_KEY = "ebaa4a8cf2de358e53c942"
API_SECRET = "Ojre664@S9"

# MarketData Creds
# API_KEY = "ebaa4a8cf2de358e53c942"
# API_SECRET = "Ojre664@S9"

XTS_API_BASE_URL = "https://xts-api.trading"
source = "WEBAPI"
xt = XTSConnect(API_KEY, API_SECRET, source)
login_resp = xt.interactive_login()

def nextThu_and_lastThu_expiry_date ():

    todayte = datetime.today()
    
    cmon = todayte.month
    if_month_next=(todayte + relativedelta(weekday=TH(1))).month
    next_thursday_expiry=todayte + relativedelta(weekday=TH(1))
   
    if (if_month_next!=cmon):
        month_last_thu_expiry= todayte + relativedelta(weekday=TH(5))
        if (month_last_thu_expiry.month!=if_month_next):
            month_last_thu_expiry= todayte + relativedelta(weekday=TH(4))
    else:
        for i in range(1, 7):
            t = todayte + relativedelta(weekday=TH(i))
            if t.month != cmon:
                # since t is exceeded we need last one  which we can get by subtracting -2 since it is already a Thursday.
                t = t + relativedelta(weekday=TH(-2))
                month_last_thu_expiry=t
                break
    str_month_last_thu_expiry=str(int(month_last_thu_expiry.strftime("%d")))+month_last_thu_expiry.strftime("%b").capitalize()+month_last_thu_expiry.strftime("%Y")
    str_next_thursday_expiry=str(int(next_thursday_expiry.strftime("%d")))+next_thursday_expiry.strftime("%b").capitalize()+next_thursday_expiry.strftime("%Y")
    return (str_next_thursday_expiry,str_month_last_thu_expiry)


def get_eID(symbol,ce_pe,expiry):
    nfty_ltp = nse.get_index_quote("nifty 50")['lastPrice']
    bnknfty_ltp = nse.get_index_quote("nifty bank")['lastPrice']

    print("Current nifty price is:", nfty_ltp)
    print("Current BankNifty price is:", bnknfty_ltp)
    if ce_pe == "ce":
        oType="CE"
    elif ce_pe == "pe":
        oType="PE"
    if symbol == "NIFTY":
        strikePrice= strkPrcCalc(nfty_ltp,50)
    elif symbol == "BANKNIFTY":
        strikePrice= strkPrcCalc(bnknfty_ltp,100)
    print("strike Price calculated as :", strikePrice)
    print("expiry date caluclated as :", expiry)
    response = xt.get_option_symbol(
    exchangeSegment=2,
    series='OPTIDX',
    symbol=symbol,
    expiryDate=expiry,
    optionType=oType,
    strikePrice=strikePrice)
    #print('Option Symbol:', str(response))
    #print("ExchangeInstrumentID is:",response)# (int(response["result"][0]["ExchangeInstrumentID"])))
    return int(response["result"][0]["ExchangeInstrumentID"])


def placeSLOrder(symbol,buy_sell,quantity):  
    # Place an intraday stop loss order on NSE
    if buy_sell == "buy":
        t_type=xt.TRANSACTION_TYPE_BUY
        t_type_sl=xt.TRANSACTION_TYPE_SELL
    elif buy_sell == "sell":
        t_type=xt.TRANSACTION_TYPE_SELL
        t_type_sl=xt.TRANSACTION_TYPE_BUY
    # quantity = mul*nifty_lot_size
    order_resp = xt.place_order(exchangeSegment=xt.EXCHANGE_NSEFO,
                   exchangeInstrumentID= symbol ,
                   productType=xt.PRODUCT_MIS, 
                   orderType=xt.ORDER_TYPE_MARKET,                   
                   orderSide=t_type,
                   timeInForce=xt.VALIDITY_DAY,
                   disclosedQuantity=0,
                   orderQuantity=quantity,
                   limitPrice=0,
                   stopPrice=0,
                   orderUniqueIdentifier="pl_test5"
                   )
    if order_resp['type'] != 'error':
         orderID = order_resp['result']['AppOrderID']
         print(f''' Order ID for [t_type] {symbol} is: ", {orderID}''')
    if order_resp['type'] == 'error':
            print("Error placing Order.. try Again")
            exit()
    time.sleep(5)
    stopPrice = 0
    
    orderBook = xt.get_order_book()
    
    stopPrice = 0
    orderList = [{'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10026366, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31389582', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 39992, 'OrderSide': 'Buy', 'OrderType': 'StopMarket', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 269.3, 'OrderStatus': 'Cancelled', 'OrderAverageTradedPrice': '', 'LeavesQuantity': 75, 'CumulativeQuantity': 0, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-29T13:13:54.0517821', 'ExchangeTransactTime': '2020-12-29T15:05:57+05:30', 'LastUpdateDateTime': '2020-12-29T15:05:57.3474221', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'dec29_sl_1', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 313939350474164}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 20030735, 'OrderReferenceID': '', 'GeneratedBy': 'TWS', 'ExchangeOrderID': 'X_31389805', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 39992, 'OrderSide': 'Buy', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '208.75', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-29T14:56:31.871326', 'ExchangeTransactTime': '2020-12-29T14:56:32+05:30', 'LastUpdateDateTime': '2020-12-29T14:56:32.1253445', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': '', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 313939350474163}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10026385, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31389601', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41379, 'OrderSide': 'Buy', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 93.35, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '95.45', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-29T13:28:09.5274879', 'ExchangeTransactTime': '2020-12-29T13:50:59+05:30', 'LastUpdateDateTime': '2020-12-29T13:50:59.2861998', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'dec29_sl_2', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 313939350474162}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10026383, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31389599', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41379, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '78.35', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-29T13:26:41.0961354', 'ExchangeTransactTime': '2020-12-29T13:26:41+05:30', 'LastUpdateDateTime': '2020-12-29T13:26:41.9091972', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'dec29_2', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 313939350474161}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10026364, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31389580', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 39992, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '219.30', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-29T13:12:36.8657664', 'ExchangeTransactTime': '2020-12-29T13:12:37+05:30', 'LastUpdateDateTime': '2020-12-29T13:12:37.5668251', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'dec29_1', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 313939350474160}]
    orderID = 10026366
    # orderList = orderBook["result"]
    for i in orderList:
        if orderID == i["AppOrderID"] and i["OrderStatus"] == 'Filled':
            stopPrice = float(( i["OrderAverageTradedPrice"]))
            
            
            
            else:
            print(":::Not booked SL order:::", i["OrderStatus"])
            
            
            
            
    

def main(ticker):
    
    for oType in "ce","pe":
        weekly_exp,monthly_exp = nextThu_and_lastThu_expiry_date()
        #expiry = get_expiry_from_option_chain(ticker)
        # weekly_exp,monthly_exp=(expiry[:2])
        if ticker == "NIFTY":
             quantity = 75
        if ticker == "BANKNIFTY":
            quantity = 25
        eID = get_eID(ticker,oType,weekly_exp)
        placeSLOrder(eID,'sell',quantity)
        






#############################################################################################################
#############################################################################################################
tickers = ["NIFTY"] 
#tickers to track - recommended to use max movers from previous day
capital = 3000 #position size
st_dir = {} #directory to store super trend status for each ticker

for ticker in tickers:
    st_dir[ticker] = ["None","None","None"]    
    
starttime=time.time()
timeout = time.time() + 60*60*1  # 60 seconds times 360 meaning 6 hrs
while time.time() <= timeout:
    try:
        main(capital)
        time.sleep(300 - ((time.time() - starttime) % 300.0))
    except KeyboardInterrupt:
        print('\n\nKeyboard exception received. Exiting.')
        exit()        
