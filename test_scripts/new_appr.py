# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 11:02:52 2020
Live execution - New Approach with Threaded Timer
@author: Welcome
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta, TH
from collections import defaultdict
from XTConnect.Connect import XTSConnect
from sys import exit
from nsetools import Nse
nse = Nse()
import time
import pandas as pd
import concurrent.futures
from threading import Timer
from operator import add,sub
import traceback
# from itertools import repeat
# import multiprocessing
# import schedule

global ordersEid
ordersEid = {}
cdate = datetime.strftime(datetime.now(), "%d-%m-%Y")
kickTime = "01:35:00"
wrapTime = "15:05:00"
globalSL = -1500
globalTarget = 3000


API_KEY = "ebaa4a8cf2de358e53c942"
API_SECRET = "Ojre664@S9"
XTS_API_BASE_URL = "https://xts-api.trading"
source = "WEBAPI"
xt = XTSConnect(API_KEY, API_SECRET, source)
login_resp = xt.interactive_login()
if login_resp['type'] != 'error':
    print("Login Successful")
    
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
        
def login():
    global xt
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
    if login_resp['type'] != 'error':
        print("Login Successful")

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
 
def strkPrcCalc(ltp,base):    
    return base * round(ltp/base)

def get_eID(symbol,ce_pe,expiry,strikePrice):
    if ce_pe == "ce":
        oType="CE"
    elif ce_pe == "pe":
        oType="PE"
    # print("expiry date caluclated as :", expiry)
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
    ordersEid[eid]=(oType)
    # return int(eID_resp["result"][0]["ExchangeInstrumentID"])
    return eid

def getOrderList():
    aa = 0
    while aa < 10:
        try:
           oBook_resp = xt.get_order_book()
           if oBook_resp['type'] != "error":
               orderList =  oBook_resp['result']
               return orderList
               break
           if oBook_resp['type'] == "error":
               print(oBook_resp["description"])
               if (oBook_resp["description"] == "Please Provide token to Authenticate") \
                   or (oBook_resp["description"] == "Your session has been expired") \
                   or (oBook_resp["description"] == "Token/Authorization not found"):
                   print("Trying login in again...")
                   login()
                   continue
           else:
               raise Exception("Unkonwn error in getOrderList func")           
        except Exception as e:
            print("got exception - can't extract order data..retrying", e)
            traceback.print_exc()
            aa+=1

def getPositionList():
    a = 0
    while a < 5:
        try:
           pos_resp = xt.get_position_daywise()
           if pos_resp['type'] != "error":
               positionList = pos_resp['result']['positionList']
               return positionList
               break
           if pos_resp['type'] == "error":
               print(pos_resp["description"])
               if (pos_resp["description"] == "Please Provide token to Authenticate") \
                   or (pos_resp["description"] == "Your session has been expired") \
                   or (pos_resp["description"] == "Token/Authorization not found"):
                   print("Trying login in again...")
                   login()
                   continue
           else:
               raise Exception("Unkonwn error in getPositionoList func")
        except Exception as e:
            print("got exception - Can't extract position data...retrying",e)
            traceback.print_exc()
            time.sleep(2)
            a+=1
            
def get_global_PnL():
    global pos_df
    totalMTMdf = 0.0
    positionList=getPositionList()
    if positionList:
        pos_df = pd.DataFrame(positionList)
        # posDf['MTM'].replace({',':''},regex=True).apply(pd.to_numeric,1).sum()
        totalMTMdf = pos_df['MTM'].replace({',':''},regex=True).apply(pd.to_numeric,1).sum()
        return totalMTMdf
    else:
        return totalMTMdf

def printPNL():
    print(time.strftime("%d-%m-%Y %H:%M:%S"),",",cur_PnL)
    
def squareOff(eid,symbol):
    ab = 0
    while ab < 10:
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
           break
        except:
            print("Unable to sq off positions... retrying")
            ab+=1
    
    if sq_off_resp['type'] == 'success':
        print(f"Squared-off for symbol {symbol} | {eid}")
        
