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



symbol = 41288  
initial_order = []
order_id = 1234
initial_order.append(order_id)
o2_id = 7894
initial_order.append(o2_id)
dict = {}
dict[symbol] = initial_order
dict[41288][1]

d = {41288: [1234, 7894],41287: [1237, 7897]}
[[i for i in d[x]] for x in d.keys()][0][0] 
for v in d.values():
    print(v)
    
    
dict1 = {}
dict1[symbol] = []
dict1[symbol].append(order_id)
print(dict1)

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

def squareOff(ids,symbol):
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










