# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 02:05:10 2021
Re-writing Strategy-1 (INDEX OPTION WRITING)
@author: lmahendran
"""
############## imports ##############
from datetime import datetime,date
from dateutil.relativedelta import relativedelta, TH , WE
from XTConnect.Connect import XTSConnect
import XTConnect.Exception as ex
from pathlib import Path
import time
import json
import logging
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
# pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', -1)
import configparser
import timer
from threading import Thread
from openpyxl import load_workbook
from logging.handlers import TimedRotatingFileHandler
from sys import exit
import os

os.chdir(r'D:\Python\First_Choice_Git\xts\strategy\scripts')


############## logging configs ##############

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

filename='../logs/IndexOptionWriting_Live_log.txt'

#file_handler = logging.FileHandler(filename)
file_handler = TimedRotatingFileHandler(filename, when='d', interval=1, backupCount=3)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

############## XTS Initialisation ##############

cfg = configparser.ConfigParser()
cfg.read('../../XTConnect/config.ini')
source = cfg['user']['source']
appKey = cfg.get('user', 'interactive_appkey')
secretKey = cfg.get('user', 'interactive_secretkey')
xt = XTSConnect(appKey, secretKey, source)

global cdate
cdate = datetime.strftime(datetime.now(), "%d-%m-%Y")
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

############## Variable Declarations ##############

etr_inst = None
rpr_inst = None
ext_inst = None
tr_insts = None
ltp = {}
gl_pnl = None
pnl_dump = []
idxs = ['NIFTY','BANKNIFTY']
orders=[{'refId':10001, 'setno':1, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"NIFTY", 'otype': "ce", 'status': "Idle", 'expiry': 'week', 'lot': 1, 'straddle_points':50, 'stoplosstrig': 15.25, 'startTime':"09:59:00"},
		{'refId':10002, 'setno':2, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"NIFTY", 'otype': "pe", 'status': "Idle", 'expiry': 'week', 'lot': 1, 'straddle_points':50, 'stoplosstrig': 15.25, 'startTime':"09:59:00"},
        {'refId':10003, 'setno':3, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"BANKNIFTY", 'otype': "ce", 'status': "Idle", 'expiry': 'week', 'lot': 1, 'straddle_points':100, 'stoplosstrig': 60.25, 'startTime':"09:59:00"},
		{'refId':10004, 'setno':4, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"BANKNIFTY", 'otype': "pe", 'status': "Idle", 'expiry': 'week', 'lot': 1, 'straddle_points':100, 'stoplosstrig': 60.25, 'startTime':"09:59:00"}]
universal = {'exit_status': 'Idle', 'minPrice': -3000, 'maxPrice': 6900, 'exitTime':'15:05:00', 'ext_txn_type':'buy'}

############## Functions ##############

def get_expiry():
    global weekly_exp, monthly_exp
    now = datetime.today()
    cmon = now.month
    thu = (now + relativedelta(weekday=TH(1))).strftime('%d%b%Y')
    wed = (now + relativedelta(weekday=WE(1))).strftime('%d%b%Y')
    nxtmon = (now + relativedelta(weekday=TH(1))).month
    if (nxtmon != cmon):
        month_last_thu_expiry = now + relativedelta(weekday=TH(5))
        if (month_last_thu_expiry.month!= nxtmon):
            mon_thu = now + relativedelta(weekday=TH(4))
            mon_wed = now + relativedelta(weekday=WE(4))
    else:
        for i in range(1, 7):
            t = now + relativedelta(weekday=TH(i))
            if t.month != cmon:
                # since t is exceeded we need last one  which we can get by subtracting -2 since it is already a Thursday.
                mon_thu = (t + relativedelta(weekday=TH(-2))).strftime('%d%b%Y')
                mon_wed = (t + relativedelta(weekday=WE(-2))).strftime('%d%b%Y')
                break
    xpry_resp = xt.get_expiry_date(exchangeSegment=2, series='OPTIDX', symbol='NIFTY')
    if 'result' in xpry_resp:
        expiry_dates = xpry_resp['result']
    else:
        logger.error('Error getting Expiry dates..')
        raise ex.XTSDataException('Issue in getting expiry dates')
    if thu in expiry_dates:
        weekly_exp = thu
        logger.info(f'Thursday - {weekly_exp} is the week expiry')
    elif wed in expiry_dates:
        weekly_exp = wed
        logger.info(f'Wednesday - {weekly_exp} is the week expiry')
    if mon_thu in expiry_dates:
        monthly_exp = mon_thu
        logger.info(f'Thursday - {monthly_exp} is the month expiry')
    elif mon_wed in expiry_dates:
        monthly_exp = mon_wed
        logger.info(f'Wednesday - {monthly_exp} is the month expiry')
                    
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

def strikePrice(idx):
    if idx == idxs[0]:
        base = 50
        ids = 'NIFTY 50'
    elif idx == idxs[1]:
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

def instrumentLookup(instrument_df,symbol):
    """Looks up instrument token for a given script from instrument dump"""
    try:
        return instrument_df[instrument_df.Description==symbol].ExchangeInstrumentID.values[0]
    except:
        return -1

def getOrderList():
    aa = 0
    # logger.info('Checking OrderBook for order status..') 
    while aa < 5:
        try:
           oBook_resp = xt.get_order_book()
           if oBook_resp['type'] != "error":
               orderList =  oBook_resp['result']
               # logger.info('OrderBook result retreived success')
               return orderList
               break
           else:
               raise Exception("Unkonwn error in getOrderList func")           
        except Exception:
            logger.exception("Can't extract order data..retrying")
            # traceback.print_exc()
            time.sleep(2)
            aa+=1

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
                        tradedPrice = float(next((orderList['OrderAverageTradedPrice'] \
                                            for orderList in orderLists \
                                                if orderList['AppOrderID'] == orderID and\
                                                    orderList['OrderStatus'] == 'Filled'),None).replace(',', ''))
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
                            return None, None, None
                            break
                else:
                    logger.info('\n  Unable to get OrderList inside place order function..')
                    logger.info('..Hence traded price will retun as Zero \n ')
        elif order_resp['type'] == 'error':
            logger.info(f'Order not placed for - {symbol} ')
            logger.error(order_resp['description'])
            raise Exception('Order not placed - ')
    except Exception():
        raise ex.XTSOrderException('Unable to place order in placeOrder func...')
        logger.exception('Unable to place order in placeOrder func...')
        time.sleep(1)

def placeSLOrder(symbol, txn_type, qty, slTrigger):
    logger.info('Placing SL Order..')
    # Place an intraday stop loss order on NSE
    if txn_type == "buy":
        t_type=xt.TRANSACTION_TYPE_BUY
    elif txn_type == "sell":
        t_type=xt.TRANSACTION_TYPE_SELL
    try:
        sl_order_resp = xt.place_order(exchangeSegment=xt.EXCHANGE_NSEFO,
                             exchangeInstrumentID= symbol ,
                             productType=xt.PRODUCT_MIS, 
                             orderType="StopMarket",                   
                             orderSide=t_type,
                             timeInForce=xt.VALIDITY_DAY,
                             disclosedQuantity=0,
                             orderQuantity=qty,
                             limitPrice=0,
                             stopPrice=slTrigger,
                             orderUniqueIdentifier="FC_SLOrder"
                             )
        if sl_order_resp['type'] != 'error':
            orderID = sl_order_resp['result']['AppOrderID']            #extracting the order id from response
            logger.info(f'\n  StopLoss Order ID for {t_type}ing {symbol} is: {orderID} \n')
        else:
            logger.error(' \n Error in placing SL order \n')
        time.sleep(2)
        logger.info('Checking StopLoss status..')
        while universal['exit_status'] == 'Idle':
            time.sleep(5)
            orderLists = getOrderList()
            if orderLists:
                new_sl_orders = [ol for ol in orderLists if ol['AppOrderID'] == orderID and ol['OrderStatus'] != 'Filled']  
                if not new_sl_orders:
                    logger.info('Stop Loss Order Triggered inside repair block')
                    tradedPrice = float(next((orderList['OrderAverageTradedPrice'] \
                                        for orderList in orderLists\
                                             if orderList['AppOrderID'] == orderID and\
                                                 orderList['OrderStatus'] == 'Filled'),None).replace(',', ''))
                    LastUpdateDateTime=datetime.fromisoformat(next((orderList['LastUpdateDateTime'] for orderList in orderLists if orderList['AppOrderID'] == orderID and orderList['OrderStatus'] == 'Filled'))[0:19])
                    dateTime = LastUpdateDateTime.strftime("%Y-%m-%d %H:%M:%S")
                    logger.info(f"traded price is: {tradedPrice} and ordered  time is: {dateTime}")
                    return orderID, tradedPrice, dateTime
                    break
        if universal['exit_status'] == 'Exited':
            logger.info('Cancelling the SL order. Since the universal exit closes all open positiions')
            time.sleep(10)
            cancelOrder(orderID)
            return None,None,None
    except:
        raise ex.XTSOrderException('Unable to place stoploss order in placeSLOrder func...')

def execute(orders):
    global tr_insts
    tr_insts = []
    etr_inst = {}
    rpr_inst = {}
    startTime = datetime.strptime((cdate+" "+orders['startTime']),"%d-%m-%Y %H:%M:%S")
    weekday = datetime.today().weekday()
    while True:
        if orders['status'] == 'Idle':
            #Entry condition check
            if (datetime.now() >= startTime):
                logger.info(f'Placing orders for {orders["setno"]} at {orders["startTime"]}..')
                etr_inst['set']=orders['setno']
                etr_inst['txn_type'] = orders['ent_txn_type']
                sp = strikePrice(orders['idx'])
                
                if weekday != 3: #if not thursday, take straddle
                    etr_inst['strike'] = sp + orders['straddle_points'] if orders['otype'] == 'ce' else sp - orders['straddle_points']
                else:
                    etr_inst['strike'] = sp
                
                etr_inst['qty'] = 75*orders['lot'] if orders['idx'] == 'NIFTY' else 25*orders['lot']
                etr_inst['tr_qty'] = -etr_inst['qty'] if orders['ent_txn_type'] == 'sell' else etr_inst['qty']
                
                if orders['expiry'] == 'week':
                    etr_inst['expiry'] = weekly_exp
                etr_inst['optionType'] = orders['otype'].upper()
                
                if weekly_exp == monthly_exp:
                    inst_name = orders['idx']+(datetime.strftime(datetime.strptime(etr_inst['expiry'], '%d%b%Y'),'%y%b')).upper()+str(etr_inst['strike'])+etr_inst['optionType']
                else:
                    inst_name = orders['idx']+(datetime.strftime(datetime.strptime(etr_inst['expiry'], '%d%b%Y'),'%y%#m%d'))+str(etr_inst['strike'])+etr_inst['optionType']
                logger.info(f' Instrument Name is : {inst_name}')
                etr_inst['name'] = inst_name
                etr_inst['symbol'] = int(instrumentLookup(instrument_df,inst_name))
                if etr_inst['symbol'] == -1:
                    logger.info('Unable to get symbol from instrument Dump..exiting.')
                    exit()
                etr_inst['orderID'] = None
                etr_inst['tradedPrice'] = None
                # logger.info(f"orders before placing orders : {orders}")
                orderID, tradedPrice, dateTime = placeOrder(etr_inst['symbol'],etr_inst['txn_type'],etr_inst['qty'])
                etr_inst['orderID'] = orderID
                etr_inst['tradedPrice'] = tradedPrice
                etr_inst['dateTime'] = dateTime
                if orderID and tradedPrice:
                    etr_inst['set_type'] = 'Entry'
                    orders['status'] = 'Entered'
                logger.info(f'Entry order dtls: {etr_inst}')
                tr_insts.append(etr_inst)
                
        if universal['exit_status'] == 'Idle':  #Checking wheather universal exit triggered or not
            if orders['status'] == 'Entered':
                ename = next(i['name'] for i in tr_insts if i['set_type']=='Entry' and i['set']==orders['setno'])
                esymbol = next(i['symbol'] for i in tr_insts if i['set_type']=='Entry' and i['set']==orders['setno'])
                etp = next(i['tradedPrice'] for i in tr_insts if i['set_type']=='Entry' and i['set']==orders['setno'])
                slt = round((etp + orders['stoplosstrig']),2)
                eqty = next(i['qty'] for i in tr_insts if i['set_type']=='Entry' and i['set']==orders['setno'])
                rpr_inst['set_type'] = 'Repair'
                rpr_inst['set']=orders['setno']
                rpr_inst['txn_type'] = orders['rpr_txn_type']
                rpr_inst['strike'] = next(i['strike'] for i in tr_insts if i['set_type']=='Entry' and i['set']==orders['setno'])
                rpr_inst['qty']= eqty
                # rpr_inst['tr_qty'] = -rpr_inst['qty'] if orders['rpr_txn_type'] == 'sell' else rpr_inst['qty']
                if orders['expiry'] == 'week':
                    rpr_inst['expiry'] = weekly_exp
                rpr_inst['optionType'] = orders['otype'].upper()
                rpr_inst['name'] = ename
                rpr_inst['symbol'] = esymbol
                rpr_inst['orderID'] = None 
                rpr_inst['tradedPrice'] = None
                orderID, tradedPrice, dateTime = placeSLOrder(rpr_inst['symbol'], rpr_inst['txn_type'], rpr_inst['qty'], slt)
                rpr_inst['orderID'] = orderID
                rpr_inst['tradedPrice'] = tradedPrice
                rpr_inst['dateTime'] = dateTime
                if orderID and tradedPrice:
                    rpr_inst['tr_qty'] = -rpr_inst['qty'] if orders['rpr_txn_type'] == 'sell' else rpr_inst['qty']
                    orders['status'] = 'Repaired'
                logger.info(f'Repair order dtls: {rpr_inst}')
                tr_insts.append(rpr_inst)
                continue
        elif universal['exit_status'] == 'Exited':
           orders['status'] = 'Universal_Exit'
           logger.info('Orders must be square-off by Universal Exit Func')
           break
            
        if orders['status'] == 'Repaired':
            logger.info(f'Repaired the Entry Order set: {orders["setno"]}.Exiting the thread')
            break

def exitCheck(universal):
    global tr_insts , univ_exits
    # univ_exits = []
    # ext_inst = {}          
    exitTime = datetime.strptime((cdate+" "+universal['exitTime']),"%d-%m-%Y %H:%M:%S")
    while True:
        if universal['exit_status'] == 'Idle':
            #Exit condition check
            if (datetime.now() >= exitTime) or (gl_pnl <= universal['minPrice']) or (gl_pnl >= universal['maxPrice']):
                logger.info('Exit condition passed. Squaring off all open positions')
                # squaring off based on the gdf value
                ext_inst = {}
                for i in range(len(gdf)):
                    if gdf["tr_qty"].values[i] == 0:
                        continue
                    ext_inst['symbol'] = int(gdf['symbol'].values[i])                    
                    ext_inst['txn_type'] = universal['ext_txn_type'] 
                    ext_inst['tr_qty'] = -int(gdf['tr_qty'].values[i])
                    ext_inst['qty'] = abs(ext_inst['tr_qty'])
                    ext_inst['name'] = str(gdf['name'].values[i])
                    ext_inst['optionType'] = ext_inst['name'][-2:] 
                    ext_inst['strike'] = ext_inst['name'][-7:-2]
                    ext_inst['orderID'] = None
                    ext_inst['tradedPrice'] = None
                    orderID, tradedPrice, dateTime = placeOrder(ext_inst['symbol'], ext_inst['txn_type'], ext_inst['qty'])
                    ext_inst['orderID'] = orderID
                    ext_inst['tradedPrice'] = tradedPrice
                    ext_inst['dateTime'] = dateTime
                    if orderID and tradedPrice:
                        ext_inst['set_type']='Universal_Exit'
                    logger.info(f'Universal Exit order dtls: {ext_inst}')
                    tr_insts.append(ext_inst.copy())    
                logger.info('Breaking the main loop')
                universal['exit_status'] = 'Exited'
                break
        else:
            time.sleep(1)

def getLTP():
    global ltp
    # ltp={}
    if tr_insts:
        # logger.info('inside tr_insts cond - getLTP')
        symbols=[i['symbol'] for i in tr_insts if i['set_type'] == 'Entry']
        instruments=[]
        for symbol in symbols:
            instruments.append({'exchangeSegment': 2, 'exchangeInstrumentID': symbol})
        xt.send_unsubscription(Instruments=instruments,xtsMessageCode=1502)
        subs_resp=xt.send_subscription(Instruments=instruments,xtsMessageCode=1502)
        if subs_resp['type'] == 'success':
            for symbol,i in zip(symbols,range(len(symbols))):
                listQuotes = json.loads(subs_resp['result']['listQuotes'][i])
                price=listQuotes['Touchline']['LastTradedPrice']
                ltp[symbol]=price

def getGlobalPnL():
    global gl_pnl, df, gdf, pnl_dump
    # pnl_dump = []
    if tr_insts:
        # logger.info('inside tr_insts cond - getGlobalLTP')
        df = pd.DataFrame(tr_insts)
        df['tr_amount'] = df['tr_qty']*df['tradedPrice']
        df = df.fillna(0)
        df = df.astype(dtype={'set': int, 'txn_type': str, 'strike': int, 'qty': int, 'tr_qty': int, 'expiry': str, \
                                 'name': str, 'symbol': int, 'orderID': int, 'tradedPrice': float, 'dateTime': str, \
                                 'set_type': str, 'tr_amount': float, 'optionType': str})
        gdf = df.groupby(['name','symbol'],as_index=False).sum()[['symbol','name','tr_qty','tradedPrice','tr_amount']]
        gdf['ltp'] = gdf['symbol'].map(ltp)
        gdf['cur_amount'] = gdf['tr_qty']*gdf['ltp']
        gdf['pnl'] = gdf['cur_amount'] - gdf['tr_amount']
        logger.info(f'\n\nPositionList: \n {df}')
        logger.info(f'\n\nCombinedPositionsLists: \n {gdf}')
        gl_pnl = round(gdf['pnl'].sum(),2)
        logger.info(f'\n\nGlobal PnL : {gl_pnl} \n')
        pnl_dump.append([time.strftime("%d-%m-%Y %H:%M:%S"),gl_pnl])
    else:
        gl_pnl = 0

def dataToExcel(pnl_dump):
    pnl_df = pd.DataFrame(pnl_dump,columns=['date','pl'])
    pnl_df = pnl_df.set_index(['date'])
    pnl_df.index = pd.to_datetime(pnl_df.index, format='%d-%m-%Y %H:%M:%S')
    resampled_df = pnl_df['pl'].resample('1min').ohlc()
    #writing the output to excel sheet
    writer = pd.ExcelWriter('../pnl/Index_Option_Writing_PnL.xlsx',engine='openpyxl')
    writer.book = load_workbook('../pnl/Index_Option_Writing_PnL.xlsx')
    resampled_df.to_excel(writer, sheet_name=(cdate), index=True)
    df.to_excel(writer, sheet_name=(cdate),startrow=15, startcol=7, index=False)
    gdf.to_excel(writer, sheet_name=(cdate),startrow=4, startcol=7, index=False)
    writer.sheets=dict((ws.title, ws) for ws in writer.book.worksheets)
    worksheet = writer.sheets[cdate]
    worksheet['G1'] = "MaxPnL"
    worksheet["G2"] = "=MAX(E:E)"
    worksheet['H1'] = "MinPnL"
    worksheet["H2"] = "=MIN(E:E)"
    worksheet['I1'] = "FinalPnL"
    worksheet['I2'] = gl_pnl          
    writer.save()
    writer.close()

############## main ##############

if __name__ == '__main__':
    threads=[]
    # nextThu_and_lastThu_expiry_date()
    try:
        masterDump()
        get_expiry()
    except:
        logger.exception('Failed to get masterDump/ expiryDates. Exiting..')
        exit()
    # all the sets will execute in parallel with threads
    for i in range(len(orders)):
        t = Thread(target=execute,args=(orders[i],))
        t.start()
        threads.append(t)
    # below function runs in background
    logger.info('Starting a timer based thread to fetch LTP of traded instruments..')
    getGlobalPnL()
    fetchLtp = timer.RepeatedTimer(10, getLTP)
    fetchPnL = timer.RepeatedTimer(10, getGlobalPnL)
    try:
        exitCheck(universal)
        time.sleep(5)
    except KeyboardInterrupt:
        logger.error('\n\nKeyboard exception received. Exiting.')
        universal['exit_status'] = 'Exited' #todo write dead case here to stop the threads in case of exitcheck exception
        exit()
    except Exception:
        universal['exit_status'] = 'Exited'
        logger.exception('Error Occured..')
    finally:
        logger.info('Cleaning up..')
        fetchLtp.stop()
        fetchPnL.stop()
        _ = [t.join() for t in threads]
        time.sleep(5)
        #prints dump to excel
        getGlobalPnL()      #getting latest data
        dataToExcel(pnl_dump)
        # logging the orders and data to log file
        logger.info('--------------------------------------------')
        logger.info(f'Total Orders and its status: \n {tr_insts} \n')
        logger.info('Summary')
        logger.info(f'\n\n PositionList: \n {df}')
        logger.info(f'\n\n CombinedPositionsLists: \n {gdf}')
        logger.info(f'\n\n Global PnL : {gl_pnl} \n')
        logger.info('--------------------------------------------')
        
############## END ##############    