def cancelOrder(OrderID):
    cancel_resp = xt.cancel_order(
        appOrderID=OrderID,
        orderUniqueIdentifier='FC_Cancel_Orders_1') 
    if cancel_resp['type'] != 'error':
            cancelled_SL_orderID = cancel_resp['result']['AppOrderID']
            print("Cancelled SL order id :", cancelled_SL_orderID)

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
         # print("Balance Available is: ", cashAvailable)
    else:
        print(bal_resp['description'])
        print("Unable to fetch Cash margins... try again..")
    return int(cashAvailable)
        
def prepareVars(ticker): 
    try:
        # for ticker in tickers:
        global net_cash, margin_ok, quantity,eID,strikePrice,nfty_ltp,bnknfty_ltp
        nextThu_and_lastThu_expiry_date ()
        # try:
        if ticker == "NIFTY":
             quantity = 75
             nfty_ltp = nse.get_index_quote("nifty 50")['lastPrice']
             strikePrice = strkPrcCalc(nfty_ltp,50)
             # margin_ok = int(checkBalance()) >= 1000000001  
        elif ticker == "BANKNIFTY":
            quantity = 25
            bnknfty_ltp = nse.get_index_quote("nifty bank")['lastPrice']
            strikePrice = strkPrcCalc(bnknfty_ltp,100)
            # margin_ok = int(checkBalance()) >= 1000000001 
        else:
            print("Enter a Valid symbol - NIFTY or BANKNIFTY")
        eID = [ (get_eID(ticker,i,weekly_exp,strikePrice)) for i in ['ce','pe'] ]
        # print("EID is :", eID)
        net_cash = checkBalance()
        margin_ok = int(net_cash) >= 55000
        print(f''' net_cash - {net_cash},
              strikePrice - {strikePrice},
              nfty_ltp - {nfty_ltp},
              eID - {eID}
              ''')
        return True
    except:
        print("unable to set variables to place order")
        return False

def placeOrderWithSL(symbol,buy_sell,quantity):
    # Place an intraday stop loss order on NSE
    # global orderID_dict
    orderID_dict = {}
    orderID_dict[symbol] = []
    
    if buy_sell == "buy":
        t_type=xt.TRANSACTION_TYPE_BUY
        t_type_sl=xt.TRANSACTION_TYPE_SELL
        slPoints = -15
    elif buy_sell == "sell":
        t_type=xt.TRANSACTION_TYPE_SELL
        t_type_sl=xt.TRANSACTION_TYPE_BUY
        slPoints = +15
    tradedPrice = 0
    # quantity = mul*nifty_lot_size
    try:
        print('placing order for --', symbol)
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
                         orderUniqueIdentifier="FirstChoice0"
                         )
        # extracting the order id from response
        if order_resp['type'] != 'error':
            orderID = order_resp['result']['AppOrderID']
            print(f''' Order ID for {t_type} {symbol} is: ", {orderID}''')
            orderID_dict[symbol].append(orderID)
            orderID_dict[symbol].append(symbol)
        elif order_resp['type'] == 'error':
            print("Error placing 1st Order.. Exiting...")
            exit()
            
        # get trade price of the last order processed from orderList
        orderList = getOrderList()
        for i in orderList:
            if orderID == i["AppOrderID"] and i["OrderStatus"] == 'Filled':
                tradedPrice = float(( i["OrderAverageTradedPrice"]))
                print('Traded price is: ', tradedPrice)
                break
        print('placing SL order for --', symbol)
        placed_SL_order = xt.place_order(exchangeSegment=xt.EXCHANGE_NSEFO,
                         exchangeInstrumentID= symbol ,
                         productType=xt.PRODUCT_MIS, 
                         orderType="StopMarket",                   
                         orderSide=t_type_sl,
                         timeInForce=xt.VALIDITY_DAY,
                         disclosedQuantity=0,
                         orderQuantity=quantity,
                         limitPrice=0,
                         stopPrice=round((tradedPrice+slPoints),2),
                         orderUniqueIdentifier="FirstChoice1"
                         )
        if placed_SL_order['type'] != 'error':
            placed_SL_orderID = placed_SL_order['result']['AppOrderID']
            print("order id for StopLoss :", placed_SL_orderID)
            orderID_dict[symbol].append(placed_SL_orderID)
        else:
             print("Error placing SL Order.. try again manually...")
        return orderID_dict
    except:
        # return False
        # monitor=False
        print("Orders Not Placed..")
            
