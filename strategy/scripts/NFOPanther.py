# -*- coding: utf-8 -*-
"""
Created on Thu Feb 01 2021 21:44:33 2021
NFO Panther Strategy 
@author: mling
"""

from datetime import datetime,date
from dateutil.relativedelta import relativedelta, TH
from XTConnect.Connect import XTSConnect
from pathlib import Path
import time
import json
import logging
import pandas as pd
import concurrent.futures
import configparser
# import timer
from threading import Timer
# from itertools import repeat
# import multiprocessing
# import schedule
from sys import exit
# import traceback

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

filename='../logs/NFOPanther_log_.txt'

file_handler = logging.FileHandler(filename)
# file_handler=logging.handlers.TimedRotatingFileHandler(filename, when='d', interval=1, backupCount=5)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

global multiplier
global cdate
# global orders


# idxs=['NIFTY 50','NIFTY BANK']
idxs=['NIFTY','BANKNIFTY']
multiplier=1

cdate = datetime.strftime(datetime.now(), "%d-%m-%Y")
startTime = "09:30:00"

cfg = configparser.ConfigParser()
cfg.read('../../XTConnect/config.ini')

source = cfg['user']['source']
appKey = cfg.get('user', 'interactive_appkey')
secretKey = cfg.get('user', 'interactive_secretkey')
xt = XTSConnect(appKey, secretKey, source)

token_file=f'access_token_{cdate}.txt'
file = Path(token_file)
try:
    if file.exists() and (date.today() == date.fromtimestamp(file.stat().st_mtime)):
        logger.info('Token file exists and created today')
        in_file = open(token_file,'r').read().split()
        access_token = in_file[0]
        userID=in_file[1]
        isInvestorClient=in_file[2]
        logger.info('Initializing session with token..')
        xt._set_common_variables(access_token, userID, isInvestorClient)
except:
    logger.exception('Wrong with token file. Generate separately.. Aborting script!..')
    exit()

# orders={'refId':10001,'set':1, \
#         'symbol': 0, 'inst_name':None, \
#         'txn_type': "sell", 'idx':"NIFTY", \
#         'strike':0, 'otype': "ce", \
#         'status': "idle",'expiry': weekly_exp, \
#         'lot': 2, 'startTime':"20:57:00"}
    
        
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

def strikePrice(idx):
    if idx in idxs[0]:
        base = 50
        ids = 'NIFTY 50'
    elif idx in idxs[1]:
        base = 100
        ids = 'NIFTY BANK'
    # if idx in idxs:
        # base,ids = [50,'Nifty 50'] if idx == 'NIFTY' else [100,'NIFTY BANK']
    else:
        logger.info(f'Invalid Index name {idx} - Valid names are {idxs}')
    try:
        idx_instruments = [{'exchangeSegment': 1, 'exchangeInstrumentID': ids}]
        spot_resp = xt.get_quote(
                    Instruments=idx_instruments,
                    xtsMessageCode=1504,
                    publishFormat='JSON')
        if spot_resp['type'] !='error':
            listQuotes = json.loads(spot_resp['result']['listQuotes'][0])
            spot=listQuotes['IndexValue']
        else:
            logger.error(spot_resp['description'])
            raise Exception()
    except Exception:
        logger.exception(f'Unable to getSpot from index {ids}')
        exit()
    else:
        strikePrice = base * round(spot/base)
        logger.info(f'StrikePrice computed as : {strikePrice}')
        return strikePrice   
        
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
           # if oBook_resp['type'] == "error":
           #     auth_issue_fix(oBook_resp)
           #     continue
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
           # elif pos_resp['type'] == "error":
           #     auth_issue_fix(pos_resp)
           #     continue
           else:
               raise Exception("Unkonwn error in getPositionoList func")
        except Exception:
            logger.exception("Can't extract position data...retrying")
            # traceback.print_exc()
            time.sleep(2)
            a+=1
                    
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
                
