# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 12:46:43 2020

@author: mling
"""
import pandas as pd
from XTConnect import XTSConnect
from datetime import datetime
from dateutil.relativedelta import relativedelta, TH


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

"""Get Balance Request"""
response = xt.get_balance()
balanceList = xt.get_balance()['result']['BalanceList']

def checkBalance():
    a = 0
    while a < 10:
        try:
           bal_resp = xt.get_balance()
           break
        except:
            print("can't extract position data..retrying")
            a+=1
    if bal_resp['type'] != 'error':
         balanceList = bal_resp['result']['BalanceList']
         cashAvailable = balanceList[0]['limitObject']['marginAvailable']['CashMarginAvailable']
         print("Balance Available is: ", cashAvailable)
    else:
        print(bal_resp['description'])
        print("Unable to fetch Cash margins... try again..")
    return cashAvailable

from datetime import datetime
from dateutil.relativedelta import relativedelta, TH

def nextThu_and_lastThu_expiry_date ():
    global weekly_exp, monthly_exp
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
    monthly_exp=str((month_last_thu_expiry.strftime("%d")))+month_last_thu_expiry.strftime("%b").capitalize()+month_last_thu_expiry.strftime("%Y")
    weekly_exp=str((next_thursday_expiry.strftime("%d")))+next_thursday_expiry.strftime("%b").capitalize()+next_thursday_expiry.strftime("%Y")
 
    
 
tickers = ["NIFTY"] 
for ticker in tickers:
    # for oType in "ce","pe":
    weekly_exp,monthly_exp = nextThu_and_lastThu_expiry_date()
    #expiry = get_expiry_from_option_chain(ticker)
    # weekly_exp,monthly_exp=(expiry[:2])
    if ticker == "NIFTY":
         quantity = 75
         nfty_ltp = nse.get_index_quote("nifty 50")['lastPrice']
         strikePrice = strkPrcCalc(nfty_ltp,50)
    if ticker == "BANKNIFTY":
        quantity = 25
        bnknfty_ltp = nse.get_index_quote("nifty bank")['lastPrice']
        strikePrice = strkPrcCalc(bnknfty_ltp,100)
eID = get_eID(ticker,oType,weekly_exp,strikePrice)



a = 0
while a < 10:
    try:
       bal_resp = xt.get_balance()
       break
    except:
        print("can't extract position data..retrying")
        a+=1




placed_order = xt.place_order(exchangeSegment=xt.EXCHANGE_NSECM,
                   exchangeInstrumentID=22,
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
def getOrderList():
    aa = 0
    while aa < 10:
        try:
           orderBook_resp = xt.get_order_book()
           orderList =  orderBook_resp['result'] 
           return orderList
           break
        except:
            print("can't extract position data..retrying")
            aa+=1


start = time.time()
getOrderList()
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

#################
from threading import Timer

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
        
from time import sleep


    

    
def printPNL(name):
    print("PNL")
    
print("starting...")
rt1 = RepeatedTimer(2, strategy, "strategy") # it auto-starts, no need of rt.start()
rt2 = RepeatedTimer(10, printPNL, "printPNL")
try:
    print("sqOff started")
    squareOff(" in sqoff")
    sleep(20) # your long-running job goes here...
    print("squareoff completed")
finally:
    print("finally block")
    rt1.stop() # better in a try/finally block to make sure the program ends!
    rt2.stop()
    print("stopped all")







import threading 
import time
  
def print_hello():
  for i in range(4):
    time.sleep(0.5)
    print("Hello")
  
def print_hi(): 
    for i in range(4): 
      time.sleep(0.7)
      print("Hi") 

t1 = threading.Thread(target=print_hello)  
t2 = threading.Thread(target=print_hi)  
t1.start()
t2.start()

# d1 = { 'CE' :58346 , 'PE' : 58349 }


import datetime

def dummy():
    return 1498

from datetime import datetime
import time

cdate = datetime.strftime(datetime.now(), "%d-%m-%Y")
check=True
m=0
bag=[]
while check:
    if (dummy() > 1500) or (datetime.now() >= datetime.strptime(cdate + " 23:00:00", "%d-%m-%Y %H:%M:%S")):
        print('trigger stop loss')
        check=False
    else:
        data = time.strftime("%d-%m-%Y %H:%M:%S"),",",dummy()
        # print(data)
        bag.append(data) 
        m+=1
        if len(bag) >= 5:
            tup=bag[-1]
            bagstr=" ".join(str(x) for x in tup)
            print(bagstr)
            bag = []
            m=0
        # print(m,len(bag))
        time.sleep(2)



type([data])

print(time.strftime("%d-%m-%Y %H:%M:%S"))
    
positionList= [{'AccountID': 'IIFL24', 'TradingSymbol': 'NIFTY 31DEC2020 CE 13900', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentId': '41376', 'ProductType': 'MIS', 'Marketlot': '75', 'Multiplier': '1', 'BuyAveragePrice': '0.00', 'SellAveragePrice': '82.70', 'OpenBuyQuantity': '0', 'OpenSellQuantity': '75', 'Quantity': '-75', 'BuyAmount': '0.00', 'SellAmount': '6,202.50', 'NetAmount': '6,202.50', 'UnrealizedMTM': '1,485.00', 'RealizedMTM': '0.00', 'MTM': '1,485.00', 'BEP': '82.70', 'SumOfTradedQuantityAndPriceBuy': '0.00', 'SumOfTradedQuantityAndPriceSell': '6,202.50', 'MessageCode': 9002, 'MessageVersion': 1, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227723717}, {'AccountID': 'IIFL24', 'TradingSymbol': 'NIFTY 31DEC2020 PE 13900', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentId': '41377', 'ProductType': 'MIS', 'Marketlot': '75', 'Multiplier': '1', 'BuyAveragePrice': '72.35', 'SellAveragePrice': '57.10', 'OpenBuyQuantity': '75', 'OpenSellQuantity': '75', 'Quantity': '75', 'BuyAmount': '5,426.25', 'SellAmount': '4,282.50', 'NetAmount': '-1,143.75', 'UnrealizedMTM': '0.00', 'RealizedMTM': '-1,143.75', 'MTM': '-1,143.75', 'BEP': '0.00', 'SumOfTradedQuantityAndPriceBuy': '5,426.25', 'SumOfTradedQuantityAndPriceSell': '4,282.50', 'MessageCode': 9002, 'MessageVersion': 1, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227723718}]
pos_df = pd.DataFrame(positionList)
for i in range(len(pos_df)):
    if int(pos_df["Quantity"].values[i]) != 0:
        symbol = pos_df["ExchangeInstrumentId"].values[i]
        print(symbol)
        
boo = int(pos_df["Quantity"].values[1])
a = pos_df["TradingSymbol"].values[0]
type(a)    
        

orderList = [{'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 20030623, 'OrderReferenceID': '', 'GeneratedBy': 'TWS', 'ExchangeOrderID': 'X_31475561', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Buy', 'OrderType': 'StopMarket', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'New', 'OrderAverageTradedPrice': '88.45', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T13:50:53.7042412', 'ExchangeTransactTime': '2020-12-30T13:50:54+05:30', 'LastUpdateDateTime': '2020-12-30T13:50:54.0682695', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': '', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762024}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025789, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475408', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41377, 'OrderSide': 'Buy', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 72.1, 'OrderStatus': 'Open', 'OrderAverageTradedPrice': '72.35', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:46.3067796', 'ExchangeTransactTime': '2020-12-30T12:39:39+05:30', 'LastUpdateDateTime': '2020-12-30T12:39:39.0228247', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice1', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762023}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025788, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475407', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41377, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '57.10', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:41.1823828', 'ExchangeTransactTime': '2020-12-30T12:21:41+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:41.8754364', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice0', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762022}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025787, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475406', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Buy', 'OrderType': 'StopMarket', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 97.7, 'OrderStatus': 'New', 'OrderAverageTradedPrice': '', 'LeavesQuantity': 75, 'CumulativeQuantity': 0, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:38.7891996', 'ExchangeTransactTime': '2020-12-30T12:21:38+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:38.7901995', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice1', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762011}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025786, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475405', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '82.70', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:33.377785', 'ExchangeTransactTime': '2020-12-30T12:21:33+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:33.7418131', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice0', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762021}]
ord_df = pd.DataFrame(orderList)
pending = ord_df[ord_df['OrderStatus'].isin(["New","Open","Partially Filled"])]["AppOrderID"].tolist()

drop = []
attempt = 0
len(pending)

while len(pending)>0 and attempt<5:
    pending = [j for j in pending if j not in drop]
    for order in pending:
        try:
            print(order)
            drop.append(order)
            
        except:
            print("unable to print order id : ",order)
            attempt+=1






# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from collections import defaultdict

ordersEid = {39308: 'CE', 39309: 'PE'}
orderID_dictR = {39309: [10026148, 39309, 10026150], 39308: [10026147, 39308, 10026149]}
dd = defaultdict(list)

for d in (ordersEid, orderID_dictR): 
    for key, value in d.items():
        dd[key].append(value)
oIDs={}
for k,v in dd.items():
    i = iter(v)
    b = dict(zip(i, i))
    oIDs.update(b)              
print(oIDs)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# from nsetools import Nse
# nse = Nse()
import pandas as pd
from XTConnect import XTSConnect
import time
from threading import Timer

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
        
        

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


def cancelOrder(order):
    print("cancelled", order)

def get_eID(symbol,ce_pe,expiry,strikePrice):
    if ce_pe == "ce":
        oType="CE"
    elif ce_pe == "pe":
        oType="PE"
    print("New strikePrice caluclated as :", strikePrice)
    eID_resp = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol=symbol,
                expiryDate=expiry,
                optionType=oType,
                strikePrice=strikePrice)
    #print('Option Symbol:', str(response))
    # print("ExchangeInstrumentID is:",eID_resp)# (int(response["result"][0]["ExchangeInstrumentID"])))
    eid = int(eID_resp["result"][0]["ExchangeInstrumentID"])
    
    # ordersEid[eid]=(oType)
    # return int(eID_resp["result"][0]["ExchangeInstrumentID"])
    return eid

def placeOrder(symbol,buy_sell,quantity):
    # Place an intraday stop loss order on NSE
    if buy_sell == "buy":
        t_type=xt.TRANSACTION_TYPE_BUY
        
    elif buy_sell == "sell":
        t_type=xt.TRANSACTION_TYPE_SELL
        # quantity = mul*nifty_lot_size
    bb = 0
    while bb < 10:
        try:
            print('placing order for --', symbol)
            print(f'''order_resp = xt.place_order(exchangeSegment=xt.EXCHANGE_NSEFO,
                         exchangeInstrumentID= {symbol} ,
                         productType=xt.PRODUCT_MIS, 
                         orderType=xt.ORDER_TYPE_MARKET,                   
                         orderSide={t_type},
                         timeInForce=xt.VALIDITY_DAY,
                         disclosedQuantity=0,
                         orderQuantity={quantity},
                         limitPrice=0,
                         stopPrice=0,
                         orderUniqueIdentifier="FirstChoice_repairOrder"
                         ''')
            break
        except:
            print("Unable to place repair order... retrying")
            bb+=1

# def squareOff(ids,symbol):
    print("squaredOff : ",ids, symbol )


from operator import add,sub

def runRepairActions(c_p):
    # if curPrc > nfty_ltp+40:
    print(" -- symbol goes +/- 40 -- ")
    positionList = [{'AccountID': 'IIFL24', 'TradingSymbol': 'NIFTY 31DEC2020 CE 13900', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentId': '39308', 'ProductType': 'MIS', 'Marketlot': '75', 'Multiplier': '1', 'BuyAveragePrice': '0.00', 'SellAveragePrice': '82.70', 'OpenBuyQuantity': '0', 'OpenSellQuantity': '75', 'Quantity': '-75', 'BuyAmount': '0.00', 'SellAmount': '6,202.50', 'NetAmount': '6,202.50', 'UnrealizedMTM': '1,485.00', 'RealizedMTM': '0.00', 'MTM': '1,485.00', 'BEP': '82.70', 'SumOfTradedQuantityAndPriceBuy': '0.00', 'SumOfTradedQuantityAndPriceSell': '6,202.50', 'MessageCode': 9002, 'MessageVersion': 1, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227723717}, {'AccountID': 'IIFL24', 'TradingSymbol': 'NIFTY 31DEC2020 PE 13900', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentId': '41377', 'ProductType': 'MIS', 'Marketlot': '75', 'Multiplier': '1', 'BuyAveragePrice': '72.35', 'SellAveragePrice': '57.10', 'OpenBuyQuantity': '75', 'OpenSellQuantity': '75', 'Quantity': '75', 'BuyAmount': '5,426.25', 'SellAmount': '4,282.50', 'NetAmount': '-1,143.75', 'UnrealizedMTM': '0.00', 'RealizedMTM': '-1,143.75', 'MTM': '-1,143.75', 'BEP': '0.00', 'SumOfTradedQuantityAndPriceBuy': '5,426.25', 'SumOfTradedQuantityAndPriceSell': '4,282.50', 'MessageCode': 9002, 'MessageVersion': 1, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227723718}]#getPositionList()
    pos_df = pd.DataFrame(positionList)
    pos_eids = pos_df[ (pos_df['Quantity'] != '0') ]["ExchangeInstrumentId"].astype(int).values.tolist()
    ce_pos_eids = [i for i in oIDs[c_p] if i in pos_eids]
    print(f"--- squaring off {c_p} positions through repair strategy function ---")
    for ids in ce_pos_eids:
        squareOff(ids,"Call Option SELL")
        
    print("--------------------- Sq-Off Completed ----------------------------")
    
    print(f"\n --- Cancelling SL-M  {c_p} orders  ---")
    orderList = [{'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10026147, 'OrderReferenceID': '', 'GeneratedBy': 'TWS', 'ExchangeOrderID': 'X_31475561', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Buy', 'OrderType': 'StopMarket', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'New', 'OrderAverageTradedPrice': '88.45', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T13:50:53.7042412', 'ExchangeTransactTime': '2020-12-30T13:50:54+05:30', 'LastUpdateDateTime': '2020-12-30T13:50:54.0682695', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': '', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762024}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025789, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475408', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41377, 'OrderSide': 'Buy', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 72.1, 'OrderStatus': 'Open', 'OrderAverageTradedPrice': '72.35', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:46.3067796', 'ExchangeTransactTime': '2020-12-30T12:39:39+05:30', 'LastUpdateDateTime': '2020-12-30T12:39:39.0228247', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice1', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762023}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025788, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475407', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41377, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '57.10', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:41.1823828', 'ExchangeTransactTime': '2020-12-30T12:21:41+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:41.8754364', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice0', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762022}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025787, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475406', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Buy', 'OrderType': 'StopMarket', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 97.7, 'OrderStatus': 'New', 'OrderAverageTradedPrice': '', 'LeavesQuantity': 75, 'CumulativeQuantity': 0, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:38.7891996', 'ExchangeTransactTime': '2020-12-30T12:21:38+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:38.7901995', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice1', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762011}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025786, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475405', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '82.70', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:33.377785', 'ExchangeTransactTime': '2020-12-30T12:21:33+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:33.7418131', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice0', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762021}] #getOrderList()
    ord_df = pd.DataFrame(orderList)
    pendings = ord_df[ (ord_df['OrderType'] == "StopMarket") & (ord_df['OrderStatus'].isin(["New","Open","Partially Filled"])) ]["AppOrderID"].tolist()
    pending = [i for i in oIDs[c_p] if i in pendings]
    drop = []
    attempt = 0
    while len(pending)>0 and attempt<5:
        pending = [j for j in pending if j not in drop]
        for order in pending:
            try:
                cancelOrder(order)
                drop.append(order)
            except:
                print("unable to cancel order id : ",order)
                attempt+=1
    
    print(f"--- placing a sell {c_p} Order for next strikeprice ---")
    if c_p == 'CE':
        sign=add
        otyp='ce'
    if c_p == 'PE':
        sign=sub
        otyp='pe'        
    eid1 = get_eID(ticker, otyp, weekly_exp, sign(strikePrice,50))
    placeOrder(eid1, 'sell', 75)
    rt1.stop()
    
    


def repairStrategy(ticker):
    if monitor:
        oIDs = {'CE': [10026147, 39308, 10026149], 'PE': [10026148, 39309, 10026150]}
        print("Dictionary of orders :",oIDs)
        # print("--- Checking for repair if symbol goes +- 40 ---")
        curPrc= 14400 #nse.get_index_quote("nifty 50")['lastPrice']
        print(f''' Cuurent NFTY PRC = {curPrc} ''')
        if curPrc > nfty_ltp+40:
            runRepairActions('CE')
        #     print("Dictionary of orders :",oIDs)
        #     print(" -- symbol goes + 40 -- ")
        #     positionList = [{'AccountID': 'IIFL24', 'TradingSymbol': 'NIFTY 31DEC2020 CE 13900', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentId': '39308', 'ProductType': 'MIS', 'Marketlot': '75', 'Multiplier': '1', 'BuyAveragePrice': '0.00', 'SellAveragePrice': '82.70', 'OpenBuyQuantity': '0', 'OpenSellQuantity': '75', 'Quantity': '-75', 'BuyAmount': '0.00', 'SellAmount': '6,202.50', 'NetAmount': '6,202.50', 'UnrealizedMTM': '1,485.00', 'RealizedMTM': '0.00', 'MTM': '1,485.00', 'BEP': '82.70', 'SumOfTradedQuantityAndPriceBuy': '0.00', 'SumOfTradedQuantityAndPriceSell': '6,202.50', 'MessageCode': 9002, 'MessageVersion': 1, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227723717}, {'AccountID': 'IIFL24', 'TradingSymbol': 'NIFTY 31DEC2020 PE 13900', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentId': '41377', 'ProductType': 'MIS', 'Marketlot': '75', 'Multiplier': '1', 'BuyAveragePrice': '72.35', 'SellAveragePrice': '57.10', 'OpenBuyQuantity': '75', 'OpenSellQuantity': '75', 'Quantity': '75', 'BuyAmount': '5,426.25', 'SellAmount': '4,282.50', 'NetAmount': '-1,143.75', 'UnrealizedMTM': '0.00', 'RealizedMTM': '-1,143.75', 'MTM': '-1,143.75', 'BEP': '0.00', 'SumOfTradedQuantityAndPriceBuy': '5,426.25', 'SumOfTradedQuantityAndPriceSell': '4,282.50', 'MessageCode': 9002, 'MessageVersion': 1, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227723718}]#getPositionList()
        #     pos_df = pd.DataFrame(positionList)
        #     pos_eids = pos_df[ (pos_df['Quantity'] != '0') ]["ExchangeInstrumentId"].astype(int).values.tolist()
        #     ce_pos_eids = [i for i in oIDs['CE'] if i in pos_eids]
        #     print("--- squaring off CE positions through repair strategy function ---")
        #     for ids in ce_pos_eids:
        #         squareOff(ids,"Call Option SELL")
        #     print("--------------------- Sq-Off Completed ----------------------------")
        #     print("\n --- Cancelling SL-M  CE orders  ---")
        #     orderList = [{'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10026147, 'OrderReferenceID': '', 'GeneratedBy': 'TWS', 'ExchangeOrderID': 'X_31475561', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Buy', 'OrderType': 'StopMarket', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'New', 'OrderAverageTradedPrice': '88.45', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T13:50:53.7042412', 'ExchangeTransactTime': '2020-12-30T13:50:54+05:30', 'LastUpdateDateTime': '2020-12-30T13:50:54.0682695', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': '', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762024}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025789, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475408', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41377, 'OrderSide': 'Buy', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 72.1, 'OrderStatus': 'Open', 'OrderAverageTradedPrice': '72.35', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:46.3067796', 'ExchangeTransactTime': '2020-12-30T12:39:39+05:30', 'LastUpdateDateTime': '2020-12-30T12:39:39.0228247', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice1', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762023}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025788, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475407', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41377, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '57.10', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:41.1823828', 'ExchangeTransactTime': '2020-12-30T12:21:41+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:41.8754364', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice0', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762022}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025787, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475406', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Buy', 'OrderType': 'StopMarket', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 97.7, 'OrderStatus': 'New', 'OrderAverageTradedPrice': '', 'LeavesQuantity': 75, 'CumulativeQuantity': 0, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:38.7891996', 'ExchangeTransactTime': '2020-12-30T12:21:38+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:38.7901995', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice1', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762011}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025786, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475405', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '82.70', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:33.377785', 'ExchangeTransactTime': '2020-12-30T12:21:33+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:33.7418131', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice0', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762021}] #getOrderList()
        #     ord_df = pd.DataFrame(orderList)
        #     pendings = ord_df[ (ord_df['OrderType'] == "StopMarket") & (ord_df['OrderStatus'].isin(["New","Open","Partially Filled"])) ]["AppOrderID"].tolist()
        #     pending = [i for i in oIDs['CE'] if i in pendings]
        #     drop = []
        #     attempt = 0
        #     while len(pending)>0 and attempt<5:
        #         pending = [j for j in pending if j not in drop]
        #         for order in pending:
        #             try:
        #                 cancelOrder(order)
        #                 drop.append(order)
        #             except:
        #                 print("unable to cancel order id : ",order)
        #                 attempt+=1
            
        #     print("--- placing a sell CE Order for next strikeprice ---")
        #     eid1 = get_eID(ticker, 'ce', weekly_exp, strikePrice+50)
        #     placeOrder(eid1, 'sell', 75)
        #     # rt1.stop()
        
        elif curPrc < nfty_ltp-40:
            runRepairActions('PE')
        #     oIDs = {'CE': [10026147, 39308, 10026149], 'PE': [10026148, 39309, 10026150]}       
        #     print("Dictionary of orders :",oIDs)

        #     print(" -- symbol goes -ve 40 -- ")
        #     positionList = [{'AccountID': 'IIFL24', 'TradingSymbol': 'NIFTY 31DEC2020 CE 13900', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentId': '39308', 'ProductType': 'MIS', 'Marketlot': '75', 'Multiplier': '1', 'BuyAveragePrice': '0.00', 'SellAveragePrice': '82.70', 'OpenBuyQuantity': '0', 'OpenSellQuantity': '75', 'Quantity': '-75', 'BuyAmount': '0.00', 'SellAmount': '6,202.50', 'NetAmount': '6,202.50', 'UnrealizedMTM': '1,485.00', 'RealizedMTM': '0.00', 'MTM': '1,485.00', 'BEP': '82.70', 'SumOfTradedQuantityAndPriceBuy': '0.00', 'SumOfTradedQuantityAndPriceSell': '6,202.50', 'MessageCode': 9002, 'MessageVersion': 1, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227723717}, {'AccountID': 'IIFL24', 'TradingSymbol': 'NIFTY 31DEC2020 PE 13900', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentId': '39309', 'ProductType': 'MIS', 'Marketlot': '75', 'Multiplier': '1', 'BuyAveragePrice': '72.35', 'SellAveragePrice': '57.10', 'OpenBuyQuantity': '75', 'OpenSellQuantity': '75', 'Quantity': '75', 'BuyAmount': '5,426.25', 'SellAmount': '4,282.50', 'NetAmount': '-1,143.75', 'UnrealizedMTM': '0.00', 'RealizedMTM': '-1,143.75', 'MTM': '-1,143.75', 'BEP': '0.00', 'SumOfTradedQuantityAndPriceBuy': '5,426.25', 'SumOfTradedQuantityAndPriceSell': '4,282.50', 'MessageCode': 9002, 'MessageVersion': 1, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227723718}]#getPositionList()
        #     pos_df = pd.DataFrame(positionList)
        #     pos_eids = pos_df[ (pos_df['Quantity'] != '0') ]["ExchangeInstrumentId"].astype(int).values.tolist()
        #     pe_pos_eids = [i for i in oIDs['PE'] if i in pos_eids]
        #     print("--- squaring off EE positions ---")
        #     for ids in pe_pos_eids:
        #         squareOff(ids,"Put Option SELL")
           
        #     print("--- Cancelling SL-M orders for PE ---")
        #     orderList = [{'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10026148, 'OrderReferenceID': '', 'GeneratedBy': 'TWS', 'ExchangeOrderID': 'X_31475561', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Buy', 'OrderType': 'StopMarket', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'New', 'OrderAverageTradedPrice': '88.45', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T13:50:53.7042412', 'ExchangeTransactTime': '2020-12-30T13:50:54+05:30', 'LastUpdateDateTime': '2020-12-30T13:50:54.0682695', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': '', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762024}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10026150, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475408', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41377, 'OrderSide': 'Buy', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 72.1, 'OrderStatus': 'Open', 'OrderAverageTradedPrice': '72.35', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:46.3067796', 'ExchangeTransactTime': '2020-12-30T12:39:39+05:30', 'LastUpdateDateTime': '2020-12-30T12:39:39.0228247', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice1', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762023}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025788, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475407', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41377, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '57.10', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:41.1823828', 'ExchangeTransactTime': '2020-12-30T12:21:41+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:41.8754364', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice0', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762022}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025787, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475406', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Buy', 'OrderType': 'StopMarket', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 97.7, 'OrderStatus': 'New', 'OrderAverageTradedPrice': '', 'LeavesQuantity': 75, 'CumulativeQuantity': 0, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:38.7891996', 'ExchangeTransactTime': '2020-12-30T12:21:38+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:38.7901995', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice1', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762011}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025786, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475405', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '82.70', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:33.377785', 'ExchangeTransactTime': '2020-12-30T12:21:33+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:33.7418131', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice0', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762021}]
        #     ord_df = pd.DataFrame(orderList)
        #     pendings = ord_df[ (ord_df['OrderType'] == "StopMarket") & (ord_df['OrderStatus'].isin(["New","Open","Partially Filled"])) ]["AppOrderID"].tolist()
        #     pending = [i for i in oIDs['PE'] if i in pendings]
        #     drop = []
        #     attempt = 0
        #     while len(pending)>0 and attempt<5:
        #         pending = [j for j in pending if j not in drop]
        #         for order in pending:
        #             try:
        #                 cancelOrder(order)
        #                 drop.append(order)
        #             except:
        #                 print("unable to cancel order id : ",order)
        #                 attempt+=1
            
        #     print("--- placing a sell PE Order for next strikeprice ---")
        #     eid2 = get_eID(ticker, 'pe', weekly_exp, strikePrice-50)
        #     placeOrder(eid2, 'sell', 75)
        #     rt1.stop()
        else:
            # print("Repair running...")
            print("winky wink")
          
monitor = True
ticker = "NIFTY"
nfty_ltp = 14448
strikePrice = 14500

# repairStrategy(ticker)

print("starting...")
nextThu_and_lastThu_expiry_date ()
rt1 = RepeatedTimer(4, repairStrategy, ticker) # it auto-starts, no need of rt.start()
try:
    print(" DUMMY BIG FUNC started  ")
    time.sleep(20) # your long-running job goes here...
    print(" DUMMY BIG FUNC completed")
finally:
    print("finally block")
    rt1.stop() # better in a try/finally block to make sure the program ends!
    print("stopped all")
    rt1.stop()
#============================================
from XTConnect import XTSConnect


API_KEY = "ebaa4a8cf2de358e53c942"
API_SECRET = "Ojre664@S9"
XTS_API_BASE_URL = "https://xts-api.trading"
source = "WEBAPI"
xt = XTSConnect(API_KEY, API_SECRET, source)
login_resp = xt.interactive_login()
if login_resp['type'] != 'error':
    logging.info("Login Successful")

import logging

logging.basicConfig(filename='../logs/Strategy_1_log.txt',level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

def login():
    global xt
    # logging.debug('login initializing..')
    # Trading Interactive Creds
    API_KEY = "ebaa4a8cf2de358e53c942"
    API_SECRET = "Ojre664@S9"
    # MarketData Creds
    # API_KEY = "ebaa4a8cf2de358e53c942"
    # API_SECRET = "Ojre664@S9"
    # XTS_API_BASE_URL = "https://xts-api.trading"
    source = "WEBAPI"
    xt = XTSConnect(API_KEY, API_SECRET, source)
    login_resp = xt.interactive_login()
    if login_resp['type'] != 'error':
        print('Login Successful')
        # logging.info("Login Successful")
    else:
         print('Login NOT Successful')
        # logging.error("Not able to login..")


eid=58346
symbol='aasss'
def squareOff(eid,symbol):
    ab = 0
    logging.info(f'squaring-off for :, {symbol} , {eid}')
    while ab < 5:
        try:
           sq_off_resp = xt.squareoff_position(
                exchangeSegment=xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=eid,
                productType=xt.PRODUCT_MIS,
                squareoffMode=xt.SQUAREOFF_DAYWISE,
                positionSquareOffQuantityType=xt.SQUAREOFFQUANTITY_PERCENTAGE,
                squareOffQtyValue=100,
                blockOrderSending=True,
                cancelOrders=True)
           if sq_off_resp['type'] != "error":
               logging.info(f"Squared-off for symbol {symbol} | {eid}")
               break
           if sq_off_resp['type'] == "error":
               logging.error(sq_off_resp["description"])
               if (sq_off_resp["description"] == "Please Provide token to Authenticate") \
                   or (sq_off_resp["description"] == "Your session has been expired") \
                   or (sq_off_resp["description"] == "Token/Authorization not found"):
                   logging.debug("Trying login in again...")
                   login()
                   continue
           else:
               raise Exception("Unkonwn error in squareOff func")
        except Exception as e:
            logging.exception("Can't square-off open positions...retrying",e)
            # traceback.print_exc()
            time.sleep(2)
            ab+=1
import time
cur_PnL=12.12
def printPNL():
    logging.info('Time-PnL printing below')
    logging.info((time.strftime("%d-%m-%Y %H:%M:%S"),cur_PnL))

import requests
# token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySUQiOiJJSUZMMjRfSU5URVJBQ1RJVkUiLCJwdWJsaWNLZXkiOiJlYmFhNGE4Y2YyZGUzNThlNTNjOTQyIiwiaWF0IjoxNjExNDA0Nzk2LCJleHAiOjE2MTE0OTExOTZ9.w42t2jV1v_eUsWlhgSOevBS_5yOEJPrwooMRYu8yN1w"

url="https://developers.symphonyfintech.in/interactive/orders"
url="https://developers.symphonyfintech.in/interactive/user/balance"
# api_key='ebaa4a8cf2de358e53c942'
headers = {
    'authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySUQiOiJJSUZMMjRfSU5URVJBQ1RJVkUiLCJwdWJsaWNLZXkiOiJlYmFhNGE4Y2YyZGUzNThlNTNjOTQyIiwiaWF0IjoxNjExNDA1OTI4LCJleHAiOjE2MTE0OTIzMjh9.WwCKzCHrlSdZhXHXG9VMgVol0oTQsFDLc9y7PCC2phg',
    'content-type':'application/json'
    }
# auth = HTTPBasicAuth('apikey', 'ebaa4a8cf2de358e53c942')
req = requests.get(url, headers=headers)
print(req.text)

import socketio
headers = {
    'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySUQiOiJJSUZMMjRfSU5URVJBQ1RJVkUiLCJwdWJsaWNLZXkiOiJlYmFhNGE4Y2YyZGUzNThlNTNjOTQyIiwiaWF0IjoxNjExNDA5OTY5LCJleHAiOjE2MTE0OTYzNjl9.WrP8ZI69p9P94gnFT3EtM0JOvxNjBuEsfl-3kBx2Qhs',
    'userID':'IIFL24'
    }
sio = socketio.Client()
url="https://developers.symphonyfintech.in/"
sio.connect(url='https://developers.symphonyfintech.in/',headers={
    'path': '/interactive/socket.io',
    'query': {'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySUQiOiJJSUZMMjRfSU5URVJBQ1RJVkUiLCJwdWJsaWNLZXkiOiJlYmFhNGE4Y2YyZGUzNThlNTNjOTQyIiwiaWF0IjoxNjExNDEwOTA4LCJleHAiOjE2MTE0OTczMDh9.yoVrCP7H8ueolnNM3VPM3vBmTuYipTDczCgVNCjYiOY',
              'userID': 'IIFL24'}
    })

sio.connect()


a,b = 10,2

def div():
    return a/b


symbo="NIFTY"
def eli(symbo):
    try:
        print('try...')
        c = div()
    except Exception as e:
        print(e)
    else:
        print(symbo)
        print('in else block',c)
    finally:
        print('all completed and reached finally')

eli(symbo)

orderID = None
if not orderID:
    print('OrderId id not None')

sl=0
if sl == 0:
    orderType=xt.ORDER_TYPE_MARKET
else:
    orderType="StopMarket"

import time
orderID = 10025786
orderLists = [{'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10026147, 'OrderReferenceID': '', 'GeneratedBy': 'TWS', 'ExchangeOrderID': 'X_31475561', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Buy', 'OrderType': 'StopMarket', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '88.45', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T13:50:53.7042412', 'ExchangeTransactTime': '2020-12-30T13:50:54+05:30', 'LastUpdateDateTime': '2020-12-30T13:50:54.0682695', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': '', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762024}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025789, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475408', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41377, 'OrderSide': 'Buy', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 72.1, 'OrderStatus': 'Open', 'OrderAverageTradedPrice': '72.35', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:46.3067796', 'ExchangeTransactTime': '2020-12-30T12:39:39+05:30', 'LastUpdateDateTime': '2020-12-30T12:39:39.0228247', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice1', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762023}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025788, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475407', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41377, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'New', 'OrderAverageTradedPrice': '57.10', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:41.1823828', 'ExchangeTransactTime': '2020-12-30T12:21:41+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:41.8754364', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice0', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762022}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025787, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475406', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Buy', 'OrderType': 'StopMarket', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 97.7, 'OrderStatus': 'New', 'OrderAverageTradedPrice': '', 'LeavesQuantity': 75, 'CumulativeQuantity': 0, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:38.7891996', 'ExchangeTransactTime': '2020-12-30T12:21:38+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:38.7901995', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice1', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762011}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025786, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475405', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '82.70', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:33.377785', 'ExchangeTransactTime': '2020-12-30T12:21:33+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:33.7418131', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice0', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762021}]
# for i in orderList:
#     print(orderID , i["AppOrderID"], i["OrderStatus"] )
#     while orderID == i["AppOrderID"] and (i["OrderStatus"] == 'Open' or i["OrderStatus"] == 'New'):
#         # if orderID == i["AppOrderID"] and (i["OrderStatus"] == 'New' or i["OrderStatus"] == 'Open'):
#         print('Orders not filled.. wait for sometime.. and try again to fetch')
#         time.sleep(2)
#     if orderID == i["AppOrderID"] and i["OrderStatus"] == 'Filled':
#         tradedPrice = float(( i["OrderAverageTradedPrice"]))
#         print('Traded price is: ', tradedPrice)
#         break


orderID = 10025788
orderLists = [{'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10026147, 'OrderReferenceID': '', 'GeneratedBy': 'TWS', 'ExchangeOrderID': 'X_31475561', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Buy', 'OrderType': 'StopMarket', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '88.45', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T13:50:53.7042412', 'ExchangeTransactTime': '2020-12-30T13:50:54+05:30', 'LastUpdateDateTime': '2020-12-30T13:50:54.0682695', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': '', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762024}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025789, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475408', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41377, 'OrderSide': 'Buy', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 72.1, 'OrderStatus': 'Open', 'OrderAverageTradedPrice': '72.35', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:46.3067796', 'ExchangeTransactTime': '2020-12-30T12:39:39+05:30', 'LastUpdateDateTime': '2020-12-30T12:39:39.0228247', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice1', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762023}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025788, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475407', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41377, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '57.10', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:41.1823828', 'ExchangeTransactTime': '2020-12-30T12:21:41+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:41.8754364', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice0', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762022}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025787, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475406', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Buy', 'OrderType': 'StopMarket', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 97.7, 'OrderStatus': 'New', 'OrderAverageTradedPrice': '', 'LeavesQuantity': 75, 'CumulativeQuantity': 0, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:38.7891996', 'ExchangeTransactTime': '2020-12-30T12:21:38+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:38.7901995', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice1', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762011}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025786, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475405', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '82.70', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:33.377785', 'ExchangeTransactTime': '2020-12-30T12:21:33+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:33.7418131', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice0', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762021}]
k='AppOrderID'
l='OrderStatus'
lambf = 0
lambf = [ (orderList['OrderAverageTradedPrice'],orderList['OrderQuantity'])  for orderList in orderLists if orderList[k] == orderID and orderList['OrderStatus'] == 'Filled']
nexf = float(next((orderList['OrderAverageTradedPrice'] for orderList in orderLists if orderList[k] == orderID and orderList['OrderStatus'] == 'Filled'),None))

# positionList = [{'AccountID': 'IIFL24', 'TradingSymbol': 'NIFTY 31DEC2020 CE 13900', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentId': '39308', 'ProductType': 'MIS', 'Marketlot': '75', 'Multiplier': '1', 'BuyAveragePrice': '0.00', 'SellAveragePrice': '82.70', 'OpenBuyQuantity': '0', 'OpenSellQuantity': '75', 'Quantity': '-75', 'BuyAmount': '0.00', 'SellAmount': '6,202.50', 'NetAmount': '6,202.50', 'UnrealizedMTM': '1,485.00', 'RealizedMTM': '0.00', 'MTM': '1,485.00', 'BEP': '82.70', 'SumOfTradedQuantityAndPriceBuy': '0.00', 'SumOfTradedQuantityAndPriceSell': '6,202.50', 'MessageCode': 9002, 'MessageVersion': 1, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227723717}, {'AccountID': 'IIFL24', 'TradingSymbol': 'NIFTY 31DEC2020 PE 13900', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentId': '41377', 'ProductType': 'MIS', 'Marketlot': '75', 'Multiplier': '1', 'BuyAveragePrice': '72.35', 'SellAveragePrice': '57.10', 'OpenBuyQuantity': '75', 'OpenSellQuantity': '75', 'Quantity': '75', 'BuyAmount': '5,426.25', 'SellAmount': '4,282.50', 'NetAmount': '-1,143.75', 'UnrealizedMTM': '0.00', 'RealizedMTM': '-1,143.75', 'MTM': '-1,143.75', 'BEP': '0.00', 'SumOfTradedQuantityAndPriceBuy': '5,426.25', 'SumOfTradedQuantityAndPriceSell': '4,282.50', 'MessageCode': 9002, 'MessageVersion': 1, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227723718}]#getPositionList()
# pos_df=pd.DataFrame(positionList)

eid = {'CE': [43422, 10036036, 63.9, 75], 'PE': [43423, 10036037, 70.1, 75]}

import pandas as pd
j ={'orderID':[10036036, 10036037], 
 'tradedProce':[63.9, 70.1], 
 'symbol':['43422', '43423'],
 'qty':[75,75]
 }
import json

dff=pd.DataFrame(j)
instruments=[]
for i in range(len(dff)):
    instruments.append({'exchangeSegment': 2, 'exchangeInstrumentID': dff['symbol'].values[i]})
print(instruments)
# subs_resp = xt.send_subscription(Instruments=instruments,xtsMessageCode=1502)
subs_resp = {"type":"success","code":"s-quotes-0001","description":"Get quotes successfully!","result":{"mdp":1502,"quotesList":[{"exchangeSegment":2,"exchangeInstrumentID":"43423"},{"exchangeSegment":2,"exchangeInstrumentID":"43422"}],"listQuotes":["{\"MessageCode\":1502,\"MessageVersion\":4,\"ApplicationType\":0,\"TokenID\":0,\"ExchangeSegment\":2,\"ExchangeInstrumentID\":43423,\"ExchangeTimeStamp\":1296226865,\"Bids\":[{\"Size\":600,\"Price\":76.45,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},{\"Size\":300,\"Price\":76.3,\"TotalOrders\":3,\"BuyBackMarketMaker\":0},{\"Size\":150,\"Price\":76.25,\"TotalOrders\":2,\"BuyBackMarketMaker\":0},{\"Size\":450,\"Price\":76.2,\"TotalOrders\":2,\"BuyBackMarketMaker\":0},{\"Size\":150,\"Price\":76.15,\"TotalOrders\":2,\"BuyBackMarketMaker\":0}],\"Asks\":[{\"Size\":75,\"Price\":76.65,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},{\"Size\":450,\"Price\":76.7,\"TotalOrders\":2,\"BuyBackMarketMaker\":0},{\"Size\":75,\"Price\":76.75,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},{\"Size\":1200,\"Price\":76.8,\"TotalOrders\":4,\"BuyBackMarketMaker\":0},{\"Size\":1050,\"Price\":76.85,\"TotalOrders\":6,\"BuyBackMarketMaker\":0}],\"Touchline\":{\"BidInfo\":{\"Size\":600,\"Price\":76.45,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},\"AskInfo\":{\"Size\":75,\"Price\":76.65,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},\"LastTradedPrice\":99.9,\"LastTradedQunatity\":75,\"TotalBuyQuantity\":707700,\"TotalSellQuantity\":390825,\"TotalTradedQuantity\":91123350,\"AverageTradedPrice\":53.44,\"LastTradedTime\":1296226865,\"LastUpdateTime\":1296226865,\"PercentChange\":174.55197132616487,\"Open\":22.95,\"High\":107.55,\"Low\":21.35,\"Close\":27.9,\"TotalValueTraded\":null,\"BuyBackTotalBuy\":0,\"BuyBackTotalSell\":0},\"BookType\":1,\"XMarketType\":1,\"SequenceNumber\":338944086942332}","{\"MessageCode\":1502,\"MessageVersion\":4,\"ApplicationType\":0,\"TokenID\":0,\"ExchangeSegment\":2,\"ExchangeInstrumentID\":43422,\"ExchangeTimeStamp\":1296226865,\"Bids\":[{\"Size\":75,\"Price\":56.85,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},{\"Size\":1200,\"Price\":56.8,\"TotalOrders\":4,\"BuyBackMarketMaker\":0},{\"Size\":1050,\"Price\":56.7,\"TotalOrders\":3,\"BuyBackMarketMaker\":0},{\"Size\":975,\"Price\":56.65,\"TotalOrders\":3,\"BuyBackMarketMaker\":0},{\"Size\":1575,\"Price\":56.6,\"TotalOrders\":4,\"BuyBackMarketMaker\":0}],\"Asks\":[{\"Size\":75,\"Price\":57.1,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},{\"Size\":300,\"Price\":57.15,\"TotalOrders\":3,\"BuyBackMarketMaker\":0},{\"Size\":150,\"Price\":57.2,\"TotalOrders\":2,\"BuyBackMarketMaker\":0},{\"Size\":150,\"Price\":57.25,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},{\"Size\":1275,\"Price\":57.3,\"TotalOrders\":6,\"BuyBackMarketMaker\":0}],\"Touchline\":{\"BidInfo\":{\"Size\":75,\"Price\":56.85,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},\"AskInfo\":{\"Size\":75,\"Price\":57.1,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},\"LastTradedPrice\":66.6,\"LastTradedQunatity\":75,\"TotalBuyQuantity\":651225,\"TotalSellQuantity\":452775,\"TotalTradedQuantity\":34126875,\"AverageTradedPrice\":85.86,\"LastTradedTime\":1296226865,\"LastUpdateTime\":1296226865,\"PercentChange\":-79.70499377998934,\"Open\":222,\"High\":233.4,\"Low\":39.1,\"Close\":281.35,\"TotalValueTraded\":null,\"BuyBackTotalBuy\":0,\"BuyBackTotalSell\":0},\"BookType\":1,\"XMarketType\":1,\"SequenceNumber\":338944086942324}"]}}
if subs_resp['type'] == 'success':
    ltp=[]
    for i in range(len(dff)):
        listQuotes = json.loads(subs_resp['result']['listQuotes'][i])
        ltp.append(listQuotes['Touchline']['LastTradedPrice'])
        
dff['ltp']=ltp
dff['pnl']=(dff['ltp']-dff['tradedProce'])*dff['qty']        
cur_PnL=round(dff['pnl'].sum(),2)   
 
Out[149]: 
    orderID  tradedProce symbol  qty   ltp    pnl
0  10036036         63.9  43422   75  76.6  952.5
1  10036037         70.1  43423   75  57.1 -975.0

Out[153]: 
    orderID  tradedProce symbol  qty   ltp     pnl
0  10036036         63.9  43422   75  99.9  2700.0
1  10036037         70.1  43423   75  66.6  -262.5

    get_quote_resp = {"type":"success","code":"s-quotes-0001","description":"Get quotes successfully!","result":{"mdp":1502,"quotesList":[{"exchangeSegment":2,"exchangeInstrumentID":"43423"},{"exchangeSegment":2,"exchangeInstrumentID":"43422"}],"listQuotes":["{\"MessageCode\":1502,\"MessageVersion\":4,\"ApplicationType\":0,\"TokenID\":0,\"ExchangeSegment\":2,\"ExchangeInstrumentID\":43423,\"ExchangeTimeStamp\":1296226865,\"Bids\":[{\"Size\":600,\"Price\":76.45,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},{\"Size\":300,\"Price\":76.3,\"TotalOrders\":3,\"BuyBackMarketMaker\":0},{\"Size\":150,\"Price\":76.25,\"TotalOrders\":2,\"BuyBackMarketMaker\":0},{\"Size\":450,\"Price\":76.2,\"TotalOrders\":2,\"BuyBackMarketMaker\":0},{\"Size\":150,\"Price\":76.15,\"TotalOrders\":2,\"BuyBackMarketMaker\":0}],\"Asks\":[{\"Size\":75,\"Price\":76.65,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},{\"Size\":450,\"Price\":76.7,\"TotalOrders\":2,\"BuyBackMarketMaker\":0},{\"Size\":75,\"Price\":76.75,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},{\"Size\":1200,\"Price\":76.8,\"TotalOrders\":4,\"BuyBackMarketMaker\":0},{\"Size\":1050,\"Price\":76.85,\"TotalOrders\":6,\"BuyBackMarketMaker\":0}],\"Touchline\":{\"BidInfo\":{\"Size\":600,\"Price\":76.45,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},\"AskInfo\":{\"Size\":75,\"Price\":76.65,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},\"LastTradedPrice\":76.6,\"LastTradedQunatity\":75,\"TotalBuyQuantity\":707700,\"TotalSellQuantity\":390825,\"TotalTradedQuantity\":91123350,\"AverageTradedPrice\":53.44,\"LastTradedTime\":1296226865,\"LastUpdateTime\":1296226865,\"PercentChange\":174.55197132616487,\"Open\":22.95,\"High\":107.55,\"Low\":21.35,\"Close\":27.9,\"TotalValueTraded\":null,\"BuyBackTotalBuy\":0,\"BuyBackTotalSell\":0},\"BookType\":1,\"XMarketType\":1,\"SequenceNumber\":338944086942332}","{\"MessageCode\":1502,\"MessageVersion\":4,\"ApplicationType\":0,\"TokenID\":0,\"ExchangeSegment\":2,\"ExchangeInstrumentID\":43422,\"ExchangeTimeStamp\":1296226865,\"Bids\":[{\"Size\":75,\"Price\":56.85,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},{\"Size\":1200,\"Price\":56.8,\"TotalOrders\":4,\"BuyBackMarketMaker\":0},{\"Size\":1050,\"Price\":56.7,\"TotalOrders\":3,\"BuyBackMarketMaker\":0},{\"Size\":975,\"Price\":56.65,\"TotalOrders\":3,\"BuyBackMarketMaker\":0},{\"Size\":1575,\"Price\":56.6,\"TotalOrders\":4,\"BuyBackMarketMaker\":0}],\"Asks\":[{\"Size\":75,\"Price\":57.1,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},{\"Size\":300,\"Price\":57.15,\"TotalOrders\":3,\"BuyBackMarketMaker\":0},{\"Size\":150,\"Price\":57.2,\"TotalOrders\":2,\"BuyBackMarketMaker\":0},{\"Size\":150,\"Price\":57.25,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},{\"Size\":1275,\"Price\":57.3,\"TotalOrders\":6,\"BuyBackMarketMaker\":0}],\"Touchline\":{\"BidInfo\":{\"Size\":75,\"Price\":56.85,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},\"AskInfo\":{\"Size\":75,\"Price\":57.1,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},\"LastTradedPrice\":57.1,\"LastTradedQunatity\":75,\"TotalBuyQuantity\":651225,\"TotalSellQuantity\":452775,\"TotalTradedQuantity\":34126875,\"AverageTradedPrice\":85.86,\"LastTradedTime\":1296226865,\"LastUpdateTime\":1296226865,\"PercentChange\":-79.70499377998934,\"Open\":222,\"High\":233.4,\"Low\":39.1,\"Close\":281.35,\"TotalValueTraded\":null,\"BuyBackTotalBuy\":0,\"BuyBackTotalSell\":0},\"BookType\":1,\"XMarketType\":1,\"SequenceNumber\":338944086942324}"]}}
    
    # df=pd.DataFrame(eid,index=['symbol','orderID','tp','qty']).T
    # df.reset_index(level=0, inplace=True)
    
    
    
        # pnl=[]
        # pnl.append(eid['CE'])
        # pnl.append(eid['PE'])
        # pd=pd.DataFrame(pnl,columns=('symbol','orderID','tp','qty'))
    

instruments = [
    {'exchangeSegment': 2, 'exchangeInstrumentID': 43422}]

subs_resp = xt.send_subscription(
    Instruments=instruments,
    xtsMessageCode=1502)

subs_resp = {'type': 'success', 'code': 's-session-0001', 'description': 'Instrument subscribed successfully!', 'result': {'mdp': 1502, 'quotesList': [{'exchangeSegment': 2, 'exchangeInstrumentID': 43422}], 'listQuotes': ['{"MessageCode":1502,"MessageVersion":4,"ApplicationType":0,"TokenID":0,"ExchangeSegment":2,"ExchangeInstrumentID":43422,"ExchangeTimeStamp":1296226959,"Bids":[{"Size":75,"Price":54.35,"TotalOrders":1,"BuyBackMarketMaker":0},{"Size":600,"Price":54.3,"TotalOrders":4,"BuyBackMarketMaker":0},{"Size":450,"Price":54.25,"TotalOrders":5,"BuyBackMarketMaker":0},{"Size":1200,"Price":54.2,"TotalOrders":3,"BuyBackMarketMaker":0},{"Size":825,"Price":54.15,"TotalOrders":4,"BuyBackMarketMaker":0}],"Asks":[{"Size":75,"Price":54.55,"TotalOrders":1,"BuyBackMarketMaker":0},{"Size":225,"Price":54.6,"TotalOrders":2,"BuyBackMarketMaker":0},{"Size":75,"Price":54.65,"TotalOrders":1,"BuyBackMarketMaker":0},{"Size":375,"Price":54.7,"TotalOrders":1,"BuyBackMarketMaker":0},{"Size":450,"Price":54.75,"TotalOrders":3,"BuyBackMarketMaker":0}],"Touchline":{"BidInfo":{"Size":75,"Price":54.35,"TotalOrders":1,"BuyBackMarketMaker":0},"AskInfo":{"Size":75,"Price":54.55,"TotalOrders":1,"BuyBackMarketMaker":0},"LastTradedPrice":54.35,"LastTradedQunatity":75,"TotalBuyQuantity":664275,"TotalSellQuantity":482850,"TotalTradedQuantity":34562775,"AverageTradedPrice":85.48,"LastTradedTime":1296226959,"LastUpdateTime":1296226959,"PercentChange":-80.68242402701262,"Open":222,"High":233.4,"Low":39.1,"Close":281.35,"TotalValueTraded":null,"BuyBackTotalBuy":0,"BuyBackTotalSell":0},"BookType":1,"XMarketType":1,"SequenceNumber":338944087205260}']}}

get_quote_resp = {"type":"success","code":"s-quotes-0001","description":"Get quotes successfully!","result":{"mdp":1502,"quotesList":[{"exchangeSegment":2,"exchangeInstrumentID":"43423"},{"exchangeSegment":2,"exchangeInstrumentID":"43422"}],"listQuotes":["{\"MessageCode\":1502,\"MessageVersion\":4,\"ApplicationType\":0,\"TokenID\":0,\"ExchangeSegment\":2,\"ExchangeInstrumentID\":43423,\"ExchangeTimeStamp\":1296226865,\"Bids\":[{\"Size\":600,\"Price\":76.45,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},{\"Size\":300,\"Price\":76.3,\"TotalOrders\":3,\"BuyBackMarketMaker\":0},{\"Size\":150,\"Price\":76.25,\"TotalOrders\":2,\"BuyBackMarketMaker\":0},{\"Size\":450,\"Price\":76.2,\"TotalOrders\":2,\"BuyBackMarketMaker\":0},{\"Size\":150,\"Price\":76.15,\"TotalOrders\":2,\"BuyBackMarketMaker\":0}],\"Asks\":[{\"Size\":75,\"Price\":76.65,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},{\"Size\":450,\"Price\":76.7,\"TotalOrders\":2,\"BuyBackMarketMaker\":0},{\"Size\":75,\"Price\":76.75,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},{\"Size\":1200,\"Price\":76.8,\"TotalOrders\":4,\"BuyBackMarketMaker\":0},{\"Size\":1050,\"Price\":76.85,\"TotalOrders\":6,\"BuyBackMarketMaker\":0}],\"Touchline\":{\"BidInfo\":{\"Size\":600,\"Price\":76.45,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},\"AskInfo\":{\"Size\":75,\"Price\":76.65,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},\"LastTradedPrice\":76.6,\"LastTradedQunatity\":75,\"TotalBuyQuantity\":707700,\"TotalSellQuantity\":390825,\"TotalTradedQuantity\":91123350,\"AverageTradedPrice\":53.44,\"LastTradedTime\":1296226865,\"LastUpdateTime\":1296226865,\"PercentChange\":174.55197132616487,\"Open\":22.95,\"High\":107.55,\"Low\":21.35,\"Close\":27.9,\"TotalValueTraded\":null,\"BuyBackTotalBuy\":0,\"BuyBackTotalSell\":0},\"BookType\":1,\"XMarketType\":1,\"SequenceNumber\":338944086942332}","{\"MessageCode\":1502,\"MessageVersion\":4,\"ApplicationType\":0,\"TokenID\":0,\"ExchangeSegment\":2,\"ExchangeInstrumentID\":43422,\"ExchangeTimeStamp\":1296226865,\"Bids\":[{\"Size\":75,\"Price\":56.85,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},{\"Size\":1200,\"Price\":56.8,\"TotalOrders\":4,\"BuyBackMarketMaker\":0},{\"Size\":1050,\"Price\":56.7,\"TotalOrders\":3,\"BuyBackMarketMaker\":0},{\"Size\":975,\"Price\":56.65,\"TotalOrders\":3,\"BuyBackMarketMaker\":0},{\"Size\":1575,\"Price\":56.6,\"TotalOrders\":4,\"BuyBackMarketMaker\":0}],\"Asks\":[{\"Size\":75,\"Price\":57.1,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},{\"Size\":300,\"Price\":57.15,\"TotalOrders\":3,\"BuyBackMarketMaker\":0},{\"Size\":150,\"Price\":57.2,\"TotalOrders\":2,\"BuyBackMarketMaker\":0},{\"Size\":150,\"Price\":57.25,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},{\"Size\":1275,\"Price\":57.3,\"TotalOrders\":6,\"BuyBackMarketMaker\":0}],\"Touchline\":{\"BidInfo\":{\"Size\":75,\"Price\":56.85,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},\"AskInfo\":{\"Size\":75,\"Price\":57.1,\"TotalOrders\":1,\"BuyBackMarketMaker\":0},\"LastTradedPrice\":57.1,\"LastTradedQunatity\":75,\"TotalBuyQuantity\":651225,\"TotalSellQuantity\":452775,\"TotalTradedQuantity\":34126875,\"AverageTradedPrice\":85.86,\"LastTradedTime\":1296226865,\"LastUpdateTime\":1296226865,\"PercentChange\":-79.70499377998934,\"Open\":222,\"High\":233.4,\"Low\":39.1,\"Close\":281.35,\"TotalValueTraded\":null,\"BuyBackTotalBuy\":0,\"BuyBackTotalSell\":0},\"BookType\":1,\"XMarketType\":1,\"SequenceNumber\":338944086942324}"]}}
get_quote_msg_code_1510 ={"type":"success","code":"s-quotes-0001","description":"Get quotes successfully!","result":{"mdp":1510,"quotesList":[{"exchangeSegment":2,"exchangeInstrumentID":"43423"},{"exchangeSegment":2,"exchangeInstrumentID":"43422"}],"listQuotes":["{\"MessageCode\":1510,\"MessageVersion\":4,\"ApplicationType\":0,\"TokenID\":0,\"ExchangeSegment\":2,\"ExchangeInstrumentID\":43423,\"ExchangeTimeStamp\":1296226865,\"XTSMarketType\":1,\"OpenInterest\":3721575,\"SequenceNumber\":338944086942101}","{\"MessageCode\":1510,\"MessageVersion\":4,\"ApplicationType\":0,\"TokenID\":0,\"ExchangeSegment\":2,\"ExchangeInstrumentID\":43422,\"ExchangeTimeStamp\":1296226865,\"XTSMarketType\":1,\"OpenInterest\":3324000,\"SequenceNumber\":338944086942100}"]}}


search_by_resp = xt.search_by_instrumentid(Instruments=instruments)
print('Search By Instrument ID:', str(response))
search_by_resp = {'type': 'success', 'code': 's-search-0002', 'description': 'Instruments Found', 'result': [{'StrikePrice': 14000, 'OptionType': 3, 'ContractExpiration': '2021-01-28T14:30:00', 'RemainingExpiryDays': 2, 'RemainingExpiryDaysABS': 2, 'ContractExpirationString': '28Jan2021', 'HasContractExpired': False, 'UnderlyingType': 5, 'UnderlyingInstrumentId': -1, 'UnderlyingIndexName': 'Nifty 50', 'InstrumentID': 2102800043422, 'ExchangeInstrumentID': 43422, 'DisplayName': 'NIFTY 28JAN2021 CE 14000', 'Name': 'NIFTY', 'AuctionNumber': 0, 'MinimumQty': 1, 'QuantityMultiplier': 1, 'Multiplier': 1, 'PriceNumerator': 1, 'PriceDenominator': 1, 'LotSize': 75, 'InstrumentType': 2, 'SymbolType': 0, 'CfiCode': 'OCEXXX', 'Status': '', 'TicksPerPoint': 20, 'TickSize': 0.05, 'Description': 'NIFTY21JAN14000CE', 'IsImpliedMarket': False, 'IsTradeable': False, 'ExchangeSegment': 2, 'Series': 'OPTIDX', 'MaxTradeVolume': 2147483647, 'PriceBand': {'High': 1124, 'Low': 0.05, 'HighString': '1124.00', 'LowString': '0.05', 'CreditRating': '0.05-1124.00'}, 'DecimalDisplace': 2, 'ExtendedMarketProperties': {'CallAuctionIndicator': {'Name': {'Name': 'CallAuctionIndicator'}, 'Value': ''}, 'ExpulsionDate': {'Name': {'Name': 'ExpulsionDate'}, 'Value': '01Jan1980'}, 'IssueMaturityDate': {'Name': {'Name': 'IssueMaturityDate'}, 'Value': '28Jan2021'}, 'SettlementIndicator': {'Name': {'Name': 'SettlementIndicator'}, 'Value': 'C'}, 'SettlementNo': {'Name': {'Name': 'SettlementNo'}, 'Value': 'Missing'}, 'ListingDate': {'Name': {'Name': 'ListingDate'}, 'Value': '11Nov2020'}, 'CompanyName': {'Name': {'Name': 'CompanyName'}, 'Value': 'NIFTY21JAN14000CE'}, 'UniqueKey': {'Name': {'Name': 'UniqueKey'}, 'Value': 'NIFTY'}, 'RecordDate': {'Name': {'Name': 'RecordDate'}, 'Value': '01Jan1980'}, 'ExposureMargin': {'Name': {'Name': 'ExposureMargin'}, 'Value': '2'}, 'MarketType': {'Name': {'Name': 'MarketType'}, 'Value': 'NORMAL'}, 'BookClosureStartDate': {'Name': {'Name': 'BookClosureStartDate'}, 'Value': '01Jan1980'}, 'ExDate': {'Name': {'Name': 'ExDate'}, 'Value': '01Jan1980'}, 'IssueStartDate': {'Name': {'Name': 'IssueStartDate'}, 'Value': '11Nov2020'}, 'BookClosureEndDate': {'Name': {'Name': 'BookClosureEndDate'}, 'Value': '01Jan1980'}, 'Remarks': {'Name': {'Name': 'Remarks'}, 'Value': ''}}, 'MarketTypeStatusEligibility': {'Normal': {'MarketType': 1, 'Eligibile': True, 'TradingStatus': 2}, 'OddLot': {'MarketType': 2, 'Eligibile': False, 'TradingStatus': 2}, 'RetailDebt': {'MarketType': 3, 'Eligibile': False, 'TradingStatus': 2}, 'Auction': {'MarketType': 4, 'Eligibile': False, 'TradingStatus': 3}}, 'NameWithSeries': 'NIFTY-OPTIDX', 'DisplayNameWithExchange': 'NIFTY 28JAN2021 CE 14000 - NSEFO', 'DisplayNameWithSeries': 'NIFTY 28JAN2021 CE 14000 - OPTIDX', 'DisplayNameWithSeriesAndExchange': 'NIFTY 28JAN2021 CE 14000 - OPTIDX - NSEFO', 'FreezeQty': 5001, 'LastUpdateTime': 0, 'FiftyTwoWeekHigh': 0, 'FiftyTwoWeekLow': 0, 'Bhavcopy': {'Open': 486.05, 'High': 502.1, 'Low': 265.75, 'Close': 281.35, 'TotTrdQty': 1073925, 'TotTrdVal': 422856986108625, 'TimeStamp': '0001-01-01T00:00:00', 'TotalTrades': 14319, 'OpenInterest': 14095, 'SettlementPrice': 281.35}, 'AdditionalPreExpiryMarginPerc': 0, 'AdditionalMarginPercLong': 0, 'AdditionalMarginPercShort': 0, 'DeliveryMarginPerc': 0, 'SpecialMarginPercBuy': 0, 'SpecialMarginPercSell': 0, 'TenderMargin': 0, 'ELMLongMargin': 0, 'ELMShortMargin': 0, 'InitialMarginPerc': 0, 'ExposureMarginPerc': 2, 'CallAuctionIndicator': 0, 'MarketType': 1, 'CurrentEligibleMarketType': 1, 'Industry': 0}]}

ltp= 40   
symbol=39308
orderID = 10025788
tp = float(next((orderList['OrderAverageTradedPrice'] for orderList in orderLists if orderList[k] == orderID and orderList['OrderStatus'] == 'Filled'),None))
qty= next((orderList['OrderQuantity'] for orderList in orderLists if orderList[k] == orderID and orderList['OrderStatus'] == 'Filled'),None)

pnl_resp = success', 'code': 's-search-0002', 'description': 'Instruments Found', 'result': [{'StrikePrice': 14000, 'OptionType': 3, 'ContractExpiration': '2021-01-28T14:30:00', 'RemainingExpiryDays': 2, 'RemainingExpiryDaysABS': 2, 'ContractExpirationString': '28Jan2021', 'HasContractExpired': False, 'UnderlyingType': 5, 'UnderlyingInstrumentId': -1, 'UnderlyingIndexName': 'Nifty 50', 'InstrumentID': 2102800043422, 'ExchangeInstrumentID': 43422, 'DisplayName': 'NIFTY 28JAN2021 CE 14000', 'Name': 'NIFTY', 'AuctionNumber': 0, 'MinimumQty': 1, 'QuantityMultiplier': 1, 'Multiplier': 1, 'PriceNumerator': 1, 'PriceDenominator': 1, 'LotSize': 75, 'InstrumentType': 2, 'SymbolType': 0, 'CfiCode': 'OCEXXX', 'Status': '', 'TicksPerPoint': 20, 'TickSize': 0.05, 'Description': 'NIFTY21JAN14000CE', 'IsImpliedMarket': False, 'IsTradeable': False, 'ExchangeSegment': 2, 'Series': 'OPTIDX', 'MaxTradeVolume': 2147483647, 'PriceBand': {'High': 1124, 'Low': 0.05, 'HighString': '1124.00', 'LowString': '0.05', 'CreditRating': '0.05-1124.00'}, 'DecimalDisplace': 2, 'ExtendedMarketProperties': {'CallAuctionIndicator': {'Name': {'Name': 'CallAuctionIndicator'}, 'Value': ''}, 'ExpulsionDate': {'Name': {'Name': 'ExpulsionDate'}, 'Value': '01Jan1980'}, 'IssueMaturityDate': {'Name': {'Name': 'IssueMaturityDate'}, 'Value': '28Jan2021'}, 'SettlementIndicator': {'Name': {'Name': 'SettlementIndicator'}, 'Value': 'C'}, 'SettlementNo': {'Name': {'Name': 'SettlementNo'}, 'Value': 'Missing'}, 'ListingDate': {'Name': {'Name': 'ListingDate'}, 'Value': '11Nov2020'}, 'CompanyName': {'Name': {'Name': 'CompanyName'}, 'Value': 'NIFTY21JAN14000CE'}, 'UniqueKey': {'Name': {'Name': 'UniqueKey'}, 'Value': 'NIFTY'}, 'RecordDate': {'Name': {'Name': 'RecordDate'}, 'Value': '01Jan1980'}, 'ExposureMargin': {'Name': {'Name': 'ExposureMargin'}, 'Value': '2'}, 'MarketType': {'Name': {'Name': 'MarketType'}, 'Value': 'NORMAL'}, 'BookClosureStartDate': {'Name': {'Name': 'BookClosureStartDate'}, 'Value': '01Jan1980'}, 'ExDate': {'Name': {'Name': 'ExDate'}, 'Value': '01Jan1980'}, 'IssueStartDate': {'Name': {'Name': 'IssueStartDate'}, 'Value': '11Nov2020'}, 'BookClosureEndDate': {'Name': {'Name': 'BookClosureEndDate'}, 'Value': '01Jan1980'}, 'Remarks': {'Name': {'Name': 'Remarks'}, 'Value': ''}}, 'MarketTypeStatusEligibility': {'Normal': {'MarketType': 1, 'Eligibile': True, 'TradingStatus': 2}, 'OddLot': {'MarketType': 2, 'Eligibile': False, 'TradingStatus': 2}, 'RetailDebt': {'MarketType': 3, 'Eligibile': False, 'TradingStatus': 2}, 'Auction': {'MarketType': 4, 'Eligibile': False, 'TradingStatus': 3}}, 'NameWithSeries': 'NIFTY-OPTIDX', 'DisplayNameWithExchange': 'NIFTY 28JAN2021 CE 14000 - NSEFO', 'DisplayNameWithSeries': 'NIFTY 28JAN2021 CE 14000 - OPTIDX', 'DisplayNameWithSeriesAndExchange': 'NIFTY 28JAN2021 CE 14000 - OPTIDX - NSEFO', 'FreezeQty': 5001, 'LastUpdateTime': 0, 'FiftyTwoWeekHigh': 0, 'FiftyTwoWeekLow': 0, 'Bhavcopy': {'Open': 486.05, 'High': 502.1, 'Low': 265.75, 'Close': 281.35, 'TotTrdQty': 1073925, 'TotTrdVal': 422856986108625, 'TimeStamp': '0001-01-01T00:00:00', 'TotalTrades': 14319, 'OpenInterest': 14095, 'SettlementPrice': 281.35}, 'AdditionalPreExpiryMarginPerc': 0, 'AdditionalMarginPercLong': 0, 'AdditionalMarginPercShort': 0, 'DeliveryMarginPerc': 0, 'SpecialMarginPercBuy': 0, 'SpecialMarginPercSell': 0, 'TenderMargin': 0, 'ELMLongMargin': 0, 'ELMShortMargin': 0, 'InitialMarginPerc': 0, 'ExposureMarginPerc': 2, 'CallAuctionIndicator': 0, 'MarketType': 1, 'CurrentEligibleMarketType': 1, 'Industry': 0}]}

pd.DataFrame({43423: [43423, 10036037, 70.1, 10036038], 43422: [43422, 10036036, 63.9, 10036039]})
ocd = {43422: 'CE', 43423: 'PE'}
za=0
zz=pd.DataFrame(ocd,index=[0])
za=zz.reset_index(level=0, inplace=True)
aa=za.columns([1,2])


df = pd.DataFrame({'CE': [43422, 10036036, 63.9, 10036039], 'PE': [43423, 10036037, 70.1, 10036038]},index=['symbol','orderID','tp','qty'])
dft=df.T

dft['symbol']
dft.reset_index(level=0, inplace=True)
dict(dft.iloc[0])

pnl1 = [symbol,orderID,tp,qty,ltp]
pnl2 = [symbol,orderID,tp,qty,ltp]
pnl1 = [39308,10025788,100,10,120]
pnl2 = [39309,10025789,100,10,80]
pnl=[]
pnl.append(pnl1)
pnl.append(pnl2)
pnl_pd=0
pnl_pd= pd.DataFrame(pnl,columns=('symbol','orderID','tp','qty','ltp'))
# pnl_pd.columns=['symbol','orderID','tp','qty','ltp']
pnl_pd['pnl']=(pnl_pd['ltp']-pnl_pd['tp'])*pnl_pd['qty']

pnl_pd['pnl']=(pnl_pd['tp']-pnl_pd['ltp'])*pnl_pd['qty']


while True:
    orderList = [{'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10026147, 'OrderReferenceID': '', 'GeneratedBy': 'TWS', 'ExchangeOrderID': 'X_31475561', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Buy', 'OrderType': 'StopMarket', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '88.45', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T13:50:53.7042412', 'ExchangeTransactTime': '2020-12-30T13:50:54+05:30', 'LastUpdateDateTime': '2020-12-30T13:50:54.0682695', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': '', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762024}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025789, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475408', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41377, 'OrderSide': 'Buy', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 72.1, 'OrderStatus': 'Open', 'OrderAverageTradedPrice': '72.35', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:46.3067796', 'ExchangeTransactTime': '2020-12-30T12:39:39+05:30', 'LastUpdateDateTime': '2020-12-30T12:39:39.0228247', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice1', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762023}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025788, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475407', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41377, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'New', 'OrderAverageTradedPrice': '57.10', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:41.1823828', 'ExchangeTransactTime': '2020-12-30T12:21:41+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:41.8754364', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice0', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762022}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025787, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475406', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Buy', 'OrderType': 'StopMarket', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 97.7, 'OrderStatus': 'New', 'OrderAverageTradedPrice': '', 'LeavesQuantity': 75, 'CumulativeQuantity': 0, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:38.7891996', 'ExchangeTransactTime': '2020-12-30T12:21:38+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:38.7901995', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice1', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762011}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025786, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475405', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '82.70', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:33.377785', 'ExchangeTransactTime': '2020-12-30T12:21:33+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:33.7418131', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice0', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762021}]
    print("loading Olists")
    for i in orderList:
        print(orderID , i["AppOrderID"], i["OrderStatus"] )
        if orderID == i["AppOrderID"] and i["OrderStatus"] != 'Filled':
            print('Orders not filled.. wait for sometime.. and try again to fetch')
            time.sleep(3)
            break
    else:
        break
check = True
a=0
while a<3:
    orderList7 = [{'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10026147, 'OrderReferenceID': '', 'GeneratedBy': 'TWS', 'ExchangeOrderID': 'X_31475561', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Buy', 'OrderType': 'StopMarket', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '88.45', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T13:50:53.7042412', 'ExchangeTransactTime': '2020-12-30T13:50:54+05:30', 'LastUpdateDateTime': '2020-12-30T13:50:54.0682695', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': '', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762024}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025789, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475408', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41377, 'OrderSide': 'Buy', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 72.1, 'OrderStatus': 'Open', 'OrderAverageTradedPrice': '72.35', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:46.3067796', 'ExchangeTransactTime': '2020-12-30T12:39:39+05:30', 'LastUpdateDateTime': '2020-12-30T12:39:39.0228247', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice1', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762023}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025788, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475407', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41377, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'New', 'OrderAverageTradedPrice': '57.10', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:41.1823828', 'ExchangeTransactTime': '2020-12-30T12:21:41+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:41.8754364', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice0', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762022}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025787, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475406', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Buy', 'OrderType': 'StopMarket', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 97.7, 'OrderStatus': 'New', 'OrderAverageTradedPrice': '', 'LeavesQuantity': 75, 'CumulativeQuantity': 0, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:38.7891996', 'ExchangeTransactTime': '2020-12-30T12:21:38+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:38.7901995', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice1', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762011}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10025786, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_31475405', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 41376, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '82.70', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-30T12:21:33.377785', 'ExchangeTransactTime': '2020-12-30T12:21:33+05:30', 'LastUpdateDateTime': '2020-12-30T12:21:33.7418131', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FirstChoice0', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 314802227762021}]
    print("loading Olists")
    aj = [orderList for orderList in orderList7 if orderList[k] == orderID and orderList['OrderStatus'] != 'Filled']  
    if not aj:
        nexf3 = float(next((orderList['OrderAverageTradedPrice'] for orderList in orderList7 if orderList[k] == orderID and orderList['OrderStatus'] == 'Filled'),None))
        print(nexf3)
        break
    a+=1
    time.sleep(3)    
else:
    "unable to perform orderLsits"    



tp = None
if tp:
    print("tp is None")
  
# ========================= 
dest = {**orig, **extra}
dest = {**orig, 'D': 4, 'E': 5}

import pandas as pd

orderID_dict=None
orderID_dictR = {}

otype='CE'
orderID=[11,11]

orderID2=21
tradedPrice=211
symbol="LL"
qty=75


orderID_dict={}
orderID_dict[symbol] = []
orderID_dict[symbol].append({'symbol':symbol})
orderID_dict[symbol].append({'orderID':orderID})
orderID_dict[symbol].append({'orderID2':orderID2})
orderID_dict[symbol].append({'tradedPrice':tradedPrice})

orderID_dictR.update(orderID_dict)

ordersEid = {'L7': 'CE', 'A7': 'PE'}

j = {}
j["orderID"]=[]
j["orderID"].append(orderID)

j["symbol"].append({'orderID':orderID})
j["symbol"].append({'orderID2':orderID2})
j["symbol"].append({'tradedPrice':tradedPrice})
orderID_dict={}
orderID_dict[symbol] = []
orderID_dict[symbol].append(j)
# orderID_dictR = {}
orderID_dictR.update(orderID_dict)

from collections import defaultdict
dd = defaultdict(list)
for d in (ordersEid, orderID_dictR): 
    for key, value in d.items():
        dd[key].append(value)
oIDs={}
for k,v in dd.items():
    i = iter(v)
    # print(i)
    b = dict(zip(i, i))
    oIDs.update(b)              

oIDs['CE'][0]['symbol']

df = pd.DataFrame({'Date':['10/2/2011', '11/2/2011', '12/2/2011', '13/2/2011'], 
                    'Event':['Music', 'Poetry', 'Theatre', 'Comedy'], 
                    'Cost':[10000, 5000, 15000, 2000]}) 

j ={'orderID':[1234, 11111], 
 'tradedProce':[90, 20], 
 'symbol':['CE', 'PE']}

pd.DataFrame(j)



# orderID_dictR = {39309: [10026148, 39309, 10026150], 39308: [10026147, 39308, 10026149]}
dd = defaultdict(list)

for d in (ordersEid, orderID_dictR): 
    for key, value in d.items():
        dd[key].append(value)
oIDs={}
for k,v in dd.items():
    
    i = iter(v)
    # print(i)
    b = dict(zip(i, i))
    oIDs.update(b)              
print(oIDs)

oIDs['CE'][0]




gg={'A7': [{'symbol': 'A7', 'orderID': 11117, 'orderID2': 22227, 'tradedPrice': 777}], 'L7': [{'symbol': 'L7', 'orderID': 11117, 'orderID2': 22227, 'tradedPrice': 777}]}
hh={'L7': 'CE', 'A7': 'PE'}
ii={**gg,**hh}
# ==============================================
new_dict = {k:[] for k in ['oo','tt','qq','ss','sl']}

import pandas as pd
import json,time


# instruments=[{'exchangeSegment': 2, 'exchangeInstrumentID': '41438'} ,
#              {'exchangeSegment': 2, 'exchangeInstrumentID': '41439'}]
# subs_resp = xt.send_subscription(Instruments=instruments,xtsMessageCode=1502)

j ={'orderID':[10036036, 10036037], 
 'tradedPrice':[52.65, 43.05], 
 'symbol':['41438', '41439'],
 'qty':[75,75]
 }
dc =[{'ss': '41410', 'qq': 75, 'oo': 10029379, 'tt': 19.95, 'sl': 10029381}, 
     {'ss': '41411', 'qq': 75, 'oo': 10029380, 'tt': 0.45, 'sl': 10029382}]

def printPNL(dc):
    try:
        odf = pd.DataFrame(dc)
        eid_df =pd.DataFrame(ordersEid)
        df = odf.merge(eid_df, how='left')
        # login()
        instruments=[]
        for i in range(len(df)):
            instruments.append({'exchangeSegment': 2, 'exchangeInstrumentID': df['ss'].values[i]})
            # print(instruments)
        xt.send_unsubscription(Instruments=instruments,xtsMessageCode=1502)    
        subs_resp = xt.send_subscription(Instruments=instruments,xtsMessageCode=1502)
                
        if subs_resp['type'] == 'success':
            ltp=[]
            for i in range(len(df)):
                listQuotes = json.loads(subs_resp['result']['listQuotes'][i])
                ltp.append(listQuotes['Touchline']['LastTradedPrice'])
            df['ltp']=ltp
            df['pnl']=(df['ltp']-df['tt'])*df['qq'] 
            cur_PnL=df['pnl'].sum() 
            print(f'df is : \n {df} \n')
            # logging.info('Time,PnL printing below')
            # logging.info((time.strftime("%d-%m-%Y %H:%M:%S"),cur_PnL))
            print(time.strftime("%d-%m-%Y %H:%M:%S"),cur_PnL)
    except Exception as e:
        print('Exception:',e)

#=============================

d1 = {'oo': 10028744, 'tt': 32.0, 'qq': 75, 'ss': 40021, 'sl': 10028745}
d2 = {'oo': 10028746, 'tt': 66.0, 'qq': 75, 'ss': 40026, 'sl': 10028746}
from collections import defaultdict

a = {'ss': 41410, 'qq': 75, 'oo': 10029379, 'tt': 19.95, 'sl': 10029381}

for k,v in a.items():
    print(k,v)
    d = {}
    d[k]=(v)

res = df.merge(dp1, how='left')

res.

dc =[{'ss': 41410, 'qq': 75, 'oo': 10029379, 'tt': 19.95, 'sl': 10029381}, 
     {'ss': 41411, 'qq': 75, 'oo': 10029380, 'tt': 0.45, 'sl': 10029382}]
df =pd.DataFrame(dc)

ordersEid = {'oty': ['PE', 'CE'], 'ss': ['41410', '41411']}
# ordersEid = { 'CE' :41410, 'PE': 41777}
dp1 =pd.DataFrame(ordersEid)

import json

dp1['CE']

for i in range(len(df)):
    print(df['ss'].values[i])


xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol="NIFTY",
                expiryDate='28Jan2021',
                optionType="CE",
                strikePrice=13800)

def getSpot():
    idx_instruments = [{'exchangeSegment': 1, 'exchangeInstrumentID': 'NIFTY 50'},
                   {'exchangeSegment': 1, 'exchangeInstrumentID': 'NIFTY BANK'}]
    spot_resp = xt.get_quote(
                Instruments=idx_instruments,
                xtsMessageCode=1504,
                publishFormat='JSON')
    spot=[]
    for i in range(len(idx_instruments)):
        listQuotes = json.loads(spot_resp['result']['listQuotes'][i])
        spot.append(listQuotes['IndexValue'])
        print(f'\n Spot price fetched as : {spot}') 
        spot=[13780.3, 30519.65]
    nfty50,nftyBank = [spot[i] for i in [0,1]]
    tr