def runOrders():
    global monitor,orderID_dictR
    orderID_dictR = {}
    monitor=False
    if margin_ok:
        print("Required Margin Available.. Taking positions...")
        # print(f"symbol = {ticker} EID = {eID} expiry = {weekly_exp} strikePrice = {strikePrice} ")#.format(ticker,expiry,Otype,strikePrice,eID))
        with concurrent.futures.ProcessPoolExecutor() as executor:
            try:
                # orderID_dict = executor.map(placeOrderWithSL,eID,repeat('sell'),repeat(quantity))
                results = [executor.submit(placeOrderWithSL,i,'sell',quantity) for i in eID]
                # orderID_dict = results
                for f in concurrent.futures.as_completed(results):
                    orderID_dictR.update(f.result())
                    print(f.result())
                monitor = True
            except Exception as e:
                print("got exception - Something wrong with placing order:", e)
                traceback.print_exc()
    else:
        print(f''' \t Margin is less to place orders... 
             Required cash : 55000
             But cash available is: {net_cash}
             Exiting without placing any orders.. 
                  ''')     
 
def runSqOffLogics():
    login()
    # if monitor:
    global cur_PnL
    print("--- ---\n")
    print('''Entering runSqOffLogics func,\n \t This logic runs till the end of the script and 
              checks SL/TARGET/TIMEings \n''')
    # cdate = datetime.strftime(datetime.now(), "%d-%m-%Y")
    check=True
    while check:
        # print("--- getting cur_PnL ---")
        cur_PnL = get_global_PnL()
        if (cur_PnL < globalSL) or (cur_PnL >= globalTarget) or (datetime.now() >= datetime.strptime(cdate + " " + wrapTime, "%d-%m-%Y %H:%M:%S")):
            print("/n SquareOff Logic met...")
            # closing all open positions             # not taking getPositionList() bcoz
            # positionList = getPositionList()      # get_global_PnL() has the latest pos_df
            # pos_df = pd.DataFrame(positionList)   # also runs every 2 secs so no need to get again
            for i in range(len(pos_df)):
                if int(pos_df["Quantity"].values[i]) != 0:
                    symbol=pos_df['TradingSymbol'].values[i]
                    eid = pos_df["ExchangeInstrumentId"].values[i]
                    squareOff(eid,symbol)
            print("Position Squareoff Completed ")
            
            #closing all pending orders
            # orderBook = getOrderBook()
            # orderList=xt.get_order_book()['result']
            orderList = getOrderList()
            ord_df = pd.DataFrame(orderList)
            pending = ord_df[ord_df['OrderStatus'].isin(["New","Open","Partially Filled"])]["AppOrderID"].tolist()
            drop = []
            attempt = 0
            while len(pending)>0 and attempt<5:
                pending = [j for j in pending if j not in drop]
                for order in pending:
                    try:
                        cancelOrder(order)
                        drop.append(order)
                    except:
                        print("unable to delete order id : ",order)
                        attempt+=1
            else:
                print("No Open orders to Cancel")
                    
            check=False # exit this long run main loop
        else:
            # print("Sq-off logic running parallelly")
            time.sleep(2)

