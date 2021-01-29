# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 21:44:33 2021

@author: mling
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta, TH
from XTConnect.Connect import XTSConnect
# from sys import exit
# from nsetools import Nse
# nse = Nse()
import time
import pandas as pd
import concurrent.futures
from threading import Timer
import json
# import traceback
import logging
# from itertools import repeat
# import multiprocessing
# import schedule

logging.basicConfig(filename='../logs/A1_Strategy_1_log.txt',level=logging.INFO,
                    format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')


global ordersEid
global new_dict
new_dict={}
# new_dict = {k:[] for k in ['oo','tt','qq','ss','sl']}
ordersEid = {}
ordersEid= {k:[] for k in ['oty','ss']}

cdate = datetime.strftime(datetime.now(), "%d-%m-%Y")
kickTime = "15:22:00"
wrapTime = "15:24:00"
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

def getSpot():
    try:
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
        logging.info(f'\n Spot price fetched as : {spot}') 
        nfty50,nftyBank = [spot[i] for i in [0,1]]
    except Exception:
        logging.exception('Unable to getSpot from index')
    else:
        return nfty50,nftyBank
        
def strkPrcCalc(spot,base):
    strikePrice = base * round(spot/base) 
    logging.info(f'StrikePrice computed as : {strikePrice}')
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
        ordersEid['oty'].append(oType)
        ordersEid['ss'].append(str(eid))
        # ordersEid[eid]=(oType)
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
               # logging.info(f'Position page result retreived success, {positionList}')
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
        
def squareOff(eid,symb):
    ab = 0
    logging.info(f'squaring-off for : {symb} - {eid}')
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
               logging.info(f'Squared-off for symbol {symb} - {eid}')
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
        nfty_ltp,bnknfty_ltp=None,None
        nextThu_and_lastThu_expiry_date ()
        nfty_ltp,bnknfty_ltp=getSpot()
        # try:
        if ticker == "NIFTY":
             quantity = 75
             # nfty_ltp = nse.get_index_quote("nifty 50")['lastPrice']
             strikePrice = strkPrcCalc(nfty_ltp,50)
             # margin_ok = int(checkBalance()) >= 1000000001  
        elif ticker == "BANKNIFTY":
            quantity = 25
            # bnknfty_ltp = nse.get_index_quote("nifty bank")['lastPrice']
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

def placeOrderwithSL(symbol,buy_sell,quantity):
    logging.info(' \n Placing Orders with StopLoss.. \n')
    orderID_dict = {}
    orderID_dict[symbol] = []
    # Place an intraday stop loss order on NSE
    orderID = 0
    tradedPrice = 0
    
    new_dict['ss']=str(symbol)
    new_dict['qq']=(quantity)
    
    if buy_sell == "buy":
        t_type=xt.TRANSACTION_TYPE_BUY
        t_type_sl=xt.TRANSACTION_TYPE_SELL
        slPoints = -15
    elif buy_sell == "sell":
        t_type=xt.TRANSACTION_TYPE_SELL
        t_type_sl=xt.TRANSACTION_TYPE_BUY
        slPoints = +15
    try:
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
                         orderUniqueIdentifier="FC_MarketOrder"
                         )
        if order_resp['type'] != 'error':
            orderID = order_resp['result']['AppOrderID']            #extracting the order id from response
            new_dict['oo']=(orderID)
            logging.info(f' \n Order ID for {t_type} {symbol} is: {orderID} \n')
            # return orderID
            # loop = True
            a=0
            while a<3:
                orderLists = getOrderList()
                if orderLists:
                    new_orders = [ol for ol in orderLists if ol['AppOrderID'] == orderID and ol['OrderStatus'] != 'Filled']  
                    if not new_orders:
                        tradedPrice = float(next((orderList['OrderAverageTradedPrice'] for orderList in orderLists if orderList['AppOrderID'] == orderID and orderList['OrderStatus'] == 'Filled'),None))
                        new_dict['tt']=(tradedPrice)
                        logging.info(f"traded price is: {tradedPrice}")
                        break
                        # loop = False
                    else:
                        logging.info(f'\n Placed order {orderID} might be in Open or New Status, Hence retrying..{a}')
                        a+=1
                        if a==2:
                            logging.info('\n traded price is calculated as Zero, place SL order Manually')
                        time.sleep(1)
                else:
                    logging.info('\n  Unable to get OrderList inside place order function..')
                    logging.info('..Hence traded price will retun as None \n ')
                    
        orderID_dict[symbol].append(symbol)
        orderID_dict[symbol].append(orderID)
        orderID_dict[symbol].append(tradedPrice)
    except Exception():
        logging.exception('Unable to place order in placeOrderWithSL func...')
        time.sleep(1)        
    else:
        if tradedPrice != 0:
            logging.info(f'\n Placing StopLoss order for {symbol}')
            stopPrice = round((tradedPrice+slPoints),2)
            logging.info(f'stopLoss price fixed as: {stopPrice}')
            sl_order_resp = xt.place_order(exchangeSegment=xt.EXCHANGE_NSEFO,
                         exchangeInstrumentID= symbol ,
                         productType=xt.PRODUCT_MIS, 
                         orderType="StopMarket",                   
                         orderSide=t_type_sl,
                         timeInForce=xt.VALIDITY_DAY,
                         disclosedQuantity=0,
                         orderQuantity=quantity,
                         limitPrice=0,
                         stopPrice=stopPrice,
                         orderUniqueIdentifier="FC_MarketOrder"
                         )
            if sl_order_resp['type'] != 'error':
                orderID = sl_order_resp['result']['AppOrderID']            #extracting the order id from response
                new_dict['sl']=(orderID)
                orderID_dict[symbol].append(orderID)
                logging.info(f'\n  StopLoss Order ID for {t_type_sl} {symbol} is: {orderID} \n')
        else:
            logging.info(' \n TradedPice is not available, Hence not placing SL order, TRY MANUALLY.. \n')
            
    # logging.info(f'orderDictionary from placeOrderWithSL {orderID_dict}')
    logging.info(f"orderDictionary from new place order func (orderID_dict)  {orderID_dict}")
    logging.info(f" \n new DICT  from new place order func (new_dict)  {new_dict} \n")
    # return orderID_dict, new_dict
    return new_dict
                    
