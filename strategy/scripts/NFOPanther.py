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
# startTime = "09:30:00"

cfg = configparser.ConfigParser()
cfg.read('../../XTConnect/config.ini')

source = cfg['user']['source']
appKey = cfg.get('user', 'interactive_appkey')
secretKey = cfg.get('user', 'interactive_secretkey')
xt = XTSConnect(appKey, secretKey, source)

# response=xt.interactive_login()
# print(response)

token_file=f'access_token_{cdate}.txt'
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

orders={'refId':10001,          \
        'setno':1,              \
        'ent_txn_type': "sell", \
        'rpr_txn_type': "buy",  \
        'ext_txn_type': "buy",  \
        'idx':"NIFTY",          \
        'otype': "ce",          \
        'status': "Idle",       \
        'expiry': 'week',       \
        'lot': 2,               \
        'startTime':"14:25:00", \
        'endTime':"14:45:00",   \
        'repairedAlready':False}
        
etr_inst= {}
rpr_inst= {}
ext_inst= {}
tr_insts=[]
       
def nextThu_and_lastThu_expiry_date():
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
    
# def ltp(symbol):
#     try:
#         instruments=[{'exchangeSegment': 2, 'exchangeInstrumentID': symbol}]
#         xt.send_unsubscription(Instruments=instruments,xtsMessageCode=1502)
#         subs_resp=xt.send_subscription(Instruments=instruments,xtsMessageCode=1502)
#         if subs_resp['type'] == 'success':
#             listQuotes = json.loads(subs_resp['result']['listQuotes'][0])
#             return listQuotes['Touchline']['LastTradedPrice']
#     except:
#         logger.exception('Unable to get LTP')
#         return None

def ltp(tr_insts):
    global ltp
    symbols=[i['symbol'] for i in tr_insts if i['set_type'] == 'Entry']
    instruments=[]
    for symbol in symbols:
        instruments.append({'exchangeSegment': 2, 'exchangeInstrumentID': symbol})
    xt.send_unsubscription(Instruments=instruments,xtsMessageCode=1502)
    subs_resp=xt.send_subscription(Instruments=instruments,xtsMessageCode=1502)
    if subs_resp['type'] == 'success':
        ltp={}
        for symbol,i in zip(symbols,range(len(symbols))):
            listQuotes = json.loads(subs_resp['result']['listQuotes'][i])
            price=listQuotes['Touchline']['LastTradedPrice']
            ltp[symbol]=price

def get_global_ltp():
    df = pd.DataFrame(tr_insts)
    df['amount'] = df['tr_qty']*df['tradedPrice']
    df = df.astype(dtype={'set': int,
                             'txn_type': str,
                             'strike': int,
                             'qty': int,
                             'tr_qty': int,
                             'expiry': str,
                             'name': str,
                             'symbol': int,
                             'orderID': int,
                             'tradedPrice': float,
                             'dateTime': str,
                             'set_type': str,
                             'amount': float})
    gdf = df.groupby(['name','symbol'],as_index=False).sum()[['symbol','name','tr_qty','tradedPrice','amount']]
    gdf['ltp'] = gdf['symbol'].map(ltp)
    gdf['cur_amt'] = gdf['tr_qty']*gdf['ltp']
    gdf['pnl'] = gdf['cur_amt'] - gdf['amount']

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
                        tradedPrice = float(next((orderList['OrderAverageTradedPrice'] for orderList in orderLists if orderList['AppOrderID'] == orderID and orderList['OrderStatus'] == 'Filled'),None))
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