def createOrderDicts():
    dd = defaultdict(list)
    for d in (ordersEid, orderID_dictR): 
        for key, value in d.items():
            dd[key].append(value)
    oIDs={}
    for k,v in dd.items():
        i = iter(v)
        b = dict(zip(i, i))
        oIDs.update(b)
    return oIDs

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
                         orderUniqueIdentifier="FirstChoice_repairOrder"
                         )
            break
        except:
            print("Unable to place repair order... retrying")
            bb+=1
            
        # extracting the order id from response
        if order_resp['type'] != 'error':
            orderID = order_resp['result']['AppOrderID']
            print(f''' Order ID for {t_type} {symbol} is: ", {orderID}''')
        elif order_resp['type'] == 'error':
            print("Error placing Order.. Exiting...")

def runRepairActions(c_p):
    # global oIDs
    oIDs = createOrderDicts()
    print("Dictionary of orders :", oIDs)
    print(" --- symbol hits +/- 40 --- ")
    # positionList = getPositionList()
    # pos_df = pd.DataFrame(positionList)
    pos_eids = pos_df[ (pos_df['Quantity'] != '0') ]["ExchangeInstrumentId"].astype(int).values.tolist()
    cp_pos_eids = [i for i in oIDs[c_p] if i in pos_eids]
    
    print(f"--------------------- Sq-Off {c_p} positions -----------------------")
    for ids in cp_pos_eids:
        squareOff(ids,"Call Option SELL")
    print(f"---------------------  Sq-Off {c_p} Completed -------------------------")
    
    print(f"------------------ Cancelling SL-M {c_p} Orders --------------------")
    orderList = getOrderList()
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
    print(f"------------------ Cancel SL-M {c_p} Orders completed -------------")
    
    print("\n---------Placing a sell {c_p} Order for next strikeprice ----------")
    if c_p == 'CE':
        sign=add
        otyp='ce'
    if c_p == 'PE':
        sign=sub
        otyp='pe'
    eid1 = get_eID(ticker, otyp, weekly_exp, sign(strikePrice,50))
    placeOrder(eid1, 'sell', quantity)
    print("----Stopping repeatedTimer------")
    rt1.stop()
    
def repairStrategy(ticker):
    # if monitor:
    # global oIDs
    # oIDs = createOrderDicts()
    # print("Dictionary of orders :", oIDs)
    curPrc=nse.get_index_quote("nifty 50")['lastPrice']
    print(f''' Cuurent NFTY PRICE = {curPrc} ''')
    try:
        if curPrc > nfty_ltp+40:
            runRepairActions('CE')
    
        elif curPrc < nfty_ltp-40:
            runRepairActions('PE')
       
        else:
            # print("Repair check running...")
            print(".")
    except Exception() as e:
         print("got exception - Something wrong with runRepairActions :", e)
         traceback.print_exc()   
           
#maybe main()
if __name__ == '__main__':
    # login()
    ticker='NIFTY'
    go = prepareVars(ticker)
    if go:
        print("required variables set-- ready to trigger orders at desired time")
        nstart=True
        # ndate = datetime.strftime(datetime.now(), "%d-%m-%Y")
        while nstart:
            if (datetime.now() >= datetime.strptime(cdate + " " + kickTime, "%d-%m-%Y %H:%M:%S")):
                runOrders()
                nstart = False
            else:
                time.sleep(0.5)
        
        print("starting multi funcs with threaded timer...")
        if monitor:
            rt1 = RepeatedTimer(5, repairStrategy, ticker) # it auto-starts, no need of rt.start()
            # rt2 = RepeatedTimer(15, printPNL)
            try:
                print("--- Entering SquareOffLogic Function after placing orders ---")
                runSqOffLogics()
                print("--- Sq-off Func Exit ---")
            finally:
                print("finally block")
                rt1.stop() # better in a try/finally block to make sure the program ends!
                # rt2.stop()
                print("END")
                
            # if monitor:
            # t1 = threading.Thread(target=runSqOffLogics)
            # t1.start()
            # t1.join()
        else:
            print("No Orders Placed")
            print(" not started any multi funcs threaded timer")
    else:
        print("Vars not set properly...")

#################################
