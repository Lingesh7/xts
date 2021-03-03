# -*- coding: utf-8 -*-
"""
Created on Thu Feb 01 2021 21:44:33 2021
NFO Panther Strategy  - With Universal Exit - Array of Orders
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
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
# pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', -1)
import configparser
import timer
from threading import Thread
from openpyxl import load_workbook
from sys import exit

############## logging configs ##############
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

filename='../logs/NFOPanther_log.txt'

file_handler = logging.FileHandler(filename)
# file_handler=logging.handlers.TimedRotatingFileHandler(filename, when='d', interval=1, backupCount=5)
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
multiplier=1
etr_inst = None
rpr_inst = None
ext_inst = None
tr_insts = None
ltp = {}
gl_pnl = None
idxs = ['NIFTY','BANKNIFTY']
orders=[{'refId':10001, 'setno':1, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"NIFTY", 'otype': "ce", 'status': "Idle", 'expiry': 'week', 'lot': 2, 'startTime':"22:45:00"},
		{'refId':10002, 'setno':2, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"NIFTY", 'otype': "pe", 'status': "Idle", 'expiry': 'week', 'lot': 2, 'startTime':"22:45:00"},
		{'refId':10003, 'setno':3, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"NIFTY", 'otype': "ce", 'status': "Idle", 'expiry': 'week', 'lot': 2, 'startTime':"22:47:00"},
		{'refId':10004, 'setno':4, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"NIFTY", 'otype': "pe", 'status': "Idle", 'expiry': 'week', 'lot': 2, 'startTime':"22:47:00"},
		{'refId':10005, 'setno':5, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"NIFTY", 'otype': "ce", 'status': "Idle", 'expiry': 'week', 'lot': 2, 'startTime':"22:49:00"},
		{'refId':10006, 'setno':6, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"NIFTY", 'otype': "pe", 'status': "Idle", 'expiry': 'week', 'lot': 2, 'startTime':"22:49:00"}]
universal = {'exit_status': 'Idle', 'minPrice': -12000, 'maxPrice': 24000, 'exitTime':'22:48:00', 'ext_txn_type':'buy'}
# exitTime = datetime.strptime((cdate+" "+universal['exitTime']),"%d-%m-%Y %H:%M:%S")

############## Functions ##############
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
    logger.info('Checking OrderBook for order status..') 
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
    pnl_dump = []
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
        logger.info(f'PositionList: \n {df}')
        logger.info(f'CombinedPositionsLists: \n {gdf}')
        gl_pnl = round(gdf['pnl'].sum(),2)
        logger.info(f'Global PnL : {gl_pnl}')
        pnl_dump.append([time.strftime("%d-%m-%Y %H:%M:%S"),gl_pnl])
    else:
        gl_pnl = 0
 
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
                            return None, None, None
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
    tr_insts = []
    etr_inst = {}
    rpr_inst = {}
    startTime = datetime.strptime((cdate+" "+orders['startTime']),"%d-%m-%Y %H:%M:%S")
    while True:
        if orders['status'] == 'Idle':
            #Entry condition check
            if (datetime.now() >= startTime):
                logger.info(f'Placing orders for {orders["setno"]} at {orders["startTime"]}..')
                etr_inst['set']=orders['setno']
                etr_inst['txn_type'] = orders['ent_txn_type']
                etr_inst['strike'] = strikePrice(orders['idx'])
                etr_inst['qty'] = 75*orders['lot'] if orders['idx'] == 'NIFTY' else 25*orders['lot']
                etr_inst['tr_qty'] = -etr_inst['qty'] if orders['ent_txn_type'] == 'sell' else etr_inst['qty']
                if orders['expiry'] == 'week':
                    etr_inst['expiry'] = weekly_exp
                etr_inst['optionType'] = orders['otype'].upper()
                if weekly_exp == monthly_exp:
                    inst_name = orders['idx']+(datetime.strftime(datetime.strptime(etr_inst['expiry'], '%d%b%Y'),'%y%b')).upper()+str(etr_inst['strike'])+etr_inst['optionType']
                else:
                    inst_name = orders['idx']+(datetime.strftime(datetime.strptime(etr_inst['expiry'], '%d%b%Y'),'%y%#m%d'))+str(etr_inst['strike'])+etr_inst['optionType']
                etr_inst['name'] = inst_name
                etr_inst['symbol'] = int(instrumentLookup(instrument_df,inst_name))
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
                eqty = next(i['qty'] for i in tr_insts if i['set_type']=='Entry' and i['set']==orders['setno'])
                # logger.info(f'Extracted from Entry Order:{ename}, {esymbol}, {etp}, {eqty}')
                if esymbol in ltp.keys():
                    ltpsymbol = ltp[esymbol]
                    # logger.info(f'LTP of Entry instrument : {ltpsymbol}')
                    # Repair condition check
                    if ((ltpsymbol > etp + 15) or (ltpsymbol < etp - 45)):
                        logger.info(f'Reparing order as +15/-45 cond met in set: {orders["setno"]}..')
                        rpr_inst['set']=orders['setno']
                        rpr_inst['txn_type'] = orders['rpr_txn_type']
                        # rpr_inst['strike'] = strikePrice(orders['idx'])
                        rpr_inst['strike'] = next(i['strike'] for i in tr_insts if i['set_type']=='Entry' and i['set']==orders['setno'])
                        rpr_inst['qty']= int(eqty/2)
                        rpr_inst['tr_qty'] = -rpr_inst['qty'] if orders['rpr_txn_type'] == 'sell' else rpr_inst['qty']
                        if orders['expiry'] == 'week':
                            rpr_inst['expiry']=weekly_exp
                        rpr_inst['optionType'] = orders['otype']
                        rpr_inst['name'] = ename
                        rpr_inst['symbol'] = esymbol
                        rpr_inst['orderID'] = None
                        rpr_inst['tradedPrice'] = None
                        orderID, tradedPrice, dateTime = placeOrder(rpr_inst['symbol'],rpr_inst['txn_type'],rpr_inst['qty'])
                        rpr_inst['orderID'] = orderID
                        rpr_inst['tradedPrice'] = tradedPrice
                        rpr_inst['dateTime'] = dateTime
                        if orderID and tradedPrice:
                            orders['status'] = 'Repaired'
                            # orders['repairedAlready'] = True
                            rpr_inst['set_type'] = 'Repair'
                        logger.info(f'Repair order dtls: {rpr_inst}')
                        tr_insts.append(rpr_inst)
                        continue
        elif universal['exit_status'] == 'Exited':
           orders['status'] = 'Universal_Exit'
           logger.info('Orders must be square-off by Universal Exit Func')
           break
        #breaking set loop if status repaired
        if orders['status'] == 'Repaired':
            logger.info(f'Repaired the Entry Order set: {orders["setno"]}. Exit will taken care by universally.')
            break
          
def exitCheck(universal):
    global tr_insts #todo add gl_pnl to global if the conditions didnt work
    # pnl_dump=[] 
    ext_inst = {}          
    exitTime = datetime.strptime((cdate+" "+universal['exitTime']),"%d-%m-%Y %H:%M:%S")
    # print('exitTime:', exitTime)
    while True:
        if universal['exit_status'] == 'Idle':
            #Exit condition check
            # logger.info(f'exitcheck - {gl_pnl}') #todo comment this line after execution
            if (datetime.now() >= exitTime) or (gl_pnl <= universal['minPrice']) or (gl_pnl >= universal['maxPrice']):
                logger.info('Exit time condition passed. Squaring off all open positions')
                for i in range(len(gdf)):
                    logger.info(f'gdf is : {gdf}')
                    ext_inst['symbol'] = int(gdf['symbol'].values[i])
                    ext_inst['tr_qty'] = int(gdf['tr_qty'].values[i])
                    ext_inst['qty'] = abs(ext_inst['tr_qty'])
                    ext_inst['txn_type'] = universal['ext_txn_type'] 
                    ext_inst['name'] = str(gdf['name'].values[i])
                    ext_inst['orderID'] = None
                    ext_inst['tradedPrice'] = None
                    orderID, tradedPrice, dateTime = placeOrder(ext_inst['symbol'], ext_inst['txn_type'], ext_inst['qty'])
                    ext_inst['orderID'] = orderID
                    ext_inst['tradedPrice'] = tradedPrice
                    ext_inst['dateTime'] = dateTime
                    if orderID and tradedPrice:
                        ext_inst['set_type']='Universal_Exit'
                        universal['exit_status'] = 'Exited'
                    logger.info(f'Universal Exit order dtls: {ext_inst}')
                    tr_insts.append(ext_inst)
                break

def dataToExcel(pnl_dump):
    pnl_df = pd.DataFrame(pnl_dump,columns=['date','pl'])
    pnl_df = pnl_df.set_index(['date'])
    pnl_df.index = pd.to_datetime(pnl_df.index, format='%d-%m-%Y %H:%M:%S')
    resampled_df = pnl_df['pl'].resample('1min').ohlc()
    #writing the output to excel sheet
    writer = pd.ExcelWriter('../pnl/NFOPanther_PnL.xlsx',engine='openpyxl')
    writer.book = load_workbook('../pnl/NFOPanther_PnL.xlsx')
    resampled_df.to_excel(writer, sheet_name=(cdate), index=True)
    df.to_excel(writer, sheet_name=(cdate),startrow=25, startcol=7, index=False)
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

def main():
    threads=[]
    nextThu_and_lastThu_expiry_date()
    masterDump()
    getGlobalPnL()
    logger.info('Starting a timer based thread to fetch LTP of traded instruments..')
    fetchLtp = timer.RepeatedTimer(10, getLTP)
    fetchPnL = timer.RepeatedTimer(10, getGlobalPnL)
    logger.info('starting thread based execution of orders parallely..')
    for i in range(len(orders)):
        t = Thread(target=execute,args=(orders[i],))
        t.start()
        threads.append(t)
    try:
        exitCheck(universal)
        time.sleep(5)
        # if result:
        #     logger.info('Writing pnl dump to excel..')
        #     dataToExcel(result)
        # time.sleep(5)
    except Exception:
        logger.exception('Error Occured..')
    finally:
        fetchLtp.stop()
        fetchPnL.stop()
        # _ = [t.join() for t in threads] #anohter way to join threads
        for thread in threads:
            logger.info(thread.is_alive())
            thread.join()
        # if result:
        dataToExcel(pnl_dump)
        logger.info('--------------------------------------------')
        logger.info(f'Total Orders and its status: \n {tr_insts} \n')
        logger.info('Summary')
        logger.info(f'\n\n PositionList: \n {df}')
        logger.info(f'\n\n CombinedPositionsLists: \n {gdf}')
        logger.info(f'\n\n Global PnL : {gl_pnl} \n')
        logger.info('--------------------------------------------')
        
############## main ##############        
if __name__ == '__main__':
    main()
    starttime=time.time()
    timeout = time.time() + 60*60*6 #runs for 6 hours
    while time.time() <= timeout:
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            print('\n\nKeyboard exception received. Exiting.')
            exit() 
############# END ##############

# tr_insts = [{'set': 1, 'txn_type': 'sell', 'strike': 14700, 'qty': 150, 'tr_qty': -150, 'expiry': '25Feb2021', 'optionType': 'ce', 'name': 'NIFTY21FEB14700CE', 'symbol': 39607, 'orderID': 10036280, 'tradedPrice': 111.9, 'dateTime': '2021-02-23 14:06:55', 'set_type': 'Entry'},
#             {'set': 1, 'txn_type': 'buy', 'strike': 14700, 'qty': 75, 'tr_qty': 75, 'expiry': '25Feb2021', 'optionType': 'ce', 'name': 'NIFTY21FEB14700CE', 'symbol': 39607, 'orderID': 10036285, 'tradedPrice': 117.8, 'dateTime': '2021-02-23 14:12:21', 'set_type': 'Repair'},
#             {'set': 1, 'txn_type': 'buy', 'strike': 14700, 'qty': 0, 'tr_qty': 75, 'expiry': '25Feb2021', 'optionType': 'ce', 'name': 'NIFTY21FEB14700CE', 'symbol': 39607, 'orderID': 10036301, 'tradedPrice': 122.4, 'dateTime': '2021-02-23 14:14:28', 'set_type': 'Exit'},
#             {'set': 2, 'txn_type': 'sell', 'strike': 14700, 'qty': 150, 'tr_qty': -150, 'expiry': '25Feb2021', 'optionType': 'ce', 'name': 'NIFTY21FEB14800CE', 'symbol': 39608, 'orderID': 10036280, 'tradedPrice': 7111.9, 'dateTime': '2021-02-23 14:06:55', 'set_type': 'Entry'},
#             {'set': 2, 'txn_type': 'buy', 'strike': 14700, 'qty': 75, 'tr_qty': 75, 'expiry': '25Feb2021', 'optionType': 'ce', 'name': 'NIFTY21FEB14800CE', 'symbol': 39608, 'orderID': 10036285, 'tradedPrice': 6117.8, 'dateTime': '2021-02-23 14:12:21', 'set_type': 'Repair'},
#             {'set': 3, 'txn_type': 'buy', 'strike': 14700, 'qty': 0, 'tr_qty': 75, 'expiry': '25Feb2021', 'optionType': 'ce', 'name': 'NIFTY21FEB14880CE', 'symbol': 39608, 'orderID': 10036301, 'tradedPrice': 5122.4, 'dateTime': '2021-02-23 14:14:28', 'set_type': 'Exit'}]
# orders=[{'refId':10001, 'setno':1, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"NIFTY", 'otype': "ce", 'status': "Idle", 'expiry': 'week', 'lot': 2, 'startTime':"09:30:00"},
# 		{'refId':10002, 'setno':2, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"NIFTY", 'otype': "pe", 'status': "Idle", 'expiry': 'week', 'lot': 2, 'startTime':"09:30:00"},
# 		{'refId':10003, 'setno':3, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"NIFTY", 'otype': "ce", 'status': "Idle", 'expiry': 'week', 'lot': 2, 'startTime':"10:00:00"},
# 		{'refId':10004, 'setno':4, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"NIFTY", 'otype': "pe", 'status': "Idle", 'expiry': 'week', 'lot': 2, 'startTime':"10:00:00"},
# 		{'refId':10005, 'setno':5, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"NIFTY", 'otype': "ce", 'status': "Idle", 'expiry': 'week', 'lot': 2, 'startTime':"10:30:00"},
# 		{'refId':10006, 'setno':6, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"NIFTY", 'otype': "pe", 'status': "Idle", 'expiry': 'week', 'lot': 2, 'startTime':"10:30:00"},
# 		{'refId':10007, 'setno':7, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"NIFTY", 'otype': "ce", 'status': "Idle", 'expiry': 'week', 'lot': 2, 'startTime':"11:00:00"},
# 		{'refId':10008, 'setno':8, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"NIFTY", 'otype': "pe", 'status': "Idle", 'expiry': 'week', 'lot': 2, 'startTime':"11:00:00"},
# 		{'refId':10000, 'setno':9, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"NIFTY", 'otype': "ce", 'status': "Idle", 'expiry': 'week', 'lot': 2, 'startTime':"11:30:00"},
# 		{'refId':10010, 'setno':10, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"NIFTY", 'otype': "pe", 'status': "Idle", 'expiry': 'week', 'lot': 2, 'startTime':"11:30:00"},
# 		{'refId':10011, 'setno':11, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"NIFTY", 'otype': "ce", 'status': "Idle", 'expiry': 'week', 'lot': 2, 'startTime':"13:30:00"},
# 		{'refId':10012, 'setno':12, 'ent_txn_type': "sell", 'rpr_txn_type': "buy", 'idx':"NIFTY", 'otype': "pe", 'status': "Idle", 'expiry': 'week', 'lot': 2, 'startTime':"13:30:00"}]
# universal = {'exit_status': 'Idle', 'minPrice': -12000, 'maxPrice': 24000, 'exitTime':'15:05:00', 'ext_txn_type':'buy'}