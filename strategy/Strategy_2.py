# -*- coding: utf-8 -*-
"""
Created on Thu Feb 01 2021 21:44:33 2021
Strategy_2 
@author: mling
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta, TH
from XTConnect.Connect import XTSConnect
from threading import Timer
import time
import json
import logging
import pandas as pd
import concurrent.futures

# from itertools import repeat
# import multiprocessing
# import schedule
# from sys import exit
# import traceback

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

filename='../logs/Strategy2_log_'+datetime.strftime(datetime.now(), "%d%m%Y_%H%M")+'.txt'

file_handler = logging.FileHandler(filename)
# file_handler=logging.handlers.TimedRotatingFileHandler(filename, when='d', interval=1, backupCount=5)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

global ordersEid
global new_dict
global pnl_dump
global mdf

ordersEid= {k:[] for k in ['oty','ss']}
new_dict={}
pnl_dump=[]
mdf=pd.DataFrame(columns=['ordrtyp','ss','qq','oo','tt','ltp','pnl'])
# ordersEid = {}
# new_dict = {k:[] for k in ['oo','tt','qq','ss','sl']}

cdate = datetime.strftime(datetime.now(), "%d-%m-%Y")
kickTime = "15:03:00"
wrapTime = "15:15:00"
globalSL = -1500
globalTarget = 3000

API_KEY = "ebaa4a8cf2de358e53c942"
API_SECRET = "Ojre664@S9"
XTS_API_BASE_URL = "https://xts-api.trading"
source = "WEBAPI"
xt = XTSConnect(API_KEY, API_SECRET, source)
login_resp = xt.interactive_login()
if login_resp['type'] != 'error':
    logger.info("Main Login Successful")
    
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
    logger.debug('login initializing..')
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
        logger.info("Login Successful")
    else:
        logger.error("Not able to login..")
        
def auth_issue_fix(resp):
    logger.error(f'{resp["description"]}')
    if (resp['description'] == "Please Provide token to Authenticate") \
                   or (resp["description"] == "Your session has been expired") \
                   or (resp["description"] == "Token/Authorization not found"):
                   logger.debug("Trying to login in again...")
                   login()

def nextThu_and_lastThu_expiry_date ():
    global weekly_exp, monthly_exp
    logger.info('Calculating weekly and monthly expiry dates..')
    
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
    logger.info(f'weekly expiry is : {weekly_exp}, monthly expiry is: {monthly_exp}')

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
        # logger.info(f'Spot price fetched as : {spot}') 
        # nfty50,nftyBank = [spot[i] for i in [0,1]]
    except Exception:
        logger.exception('Unable to getSpot from index')
    else:
        # return nfty50,nftyBank
        return spot
        
def strkPrcCalc(spot,base):
    strikePrice = base * round(spot/base)
    logger.info(f'StrikePrice computed as : {strikePrice}')
    return strikePrice

def get_eID(symbol,ce_pe,expiry,strikePrice):
    logger.info(f'Input of get_eID fn : {symbol}, {ce_pe},{expiry},{strikePrice}')
    weekday = datetime.today().weekday()
    if ce_pe == "ce":
        oType="CE"
        if weekday != 3:
            logger.info('Today is not Thursday. Hence straddle')
            strikePrice=strikePrice+50
    elif ce_pe == "pe":
        oType="PE"
        if weekday != 3:
            logger.info('Today is not Thursday. Hence straddle')
            strikePrice=strikePrice-50
    # print("expiry date caluclated as :", expiry)
    eID_resp = xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol=symbol,
                expiryDate=expiry,
                optionType=oType,
                strikePrice=strikePrice)
    # print('Option Symbol:', str(response))
    # logger.info(f'{eID_resp}')
    if (eID_resp['type'] != 'error') and (eID_resp["result"]):
        eid = int(eID_resp["result"][0]["ExchangeInstrumentID"])
        ordersEid['oty'].append(oType)
        ordersEid['ss'].append(str(eid))
        # ordersEid[eid]=(oType)
        logger.info(f'Exchange Instrument ID : {eid}, {ordersEid}')
        return eid
    else:
        logger.error('Not able to get ExchangeInstrument ID')
        raise Exception('Not able to get ExchangeInstrument ID')

def getOrderList():
    aa = 0
    logger.info('Retreiving OrderBook..') 
    while aa < 5:
        try:
           oBook_resp = xt.get_order_book()
           if oBook_resp['type'] != "error":
               orderList =  oBook_resp['result']
               logger.info('OrderBook result retreived success')
               return orderList
               break
           if oBook_resp['type'] == "error":
               auth_issue_fix(oBook_resp)
               continue
           else:
               raise Exception("Unkonwn error in getOrderList func")           
        except Exception:
            logger.exception("Can't extract order data..retrying")
            # traceback.print_exc()
            time.sleep(2)
            aa+=1

def getPositionList():
    a = 0
    logger.info('Retreiving position page..') 
    while a < 5:
        try:
           pos_resp = xt.get_position_daywise()
           if pos_resp['type'] != "error":
               positionList = pos_resp['result']['positionList']
               # logger.info(f'Position page result retreived success, {positionList}')
               return positionList
               break
           elif pos_resp['type'] == "error":
               auth_issue_fix(pos_resp)
               continue
           else:
               raise Exception("Unkonwn error in getPositionoList func")
        except Exception:
            logger.exception("Can't extract position data...retrying")
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
        logger.info('PnL:', totalMTMdf)
        return totalMTMdf
    else:
        return totalMTMdf
        
def squareOff(eid,symb,qty):
    ab = 0
    logger.info(f'squaring-off for : {symb} - {eid}')
    while ab < 5:
        try:
           sq_off_resp = xt.squareoff_position(
                exchangeSegment=xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=eid,
                productType=xt.PRODUCT_MIS,
                squareoffMode=xt.SQUAREOFF_DAYWISE,
                # positionSquareOffQuantityType=xt.SQUAREOFFQUANTITY_PERCENTAGE,
                positionSquareOffQuantityType=xt.SQUAREOFFQUANTITY_EXACTQUANTITY,
                squareOffQtyValue=qty,
                blockOrderSending=True,
                cancelOrders=True)
           if sq_off_resp['type'] != "error":
               logger.info(f'Squared-off for symbol {symb} - {eid}')
               break
           if sq_off_resp['type'] == "error":
               auth_issue_fix(sq_off_resp)
               continue
           else:
               raise Exception("Unkonwn error in squareOff func")
        except Exception:
            logger.exception("Can't square-off open positions...retrying")
            # traceback.print_exc()
            time.sleep(2)
            ab+=1
             
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
        
def checkBalance():
    a = 0
    logger.info('Checking balance..')
    while a < 5:
        try:
           login()
           bal_resp = xt.get_balance()
           if bal_resp['type'] != "error":
               balanceList = bal_resp['result']['BalanceList']
               cashAvailable = balanceList[0]['limitObject']['marginAvailable']['CashMarginAvailable']
               logger.info(f'Balance retreived success, available cash : {cashAvailable}')
               return int(cashAvailable)
               break
           if bal_resp['type'] == "error":
               #print(bal_resp["description"])
               auth_issue_fix(bal_resp)
               continue
           else:
               raise Exception("Unkonwn error in checkBalance func")
        except Exception:
            logger.exception("Can't extract balance data...retrying :")
            # traceback.print_exc()
            time.sleep(2)
            a+=1
        
def prepareVars(ticker): 
    logger.info('Calculating everything before executing orders..')
    try:
        # for ticker in tickers:
        global net_cash,margin_ok, quantity,eID,strikePrice,nfty_ltp,bnknfty_ltp
        nfty_ltp,bnknfty_ltp=None,None
        nextThu_and_lastThu_expiry_date ()
        spotList=getSpot()
        # try:
        if ticker == "NIFTY":
             quantity = 75
             # nfty_ltp = nse.get_index_quote("nifty 50")['lastPrice']
             nfty_ltp=spotList[0]
             strikePrice = strkPrcCalc(nfty_ltp,50)
             # margin_ok = int(checkBalance()) >= 1000000001  
        elif ticker == "BANKNIFTY":
            quantity = 25
            # bnknfty_ltp = nse.get_index_quote("nifty bank")['lastPrice']
            bnknfty_ltp=spotList[1]
            strikePrice = strkPrcCalc(bnknfty_ltp,100)
            # margin_ok = int(checkBalance()) >= 1000000001 
        else:
            logger.info("Enter a Valid symbol - NIFTY or BANKNIFTY")
        eID = [ (get_eID(ticker,i,weekly_exp,strikePrice)) for i in ['ce','pe'] ]
        # #print("EID is :", eID)
        logger.info("Checking margin from user..")
        net_cash = checkBalance()
        margin_ok = int(net_cash) >= 55000
        logger.info(f''' 
              net_cash - {net_cash},
              strikePrice - {strikePrice},
              Nifty Spot - {nfty_ltp},
              BankNifty Spot - {bnknfty_ltp}
              exchangeInstrumentID - {eID}
              ''')
        logger.info("All set from prepareVars func.. Giving a go for orders..")      
        return True
    except:
        logger.exception("Unable to reterive info like margin,strikePrice,nfty_ltp,bnknfty_ltp to place order")
        return False

def placeOrder(symbol,buy_sell,quantity,ordrtyp):
    logger.info('Placing Orders.. \n')
    # Place an intraday stop loss order on NSE
    orderID = 0
    tradedPrice = 0
    new_dict['ordrtyp']=ordrtyp
    new_dict['ss']=str(symbol)
    new_dict['qq']=(quantity)
    
    if buy_sell == "buy":
        t_type=xt.TRANSACTION_TYPE_BUY
    elif buy_sell == "sell":
        t_type=xt.TRANSACTION_TYPE_SELL
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
            logger.info(f' \n Order ID for {t_type} {symbol} is: {orderID} \n')
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
                        logger.info(f"traded price is: {tradedPrice}")
                        break
                        # loop = False
                    else:
                        logger.info(f'\n Placed order {orderID} might be in Open or New Status, Hence retrying..{a}')
                        a+=1
                        time.sleep(1)
                else:
                    logger.info('\n  Unable to get OrderList inside place order function..')
                    logger.info('..Hence traded price will retun as None \n ')
        elif order_resp['type'] == 'error':
            logger.info(f'Order not placed for - {symbol} ')
            raise Exception('Order not placed')
    except Exception():
        logger.exception('Unable to place order in placeOrder func...')
        time.sleep(1)
    else:
        return new_dict
                    
def runOrders():
    global monitor,orderID_dictR,new_dictR
    orderID_dictR = {}
    new_dictR=[]
    monitor=False
    if margin_ok:
        logger.info('Required Margin Available.. Taking positions...')
        # #print(f"symbol = {ticker} EID = {eID} expiry = {weekly_exp} strikePrice = {strikePrice} ")#.format(ticker,expiry,Otype,strikePrice,eID))
        with concurrent.futures.ProcessPoolExecutor() as executor:
            try:
                # orderID_dict = executor.map(placeOrderWithSL,eID,repeat('sell'),repeat(quantity))
                results = [executor.submit(placeOrder,i,'sell',quantity,'Entry') for i in eID]
                for f in concurrent.futures.as_completed(results):
                    new_dictR.append(f.result())
                logger.info(f'printing new_dictR value : {new_dictR}')
                monitor = True
            except Exception:
                logger.exception('got exception - Something wrong with placing order:')
                # traceback.print_exc()
    else:
        logger.info(f''' 
             Margin is less to place orders... 
             Required cash : 55000
             But cash available is: {net_cash}
             Exiting without placing any orders.. 
                  ''')     

def getPnL():
    logger.info('Checking CurPnL for this strategy..')
    global mdf
    try:
        # #print(j)
        # logger.info('Checking CurPnL for this strategy..')
        # login()
        odf=pd.DataFrame(new_dictR)
        eid_df =pd.DataFrame(ordersEid)
        fdf = odf.merge(eid_df, how='left')
        instruments=[]
        for i in range(len(fdf)):
            instruments.append({'exchangeSegment': 2, 'exchangeInstrumentID': fdf['ss'].values[i]})
            # #print(instruments)
        # logger.info(f'sending subscription for : {instruments}')    
        xt.send_unsubscription(Instruments=instruments,xtsMessageCode=1502)
        # logger.info(unsubs_resp['description'])
        subs_resp=xt.send_subscription(Instruments=instruments,xtsMessageCode=1502)
        if subs_resp['type'] == 'success':
            # logger.info(subs_resp['description'])
            ltp=[]
            for i in range(len(fdf)):
                listQuotes = json.loads(subs_resp['result']['listQuotes'][i])
                ltp.append(listQuotes['Touchline']['LastTradedPrice'])
            # logger.info(f'LastTradedPrice fetched as : {ltp}')
            fdf['ltp']=ltp
            fdf['pnl']=(fdf['tt']-fdf['ltp'])*fdf['qq']
            mdf=pd.concat([mdf,fdf.query('qq != 0')]).drop_duplicates(['ss'],keep='last')
            cur_PnL=round(mdf['pnl'].sum(),2) 
            logger.info(f' DF is : \n {mdf} \n')
            # logger.info(' Time    ,    PnL')
            logger.info((time.strftime("%d-%m-%Y %H:%M:%S"),cur_PnL))
            # logger.info(time.strftime("%d-%m-%Y %H:%M:%S"),cur_PnL)
        return cur_PnL    
        # break
    except Exception:
        logger.exception('Failed to get PNL')
        login()
        
def isSLHit():
    odf=pd.DataFrame(new_dictR)
    orderList=getOrderList()
    ordr_df=pd.DataFrame(orderList)
    pdm =pd.merge(odf,ordr_df, left_on=('sl'),right_on=('AppOrderID'))
    return pdm['OrderStatus'].isin(['Trigger Pending']).tolist()

def repairStrategy(ticker):
    spotList=getSpot()
    if ticker=='NIFTY':
        cur_prc=spotList[0]
    elif ticker=='BANKNIFTY':
        cur_prc=spotList[1]
    logger.info(f'Cur price of NIFTY is: {cur_prc}')
    logger.info(f'Points changed: {round(cur_prc-nfty_ltp,2)}')
    try:
        if cur_prc > nfty_ltp+40:
            logger.info(f'{ticker} hits +40')
            logger.info('SquaringOff CE position..')
            pos=pd.DataFrame(new_dictR)
            eid_df=pd.DataFrame(ordersEid)
            ce_df=pos.merge(eid_df, how='left')
            ids=ce_df[ce_df['oty']=='CE']['ss'].tolist()
            qt_y=ce_df[ce_df['oty']=='CE']['qq'].tolist()
            idqty = zip(ids,qt_y)
            for i_d,qty in idqty:
                logger.info(f'valid repair sq-off id {i_d}')
                squareOff(i_d, 'Repair CE',qty)
                logger.info('this is after sqoff and below code to change qty to 0')
                logger.info('Changing the qty of to 0 in new_dictR')
                for dtc in new_dictR:
                    if dtc['ss'] == i_d:
                        dtc.update({'qq':0})
            logger.info('Placing another order..')        
            eid1 = get_eID(ticker,'ce',weekly_exp,(strikePrice+50))
            logger.info(f'Repair order eid is: {eid1}')
            frsh=placeOrder(eid1,'sell',quantity,'RepairOnce')
            new_dictR.append(frsh)
            logger.info("----Stopping repeatedTimer------")
            rt1.stop()
        elif cur_prc < nfty_ltp-40:
            logger.info(f'{ticker} hits -40')
            logger.info('SquaringOff PE position..')
            pos=pd.DataFrame(new_dictR)
            eid_df=pd.DataFrame(ordersEid)
            pe_df=pos.merge(eid_df, how='left')
            ids=pe_df[pe_df['oty']=='PE']['ss'].tolist()
            qt_y=ce_df[ce_df['oty']=='PE']['qq'].tolist()
            idqty = zip(ids,qt_y)
            for i_d,qty in idqty:
                squareOff(i_d, 'Repair PE',qty)
                logger.info('Changing the qty of to 0 in new_dictR')
                for dtc in new_dictR:
                    if dtc['ss'] == i_d:
                        dtc.update({'qq':0})
            logger.info('Placing another order for PE')        
            eid2 = get_eID(ticker,'pe',weekly_exp,(strikePrice-50))
            logger.info(f'Repair order eid is: {eid2}')
            frsh=placeOrder(eid2,'sell',quantity,'RepairOnce')
            new_dictR.append(frsh)
            logger.info("----Stopping repeatedTimer------")
            rt1.stop()
            # runRepairActions('CE')
        else:
            logger.info('repair running...')
    except Exception:
        logger.exception('Repair Strategy Failed')
        logger.info("----Stopping repeatedTimer in Exception------")
        rt1.stop()

def runSqOffLogics():
    login()
    global pnl_dump
    logger.info('''\n Entering runSqOffLogics func,\n \t This logic runs till the end of the script and 
              checks SL/TARGET/TIMEings \n''')
    check=True
    while check:
        # #print("--- getting cur_PnL ---")
        cur_PnL = getPnL()
        if cur_PnL:
            if (cur_PnL < globalSL) or (cur_PnL >= globalTarget) or (datetime.now() >= datetime.strptime(cdate + " " + wrapTime, "%d-%m-%Y %H:%M:%S")):
                logger.info('SquareOff Logic met...')
                
                # closing all open positions   
                for i in range(len(mdf)):
                    eid=int(mdf['ss'].values[i])
                    symb=mdf['ordrtyp'].values[i]
                    qty=mdf['qq'].values[i]
                    squareOff(eid,symb,qty)
                # positionList = getPositionList()      
                # if positionList:
                #     pos_df = pd.DataFrame(positionList)
                    
                #     for i in range(len(pos_df)):
                #         if int(pos_df["Quantity"].values[i]) != 0:
                #             symb=pos_df['TradingSymbol'].values[i]
                #             eid = pos_df["ExchangeInstrumentId"].values[i]
                #             squareOff(eid,symb)
                #     # logger.info("Position Squareoff Completed ")
                # else:
                #     logger.info('Unable to get positionList to square-off. Try manually..')
                
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
                                #print("unable to delete order id : ",order)
                                attempt+=1
                else:
                    logger.info('Unable to get orderList to square-off. Try manually..')
        
                check=False # exit this long run main loop
            # elif not True in isSLHit():
            #     logger.info('both the order"s Sl hit - Hence winding up..')
            #     check=False
            else:
                pnl_dump.append([time.strftime("%d-%m-%Y %H:%M:%S"),cur_PnL])
                time.sleep(2)
    # return pnl_dump

#maybe main()
if __name__ == '__main__':
    # login()
    ticker='NIFTY'
    go = prepareVars(ticker)
    if go:
        logger.info('required variables set-- ready to trigger orders at desired time')
        nstart=True
        while nstart:
            if (datetime.now() >= datetime.strptime(cdate + " " + kickTime, "%d-%m-%Y %H:%M:%S")):
                runOrders()
                nstart = False
            else:
                time.sleep(0.5)
        if monitor:
            logger.info("starting multi funcs with threaded timer...")
            rt1 = RepeatedTimer(10, repairStrategy, ticker)
            try:
                logger.info("--- Entering SquareOffLogic Function after placing orders ---")
                runSqOffLogics()
                logger.info("--- Sq-off Func ended ---")
            except Exception:
                logger.exception("Something wrong with SquareoffLogic func..")
            finally:
                logger.info(f'Strategy2 Summary: \n {mdf}')
                logger.info('Dumping the PnL list to excel sheet..')
                if pnl_dump:
                    pnl_df= pd.DataFrame(pnl_dump,columns=['date','pl'])
                    pnl_df=pnl_df.set_index(['date'])
                    pnl_df.index=pd.to_datetime(pnl_df.index, format='%d-%m-%Y %H:%M:%S')
                    xdf=pnl_df['pl'].resample('1min').ohlc()
                    writer = pd.ExcelWriter(r'..\logs\Strategy2_PnL.xls')
                    xdf.to_excel(writer, sheet_name=(cdate+'_'+kickTime.replace(':','_')), index=True)
                    writer.save()
                else:
                    logger.info('Nothing to write in excel..')
                logger.info('in finally block.. Closing multi threaded func if running..')
                rt1.stop()
                logger.info('-- Script Ended --')
                logger.info('-- --------------------------------------------- --')
        else:
            logger.info("No Orders Placed")
            logger.info("Not started any multi funcs threaded timer")
    else:
        logger.info("Vars not set properly...")

