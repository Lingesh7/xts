# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 21:44:33 2021

@author: mling
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta, TH
from XTConnect.Connect import XTSConnect
# from sys import exit
from nsetools import Nse
nse = Nse()
import time
import pandas as pd
import concurrent.futures
from threading import Timer
# import traceback
import logging
# from itertools import repeat
# import multiprocessing
# import schedule

logging.basicConfig(filename='../logs/Strategy_1_log.txt',level=logging.DEBUG,
                    format='%(asctime)s:%(name)s:%(message)s')


global ordersEid
ordersEid = {}
cdate = datetime.strftime(datetime.now(), "%d-%m-%Y")
kickTime = "14:37:30"
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
    logging.info("Main Login Successful")
    
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
    logging.debug('login initializing..')
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
        logging.info("Login Successful")
    else:
        logging.error("Not able to login..")
        
def auth_issue_fix(resp):
    logging.error(resp['description'])
    if (resp['description'] == "Please Provide token to Authenticate") \
                   or (resp["description"] == "Your session has been expired") \
                   or (resp["description"] == "Token/Authorization not found"):
                   logging.debug("Trying to login in again...")
                   login()

def nextThu_and_lastThu_expiry_date ():
    global weekly_exp, monthly_exp
    logging.info('Calculating weekly and monthly expiry dates..')
    
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
    logging.info(f'weekly expiry is : {weekly_exp}, monthly expiry is: {monthly_exp}')
 
def strkPrcCalc(ltp,base):
    strikePrice = base * round(ltp/base) 
    logging.info(('StrikePrice computed as : ', strikePrice))
    return strikePrice

def get_eID(symbol,ce_pe,expiry,strikePrice):
    logging.debug(f'Input of get_eID fn : {symbol}, {ce_pe},{expiry},{strikePrice}')
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
    if eID_resp['type'] != 'error':
        eid = int(eID_resp["result"][0]["ExchangeInstrumentID"])
        ordersEid[eid]=(oType)
        logging.info(f'Exchange Instrument ID : {eid}, {ordersEid}')
        return eid
    else:
        logging.error('Not able to get ExchangeInstrument ID')

def getOrderList():
    aa = 0
    logging.info('Retreiving OrderBook..') 
    while aa < 5:
        try:
           oBook_resp = xt.get_order_book()
           if oBook_resp['type'] != "error":
               orderList =  oBook_resp['result']
               logging.info('OrderBook result retreived success')
               return orderList
               break
           if oBook_resp['type'] == "error":
               auth_issue_fix(oBook_resp)
               continue
           else:
               raise Exception("Unkonwn error in getOrderList func")           
        except Exception:
            logging.exception("Can't extract order data..retrying")
            # traceback.print_exc()
            time.sleep(2)
            aa+=1

def getPositionList():
    a = 0
    logging.info('Retreiving position page..') 
    while a < 5:
        try:
           pos_resp = xt.get_position_daywise()
           if pos_resp['type'] != "error":
               positionList = pos_resp['result']['positionList']
               logging.info(f'Position page result retreived success, {positionList}')
               return positionList
               break
           elif pos_resp['type'] == "error":
               auth_issue_fix(pos_resp)
               continue
           else:
               raise Exception("Unkonwn error in getPositionoList func")
        except Exception:
            logging.exception("Can't extract position data...retrying")
            # traceback.print_exc()
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
        logging.info('PnL:', totalMTMdf)
        return totalMTMdf
    else:
        return totalMTMdf

def printPNL():
    logging.info('Time,PnL printing below')
    logging.info((time.strftime("%d-%m-%Y %H:%M:%S"),cur_PnL))
    
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
               auth_issue_fix(sq_off_resp)
               continue
           else:
               raise Exception("Unkonwn error in squareOff func")
        except Exception:
            logging.exception("Can't square-off open positions...retrying")
            # traceback.print_exc()
            time.sleep(2)
            ab+=1
             