def execute(orders):
    global tr_insts
    # global orders
    while True:
        if orders['status'] == 'Idle':
            #Entry condition check
            if (datetime.now() >= datetime.strptime((cdate+" "+orders['startTime']),"%d-%m-%Y %H:%M:%S")):
                logger.info(f'Placing orders as status is idle and timing {orders["startTime"]} cond met ..')
                etr_inst['set']=orders['setno']
                etr_inst['txn_type'] = orders['ent_txn_type']
                etr_inst['strike'] = strikePrice(orders['idx'])
                etr_inst['qty'] = 75*orders['lot'] if orders['idx'] == 'NIFTY' else 25*orders['lot']
                etr_inst['tr_qty'] = -etr_inst['qty'] if orders['ent_txn_type'] == 'sell' else etr_inst['qty']
                if orders['expiry'] == 'week':
                    etr_inst['expiry'] = weekly_exp
                if weekly_exp == monthly_exp:
                    inst_name = orders['idx']+(datetime.strftime(datetime.strptime(etr_inst['expiry'], '%d%b%Y'),'%y%b')).upper()+str(etr_inst['strike'])+orders['otype'].upper()
                else:
                    inst_name = orders['idx']+(datetime.strftime(datetime.strptime(etr_inst['expiry'], '%d%b%Y'),'%y%#m%d'))+str(orders['strike'])+orders['otype'].upper()
                etr_inst['name'] = inst_name
                etr_inst['symbol'] = int(instrumentLookup(instrument_df,inst_name))
                etr_inst['orderID'] = None
                etr_inst['tradedPrice'] = None
                logger.info(f"orders before placing orders : {orders}")
                orderID, tradedPrice, dateTime = placeOrder(etr_inst['symbol'],etr_inst['txn_type'],etr_inst['qty'])
                etr_inst['orderID'] = orderID
                etr_inst['tradedPrice'] = tradedPrice
                etr_inst['dateTime'] = dateTime
                if orderID and tradedPrice:
                    etr_inst['set_type'] = 'Entry'
                    orders['status'] = 'Active'
                logger.info(f'Entry order dtls: {etr_inst}')
                tr_insts.append(etr_inst)
                
        if orders['status'] == 'Active':
            ename = next(i['name'] for i in tr_insts if i['set_type']=='Entry' and i['set']==orders['setno'])
            esymbol = next(i['symbol'] for i in tr_insts if i['set_type']=='Entry' and i['set']==orders['setno'])
            etp = next(i['tradedPrice'] for i in tr_insts if i['set_type']=='Entry' and i['set']==orders['setno'])
            eqty = next(i['qty'] for i in tr_insts if i['set_type']=='Entry' and i['set']==orders['setno'])
            # logger.info(f'Extracted from Entry Order:{ename}, {esymbol}, {etp}, {eqty}')
            #Exit condition check
            if (datetime.now() >= datetime.strptime((cdate+" "+orders['endTime']),"%d-%m-%Y %H:%M:%S")):
                logger.info('Exit time condition passed. Squaring off open positions in this set')
                ext_inst['set'] = orders['setno']
                ext_inst['txn_type'] = orders['ext_txn_type']
                # ext_inst['strike'] = strikePrice(orders['idx'])
                ext_inst['strike'] = next(i['strike'] for i in tr_insts if i['set_type']=='Entry' and i['set']==orders['setno'])
                if orders['repairedAlready']:
                    ext_inst['qty'] = (next(i['qty'] for i in tr_insts if i['set_type']=='Entry' and i['set']==orders['setno']))*0.5
                elif not orders['repairedAlready']:
                    ext_inst['qty'] = next(i['qty'] for i in tr_insts if i['set_type']=='Entry' and i['set']==orders['setno'])
                ext_inst['tr_qty'] = -ext_inst['qty'] if orders['ext_txn_type'] == 'sell' else ext_inst['qty']
                if orders['expiry'] == 'week':
                    ext_inst['expiry']=weekly_exp
                ext_inst['name'] = ename
                ext_inst['symbol'] = esymbol
                ext_inst['orderID'] = None
                ext_inst['tradedPrice'] = None
                # logger.info(f"orders before placing orders : {orders}")
                orderID, tradedPrice, dateTime = placeOrder(ext_inst['symbol'],ext_inst['txn_type'],ext_inst['qty'])
                ext_inst['orderID']=orderID
                ext_inst['tradedPrice']=tradedPrice
                ext_inst['dateTime']=dateTime
                if orderID and tradedPrice:
                    ext_inst['set_type']='Exit'
                    orders['status']='Exit'
                logger.info(f'Exit order dtls: {ext_inst}')
                tr_insts.append(ext_inst)
                # orders['status'] = 'Exit'
                continue

            ltpsymbol = ltp['esymbol']
            # logger.info(f'LTP of Entry instrument : {ltpsymbol}')
            
            # Repair condition check
            if ((ltpsymbol > etp + 15) or (ltpsymbol < etp -45)) and not orders['repairedAlready']:
                logger.info('Reparing order as status is active and +15/-45 cond met..')
                rpr_inst['set']=orders['setno']
                rpr_inst['txn_type'] = orders['rpr_txn_type']
                # rpr_inst['strike'] = strikePrice(orders['idx'])
                rpr_inst['strike'] = next(i['strike'] for i in tr_insts if i['set_type']=='Entry' and i['set']==orders['setno'])
                rpr_inst['qty']= int(eqty/2)
                rpr_inst['tr_qty'] = -rpr_inst['qty'] if orders['rpr_txn_type'] == 'sell' else rpr_inst['qty']
                if orders['expiry'] == 'week':
                    rpr_inst['expiry']=weekly_exp
                rpr_inst['name'] = ename
                rpr_inst['symbol'] = esymbol
                rpr_inst['orderID'] = None
                rpr_inst['tradedPrice'] = None
                orderID, tradedPrice, dateTime = placeOrder(rpr_inst['symbol'],rpr_inst['txn_type'],rpr_inst['qty'])
                rpr_inst['orderID'] = orderID
                rpr_inst['tradedPrice'] = tradedPrice
                rpr_inst['dateTime'] = dateTime
                if orderID and tradedPrice:
                    # orders['status'] = 'Repair_Done'
                    orders['repairedAlready'] = True
                    rpr_inst['set_type'] = 'Repair'
                logger.info(f'Repair order dtls: {rpr_inst}')
                tr_insts.append(rpr_inst)
        #if status turns exit
        if orders['status'] == 'Exit':
            logger.info('End Time Reached. Winding up..')
            return "Completed.."
            break
                