def masterDump():
    global instrument_df
    filename=f'../ohlc/NSE_Instruments_{cdate}.csv'
    file = Path(filename)
    if file.exists() and (date.today() == date.fromtimestamp(file.stat().st_mtime)):
        logger.info('MasterDump already exists.. reading directly')
        instrument_df=pd.read_csv(filename,header='infer')
    else:
        logger.info('Creating MasterDump..')
        exchangesegments = [xt.EXCHANGE_NSEFO]
        mastr_resp = xt.get_master(exchangeSegmentList=exchangesegments)
        # print("Master: " + str(mastr_resp))
        master=mastr_resp['result']
        spl=master.split('\n')
        mstr_df = pd.DataFrame([sub.split("|") for sub in spl],columns=(['ExchangeSegment','ExchangeInstrumentID','InstrumentType','Name','Description','Series','NameWithSeries','InstrumentID','PriceBand.High','PriceBand.Low','FreezeQty','TickSize',' LotSize','UnderlyingInstrumentId','UnderlyingIndexName','ContractExpiration','StrikePrice','OptionType']))
        instrument_df = mstr_df[mstr_df.Series == 'OPTIDX']
        instrument_df.to_csv(f"../ohlc/NSE_Instruments_{cdate}.csv",index=False)        
            
def instrumentLookup(instrument_df,symbol):
    """Looks up instrument token for a given script from instrument dump"""
    try:
        return instrument_df[instrument_df.Description==symbol].ExchangeInstrumentID.values[0]
    except:
        return -1            

def ltp(symbol):
    try:
        instruments={'exchangeSegment': 2, 'exchangeInstrumentID': symbol}
        xt.send_unsubscription(Instruments=instruments,xtsMessageCode=1502)
        subs_resp=xt.send_subscription(Instruments=instruments,xtsMessageCode=1502)
        if subs_resp['type'] == 'success':
            listQuotes = json.loads(subs_resp['result']['listQuotes'][i])
            return listQuotes['Touchline']['LastTradedPrice']
     except:
         return -1

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
            a=0
            while a<12:
                orderLists = getOrderList()
                if orderLists:
                    new_orders = [ol for ol in orderLists if ol['AppOrderID'] == orderID and ol['OrderStatus'] != 'Filled']  
                    if not new_orders:
                        tradedPrice = float(next((orderList['OrderAverageTradedPrice'] for orderList in orderLists if orderList['AppOrderID'] == orderID and orderList['OrderStatus'] == 'Filled'),None))
                        LastUpdateDateTime=datetime.fromisoformat(next((orderList['LastUpdateDateTime'] for orderList in orderLists if orderList['AppOrderID'] == orderID and orderList['OrderStatus'] == 'Filled'))[:-1])
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
                            break
                else:
                    logger.info('\n  Unable to get OrderList inside place order function..')
                    logger.info('..Hence traded price will retun as Zero \n ')
        elif order_resp['type'] == 'error':
            logger.error(order_resp['description'])
            logger.info(f'Order not placed for - {symbol} ')
            raise Exception('Order not placed - ')
    except Exception():
        logger.exception('Unable to place order in placeOrder func...')
        time.sleep(1)
    # else:
    #     return orderID, tradedPrice, dateTime