def cancelOrder(OrderID):
    logging.info(f'Cancelling order: {OrderID} ')
    cancel_resp = xt.cancel_order(
        appOrderID=OrderID,
        orderUniqueIdentifier='FC_Cancel_Orders_1') 
    if cancel_resp['type'] != 'error':
        cancelled_SL_orderID = cancel_resp['result']['AppOrderID']
        logging.info(f'Cancelled SL order id : {cancelled_SL_orderID}')
    if cancel_resp['type'] == 'error':
        logging.error(f'Cancel order not processed for : {OrderID}')
        
def checkBalance():
    a = 0
    logging.info('Checking balance..')
    while a < 5:
        try:
           bal_resp = xt.get_balance()
           if bal_resp['type'] != "error":
               balanceList = bal_resp['result']['BalanceList']
               cashAvailable = balanceList[0]['limitObject']['marginAvailable']['CashMarginAvailable']
               logging.info(f'Balance retreived success, available cash : {cashAvailable}')
               return int(cashAvailable)
               break
           if bal_resp['type'] == "error":
               print(bal_resp["description"])
               if (bal_resp["description"] == "Please Provide token to Authenticate") \
                   or (bal_resp["description"] == "Your session has been expired") \
                   or (bal_resp["description"] == "Token/Authorization not found"):
                   logging.debug("Trying login in again...")
                   login()
                   continue
           else:
               raise Exception("Unkonwn error in checkBalance func")
        except Exception:
            logging.exception("Can't extract balance data...retrying :")
            # traceback.print_exc()
            time.sleep(2)
            a+=1
        
def prepareVars(ticker): 
    logging.info('Calculating everything before executing orders..')
    try:
        # for ticker in tickers:
        global net_cash,margin_ok, quantity,eID,strikePrice,nfty_ltp,bnknfty_ltp
        nfty_ltp=None
        bnknfty_ltp=None
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
        logging.info("Checking margin from user..")
        net_cash = checkBalance()
        margin_ok = int(net_cash) >= 55000
        logging.info(f''' 
              net_cash - {net_cash},
              strikePrice - {strikePrice},
              Nifty LTP - {nfty_ltp},
              BankNiftyLTP - {bnknfty_ltp}
              exchangeInstrumentID - {eID}
              ''')
        logging.info("All set from prepareVars func.. Giving a go for orders..")      
        return True
    except:
        logging.exception("Unable to reterive info like margin,strikePrice,nfty_ltp,bnknfty_ltp  to place order")
        return False

def placeOrder(symbol,buy_sell,quantity,t_type,sl=0):
    # Place an intraday stop loss order on NSE
    orderID = 0
    tradedPrice = 0
    # if buy_sell == "buy":
    #     t_type=xt.TRANSACTION_TYPE_BUY
    # elif buy_sell == "sell":
    #     t_type=xt.TRANSACTION_TYPE_SELL
    #     # quantity = mul*nifty_lot_size
    if sl == 0:
        o_type=xt.ORDER_TYPE_MARKET
    else:
        o_type="StopMarket"
        
    logging.info(f'placing order for --, {symbol}')
    order_resp = xt.place_order(exchangeSegment=xt.EXCHANGE_NSEFO,
                         exchangeInstrumentID= symbol ,
                         productType=xt.PRODUCT_MIS, 
                         orderType=o_type,                   
                         orderSide=t_type,
                         timeInForce=xt.VALIDITY_DAY,
                         disclosedQuantity=0,
                         orderQuantity=quantity,
                         limitPrice=0,
                         stopPrice=sl,
                         orderUniqueIdentifier="FC_MarketOrder"
                         )
    if order_resp['type'] != 'error':
        orderID = order_resp['result']['AppOrderID']            #extracting the order id from response
        logging.info(f'Order ID for {t_type} {symbol} is: {orderID}')
        # return orderID
        # loop = True
        a=0
        while a<3:
            orderLists = getOrderList()
            if orderLists:
                new_orders = [ol for ol in orderLists if ol['AppOrderID'] == orderID and ol['OrderStatus'] != 'Filled']  
                if not new_orders:
                    tradedPrice = float(next((orderList['OrderAverageTradedPrice'] for orderList in orderLists if orderList['AppOrderID'] == orderID and orderList['OrderStatus'] == 'Filled'),None))
                    print("traded price is: ", tradedPrice)
                    break
                    # loop = False
                else:
                    logging.info(f'Placed order {orderID} might be in Open or New Status, Hence retrying..{a}')
                    a+=1
                    if a==2:
                        logging.info('traded price is calculated as Zero, place SL order Manually')
                    time.sleep(3)
            else:
                logging.info('Unable to get OrderList inside place order function..')
                logging.info('..Hence traded price will retun as None')
                # return orderID, tradedPrice
    return orderID, tradedPrice
            