if __name__ == '__main__':
    nextThu_and_lastThu_expiry_date()
    masterDump()
    try:
        # logger.info(f"orders before : {orders}")
        # logger.info(f" traded inst list - {tr_insts}")
        result=execute(orders)
        logger.info(result)
    except Exception:
        logger.exception('Error Occured..')
    finally:
        logger.info('--------------------------------------------')
    

       
# tr_insts=[{'set': 1, 'txn_type': 'sell', 'strike': 15100, 'qty': 150, 'expiry': '25Feb2021', 'name': 'NIFTY21FEB15100CE', 'symbol': 46357, 'orderID': 10027094, 'tradedPrice': 130.25, 'dateTime': '2021-02-19 18:33:01', 'set_type': 'Entry'},
#           {'set': 1, 'txn_type': 'buy', 'strike': 15100, 'qty': 75, 'expiry': '25Feb2021', 'name': 'NIFTY21FEB15150CE', 'symbol': 46357, 'orderID': 10027095, 'tradedPrice': 1.25, 'dateTime': '2021-02-19 19:33:01', 'set_type': 'Repair'},
#           {'set': 1, 'txn_type': 'buy', 'strike': 15100, 'qty': 75, 'expiry': '25Feb2021', 'name': 'NIFTY21FEB15150CE', 'symbol': 46357, 'orderID': 10027096, 'tradedPrice': 11.25, 'dateTime': '2021-02-19 19:37:01', 'set_type': 'Exit'},
#           {'set': 2, 'txn_type': 'sell', 'strike': 15100, 'qty': 150, 'expiry': '25Feb2021', 'name': 'NIFTY21FEB15100CE', 'symbol': 46357, 'orderID': 10027097, 'tradedPrice': 9.25, 'dateTime': '2021-02-19 20:33:01', 'set_type': 'Entry'},
#           {'set': 2, 'txn_type': 'buy', 'strike': 15100, 'qty': 75, 'expiry': '25Feb2021', 'name': 'NIFTY21FEB15150CE', 'symbol': 46357, 'orderID': 10027098, 'tradedPrice': 76.25, 'dateTime': '2021-02-19 21:33:01', 'set_type': 'Repair'},
#           {'set': 2, 'txn_type': 'buy', 'strike': 15100, 'qty': 75, 'expiry': '25Feb2021', 'name': 'NIFTY21FEB15150CE', 'symbol': 46357, 'orderID': 10027099, 'tradedPrice': 987.25, 'dateTime': '2021-02-19 21:37:01', 'set_type': 'Exit'}]
# # a = next(i['tradedPrice'] for i in tr_insts if i['set_type']=='Exit' and i['set']==2)