def runOrders():
    global monitor,orderID_dictR,new_dictR
    orderID_dictR = {}
    new_dictR=[]
    monitor=False
    if margin_ok:
        logging.info('Required Margin Available.. Taking positions...')
        # print(f"symbol = {ticker} EID = {eID} expiry = {weekly_exp} strikePrice = {strikePrice} ")#.format(ticker,expiry,Otype,strikePrice,eID))
        with concurrent.futures.ProcessPoolExecutor() as executor:
            try:
                # orderID_dict = executor.map(placeOrderWithSL,eID,repeat('sell'),repeat(quantity))
                results = [executor.submit(placeOrderwithSL,i,'sell',quantity) for i in eID]
                for f in concurrent.futures.as_completed(results):
                    # print('printiing f.results')
                    # print(f.result())
                    # orderID_dictR.update(f.result())
                    new_dictR.append(f.result())
                logging.info(f'printing new_dictR value : {new_dictR}')
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

def getPnL():
    # k=0
    logging.info('Checking CurPnL for this strategy..')
    # while k<2:
    try:
        # print(j)
        # logging.info('Checking CurPnL for this strategy..')
        # login()
        odf=pd.DataFrame(new_dictR)
        eid_df =pd.DataFrame(ordersEid)
        df = odf.merge(eid_df, how='left')
        instruments=[]
        for i in range(len(df)):
            instruments.append({'exchangeSegment': 2, 'exchangeInstrumentID': df['ss'].values[i]})
            # print(instruments)
        # logging.info(f'sending subscription for : {instruments}')    
        unsubs_resp=xt.send_unsubscription(Instruments=instruments,xtsMessageCode=1502)
        # if (unsubs_resp['type'] == 'error') and (unsubs_resp['description'] == 'Invalid Token'):
        #     login() 
        logging.info(unsubs_resp['description'])
        subs_resp = xt.send_subscription(Instruments=instruments,xtsMessageCode=1502)
        if subs_resp['type'] == 'success':
            logging.info(subs_resp['description'])
            ltp=[]
            for i in range(len(df)):
                listQuotes = json.loads(subs_resp['result']['listQuotes'][i])
                ltp.append(listQuotes['Touchline']['LastTradedPrice'])
            # logging.info(f'LastTradedPrice fetched as : {ltp}')
            df['ltp']=ltp
            df['pnl']=(df['ltp']-df['tt'])*df['qq'] 
            cur_PnL=round(df['pnl'].sum(),2) 
            logging.info(f' DF is : \n {df} \n')
            logging.info(' Time    ,    PnL')
            logging.info((time.strftime("%d-%m-%Y %H:%M:%S"),cur_PnL))
            # logging.info(time.strftime("%d-%m-%Y %H:%M:%S"),cur_PnL)
        return cur_PnL    
        # break
    except Exception:
        logging.exception('Failed to get PNL')
        login()
        # k+=1
            
def runSqOffLogics():
    login()
    logging.info('''\n Entering runSqOffLogics func,\n \t This logic runs till the end of the script and 
              checks SL/TARGET/TIMEings \n''')
    check=True
    while check:
        # print("--- getting cur_PnL ---")
        cur_PnL = getPnL()
        if cur_PnL:
            if (cur_PnL < globalSL) or (cur_PnL >= globalTarget) or (datetime.now() >= datetime.strptime(cdate + " " + wrapTime, "%d-%m-%Y %H:%M:%S")):
                logging.info('SquareOff Logic met...')
                print("\n SquareOff Logic met...")
                
                # closing all open positions             # not taking getPositionList() bcoz
                positionList = getPositionList()      # get_global_PnL() has the latest pos_df
                if positionList:
                    pos_df = pd.DataFrame(positionList)   # also runs every 2 secs so no need to get again
                    for i in range(len(pos_df)):
                        if int(pos_df["Quantity"].values[i]) != 0:
                            symb=pos_df['TradingSymbol'].values[i]
                            eid = pos_df["ExchangeInstrumentId"].values[i]
                            squareOff(eid,symb)
                    # logging.info("Position Squareoff Completed ")
                else:
                    logging.info('Unable to get positionList to square-off. Try manually..')
                
                #closing all pending orders
                orderList = getOrderList()
                if orderList:
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
                    logging.info('Unable to get orderList to square-off. Try manually..')
        
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
         
        print("starting multi funcs with threaded timer...")
        if monitor:
            try:
                print("--- Entering SquareOffLogic Function after placing orders ---")
                runSqOffLogics()
                print("--- Sq-off Func Exit ---")
            except Exception as e:
                print("Something wrong with SquareoffLogic func..", e)
            finally:
                print("-- Script Ended --")
        else:
            print("No Orders Placed")
            print(" not started any multi funcs threaded timer")
    else:
        print("Vars not set properly...")

#################################