def execute(orders):
    global tr_insts
    # global orders
    a=0
    while True:
        if orders['status'] == 'idle':
            if (datetime.now() >= datetime.strptime((cdate+" "+orders['startTime']),"%d-%m-%Y %H:%M:%S")):
                logger.info(f'Placing orders as status is idle and timing {orders["startTime"]} cond met ..')
                tr_inst['set']=orders['setno']
                tr_inst['txn_type'] = orders['txn_type']
                tr_inst['strike'] = strikePrice(orders['idx'])
                qty = 75*orders['lot'] if orders['idx'] == 'NIFTY' else 25*orders['lot']
                tr_inst['qty'] = qty
                if orders['expiry'] == 'week':
                    tr_inst['expiry']=weekly_exp
                if weekly_exp == monthly_exp:
                    inst_name = orders['idx']+(datetime.strftime(datetime.strptime(tr_inst['expiry'], '%d%b%Y'),'%y%b')).upper()+str(tr_inst['strike'])+orders['otype'].upper()
                else:
                    inst_name = orders['idx']+(datetime.strftime(datetime.strptime(tr_inst['expiry'], '%d%b%Y'),'%y%#m%d'))+str(orders['strike'])+orders['otype'].upper()
                tr_inst['name'] = inst_name
                tr_inst['symbol'] = int(instrumentLookup(instrument_df,inst_name))
                tr_inst['orderID']=None
                tr_inst['tradedPrice']=None
                logger.info(f"orders before placing orders : {orders}")
                orderID, tradedPrice, dateTime=placeOrder(tr_inst['symbol'],tr_inst['txn_type'],tr_inst['qty'])
                tr_inst['orderID']=orderID
                tr_inst['tradedPrice']=tradedPrice
                tr_inst['dateTime']=dateTime
                if orderID and tradedPrice:
                    orders['status']='Active'
                    tr_inst['set_type']='Entry'
                logger.info(f'{tr_inst}')
                tr_insts.append(tr_inst)
        if orders['status'] == 'Active':
            if (ltp(next(i['symbol'] for i in tr_insts if i['set_type']=='Entry' and i['set']==1 )) > \
                   next(i['tradedPrice'] for i in tr_insts if i['set_type']=='Entry' and i['set']==1) + 15) or \
                
            logger.info('running orders as status is Active..')
            logger.info('in Active loop')
            orders['status']='exit'
        if orders['status'] == 'exit' and a==10:
            logger.info('running orders as status is exit..')
            logger.info('temrinating the loop..')
            break
        a+=1
        logger.info(a)
        time.sleep(1)
    return tr_insts


if __name__ == '__main__':

    # orders={'refId':10001,          \
    #         'setno':1,              \ 
    #         'symbol': 0,            \
    #         'inst_name':None,       \
    #         'txn_type': "sell",     \
    #         'idx':"NIFTY",          \
    #         'strike':0,             \
    #         'otype': "ce",          \
    #         'status': "idle",       \
    #         'expiry': weekly_exp,   \
    #         'lot': 2,               \
    #         'startTime':"11:50:00"}
    orders={'refId':10001,          \
            'setno':1,              \
            'txn_type': "sell",     \
            'idx':"NIFTY",          \
            'otype': "ce",          \
            'status': "idle",       \
            'expiry': 'week',   \
            'lot': 2,               \
            'startTime':"11:50:00"}
        
    tr_inst= {}
    tr_insts=[]
    nextThu_and_lastThu_expiry_date()
    masterDump()
    try:
        logger.info("orders before : ",orders)
        logger.info(f"{tr_insts}")
        logger.info(f"{tr_inst}")
        result=execute(orders)
        print(result)
    except Exception:
        logger.exception('Error Occured..')
    finally:
        logger.info('--------------------------------------------')
    
    # print("orders after execute function : ",orders)
    
    # id = [x['id'] for x in results if x['name'] == "virtual-machine-1"]

    # strikePrice(orders['idx'])
       
tr_insts=[{'set': 1, 'txn_type': 'sell', 'strike': 15100, 'qty': 150, 'expiry': '25Feb2021', 'name': 'NIFTY21FEB15100CE', 'symbol': 46357, 'orderID': 10027094, 'tradedPrice': 130.25, 'dateTime': '2021-02-19 18:33:01', 'set_type': 'Entry'},
          {'set': 1, 'txn_type': 'buy', 'strike': 15100, 'qty': 150, 'expiry': '25Feb2021', 'name': 'NIFTY21FEB15150CE', 'symbol': 46357, 'orderID': 10027095, 'tradedPrice': 1.25, 'dateTime': '2021-02-19 18:33:01', 'set_type': 'Repair'}]
for i in tr_insts:
    a = next(i['tradedPrice'] for i in tr_insts if i['set_type']=='Entry' and i['set']==1)
        


        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        