# tr_insts= [{'set': 1, 'txn_type': 'sell', 'strike': 14700, 'qty': 150, 'tr_qty': -150, 'expiry': '25Feb2021', 'name': 'NIFTY21FEB14700CE', 'symbol': 39607, 'orderID': 10026944, 'tradedPrice': 115.2, 'dateTime': '2021-02-22 14:25:05', 'set_type': 'Entry'}, {'set': 1, 'txn_type': 'sell', 'strike': 14700, 'qty': 150, 'tr_qty': -150, 'expiry': '25Feb2021', 'name': 'NIFTY21FEB14700CE', 'symbol': 39607, 'orderID': 10026944, 'tradedPrice': 115.2, 'dateTime': '2021-02-22 14:25:05', 'set_type': 'Entry'}, {'set': 1, 'txn_type': 'buy', 'strike': 14700, 'qty': 75.0, 'tr_qty': 75.0, 'name': 'NIFTY21FEB14700CE', 'symbol': 39607, 'orderID': 10026962, 'tradedPrice': 138.0, 'dateTime': '2021-02-22 14:45:04', 'set_type': 'Exit'},
#            {'set': 2, 'txn_type': 'sell', 'strike': 14701, 'qty': 150, 'tr_qty': -150, 'expiry': '25Feb2021', 'name': 'NIFTY21FEB14800CE', 'symbol': 39608, 'orderID': 10026956, 'tradedPrice': 115.2, 'dateTime': '2021-02-22 14:25:05', 'set_type': 'Entry'}, {'set': 2, 'txn_type': 'sell', 'strike': 14800, 'qty': 150, 'tr_qty': -150, 'expiry': '25Feb2021', 'name': 'NIFTY21FEB14700CE', 'symbol': 39653, 'orderID': 10026944, 'tradedPrice': 115.2, 'dateTime': '2021-02-22 14:25:05', 'set_type': 'Entry'}, {'set': 2, 'txn_type': 'buy', 'strike': 14700, 'qty': 75.0, 'tr_qty': 75.0, 'name': 'NIFTY21FEB14800CE', 'symbol': 39656, 'orderID': 10026962, 'tradedPrice': 138.0, 'dateTime': '2021-02-22 14:45:04', 'set_type': 'Exit'}]

# tr_insts=[{'set': 1, 'txn_type': 'sell', 'strike': 14700, 'qty': 150, 'tr_qty': 75, 'expiry': '25Feb2021', 'name': 'NIFTY21FEB14700CE', 'symbol': 39607, 'orderID': 10026944, 'tradedPrice': 138.7, 'dateTime': '2021-02-22 14:25:05', 'set_type': 'RepairOnce'},
#           {'set': 1, 'txn_type': 'buy', 'strike': 14700, 'qty': 75, 'tr_qty': -150, 'expiry': '25Feb2021', 'name': 'NIFTY21FEB14700CE', 'symbol': 39607, 'orderID': 10026945, 'tradedPrice': 122.2, 'dateTime': '2021-02-22 14:25:05', 'set_type': 'Entry'}]
# tr_insts1=[{'set': 1, 'txn_type': 'buy', 'strike': 14700, 'qty': 75, 'tr_qty': -150, 'expiry': '25Feb2021', 'name': 'NIFTY21FEB14700CE', 'symbol': 39607, 'orderID': 10026945, 'tradedPrice': 122.2, 'dateTime': '2021-02-22 14:25:05', 'set_type': 'Entry'}]


    

# ltp={39607:234,39613:123}    
 