def placeOrderWithSL(symbol,buy_sell,quantity):
    # Place an intraday stop loss order on NSE
    # global orderID_dict
    logging.info('Placing Orders with StopLoss..')
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
    # tradedPrice = 0
    # quantity = mul*nifty_lot_size
    # bb = 0
    # while bb < 3:
    try:
        orderID,tradedPrice = placeOrder(symbol,buy_sell,quantity,t_type)
        logging.info(f'orderId and Traded price in try block of placeOrderWithSL: {orderID} and {tradedPrice}')
        print("orderId and Traded price in try block of placeOrderWithSL", orderID, tradedPrice)
        orderID_dict[symbol].append(orderID)
        orderID_dict[symbol].append(tradedPrice)
    except:
        logging.debug('Unable to place order in placeOrderWithSL func...')
        time.sleep(1)
        # bb+=1
    else:
        # get trade price of the last order processed from orderList
        logging.info('placing SL order for -- {symbol}')
        if tradedPrice != 0:
            stopPrice = round((tradedPrice+slPoints),2)
            logging.info(f'stopLoss price fixed as: {stopPrice}')
            orderID,tradedPrice = placeOrder(symbol,buy_sell,quantity,t_type_sl,sl=stopPrice)
            orderID_dict[symbol].append(orderID)
        else:
            logging.info('TradedPice is not available, Hence not placing SL order, TRY MANUALLY..')
            
    logging.info(f'orderDictionary from placeOrderWithSL {orderID_dict}')
    print("orderDictionary from placeOrderWithSL ", orderID_dict)
    return orderID_dict


def runOrders():
    global monitor,orderID_dictR
    orderID_dictR = {}
    monitor=False
    if margin_ok:
        logging.info('Required Margin Available.. Taking positions...')
        # print(f"symbol = {ticker} EID = {eID} expiry = {weekly_exp} strikePrice = {strikePrice} ")#.format(ticker,expiry,Otype,strikePrice,eID))
        with concurrent.futures.ProcessPoolExecutor() as executor:
            try:
                # orderID_dict = executor.map(placeOrderWithSL,eID,repeat('sell'),repeat(quantity))
                results = [executor.submit(placeOrderWithSL,i,'sell',quantity) for i in eID]
                print(results)
                for f in concurrent.futures.as_completed(results):
                    print('printiing f.results')
                    print(f.result())
                    orderID_dictR.update(f.result())
                    print('printiing orderID Dict value')
                    print(orderID_dictR)
                monitor = True
            except Exception:
                logging.exception('got exception - Something wrong with placing order:')
                # traceback.print_exc()
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
            logging.info('SquareOff Logic met...')
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


#maybe main()
if __name__ == '__main__':
    # login()
    ticker='NIFTY'
    go = prepareVars(ticker)
    if go:
        logging.info('required variables set-- ready to trigger orders at desired time')
        print("required variables set-- ready to trigger orders at desired time")
        nstart=True
        # ndate = datetime.strftime(datetime.now(), "%d-%m-%Y")
        while nstart:
            if (datetime.now() >= datetime.strptime(cdate + " " + kickTime, "%d-%m-%Y %H:%M:%S")):
                runOrders()
                nstart = False
            else:
                time.sleep(0.5)
        
        # print("starting multi funcs with threaded timer...")
        # if monitor:
        #     try:
        #         print("--- Entering SquareOffLogic Function after placing orders ---")
        #         runSqOffLogics()
        #         print("--- Sq-off Func Exit ---")
        #     except Exception as e:
        #         print("Something went wrong.. try closing the orders manually..", e)
        #     finally:
        #         print("-- Script Ended --")
                

        # else:
        #     print("No Orders Placed")
        #     print(" not started any multi funcs threaded timer")
    else:
        print("Vars not set properly...")

#################################
