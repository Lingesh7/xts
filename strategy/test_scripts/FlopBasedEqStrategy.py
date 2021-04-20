# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 11:41:46 2021
Flop Strategey on EQ
@author: Welcome
"""
############## imports ##############
from datetime import datetime,date
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
import requests
from retry import retry
import os

try:
    os.chdir(r'D:\Python\First_Choice_Git\xts\strategy\test_scripts')
except:
    pass

############## logging ##############
logger = logging.getLogger('__main__')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

filename='../logs/FlopBasedEqStrategy_log.txt'

# file_handler = logging.FileHandler(filename)
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
token_file=f'../scripts/access_token_{cdate}.txt'
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
    # exit()

bot_file = '../ohlc/bot_token.txt'
fil = Path(bot_file)
if fil.exists():
    logger.info('Bot token file exists')
    b_tok = open(bot_file,'r').read()
else:
    logger.info('Bot token missing.')
    
################ variables ###############
# tickers = ['HDFCBANK','SBIN']
tickers= ['AUROPHARMA', 'AXISBANK', 'BPCL', 
           'BANDHANBNK', 'BAJFINANCE', 'DLF', 
           'HINDALCO', 'IBULHSGFIN', 'INDUSINDBK', 
           'ICICIBANK', 'INDIGO', 'JINDALSTEL', 
           'L&TFH', 'LICHSGFIN', 'MANAPPURAM', 
           'MARUTI', 'RBLBANK', 'SBIN', 
           'TATAMOTORS', 'TATASTEEL', 'VEDL']
#tickers=['TATAMOTORS']
refid=1
# flop=[]
# mark=[]
flop = {}
mark={}
tr_insts = []
etr_inst = {}
rpr_inst = {}
ext_inst = {}
ltp = {}
gl_pnl = None
pnl_dump = []
dead = False

################ functions ###############

def bot_sendtext(bot_message):
    userids = ['1647735620']#,'1245301878','1089456737']
    for userid in userids:
        bot_token = b_tok
        bot_chatID = userid
        send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
        response = requests.get(send_text)
        resp = response.json()
        if resp['ok']:
            logger.info('Sent message to followers')
    # return response.json()

@retry(n_tries=10, delay=15, kill=True)
def masterEqDump():
    global instrument_df
    filename=f'../ohlc/NSE_EQ_Instruments_{cdate}.csv'
    file = Path(filename)
    if file.exists() and (date.today() == date.fromtimestamp(file.stat().st_mtime)):
        logger.info('MasterDump already exists.. reading directly')
        instrument_df = pd.read_csv(filename,header='infer')
    else:
        logger.info('Creating MasterDump..')
        exchangesegments = [xt.EXCHANGE_NSECM]
        mastr_resp = xt.get_master(exchangeSegmentList=exchangesegments)
        # print("Master: " + str(mastr_resp))
        master=mastr_resp['result']
        spl=master.split('\n')
        mstr_df = pd.DataFrame([sub.split("|") for sub in spl],columns=(['ExchangeSegment','ExchangeInstrumentID','InstrumentType','Name','Description','Series','NameWithSeries','InstrumentID','PriceBand.High','PriceBand.Low','FreezeQty','TickSize',' LotSize']))
        instrument_df = mstr_df[mstr_df.Series == 'EQ']
        instrument_df.to_csv(f"../ohlc/NSE_EQ_Instruments_{cdate}.csv",index=False)


def instrumentLookup(instrument_df,ticker):
    """Looks up instrument token for a given script from instrument dump"""
    try:
        return int(instrument_df[instrument_df.Name==ticker].ExchangeInstrumentID.values[0])
    except:
        return -1


def fetchOHLC(ticker,duration):
    symbol = instrumentLookup(instrument_df,ticker)
    cur_date = datetime.strftime(datetime.now(), "%b %d %Y")
    nowtime = datetime.now().strftime('%H%M%S')
    ohlc = xt.get_ohlc(exchangeSegment=xt.EXCHANGE_NSECM,
                    exchangeInstrumentID=symbol,
                    startTime=f'{cur_date} 091500',
                    endTime=f'{cur_date} {nowtime}',
                    compressionValue=duration)
    dataresp= ohlc['result']['dataReponse']
    data = dataresp.split(',')
    data_df = pd.DataFrame([sub.split("|") for sub in data],columns=(['Timestamp','Open','High','Low','Close','Volume','OI','NA']))
    data_df.drop(data_df.columns[[-1,-2]], axis=1, inplace=True)
    data_df = data_df.astype(dtype={'Open': float, 'High': float, 'Low': float, 'Close': float, 'Volume': int})
    data_df['Timestamp'] = pd.to_datetime(data_df['Timestamp'].astype('int'), unit='s')
    return data_df


def vWAP(DF):
    #calculating VWAP and UB , LB values
    df = DF.copy()
    df['vwap'] = (df.Volume*(df.High+df.Low+df.Close)/3).cumsum() / df.Volume.cumsum()
    df['uB'] = df.vwap * 1.002
    df['lB'] = df.vwap * 0.998
    return df


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
               raise Exception("Error in getOrderList func")
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
        order_resp = xt.place_order(exchangeSegment=xt.EXCHANGE_NSECM,
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
                                                if orderList['AppOrderID'] == orderID and \
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
            logger.error(order_resp['description'])
            logger.info(f'Order not placed for - {symbol} ')
            raise Exception('Order not placed - ')
    except:
        raise ex.XTSOrderException('Unable to place order in placeOrder func...')
        logger.exception('Unable to place order in placeOrder func...')
        time.sleep(1)


def preparePlaceOrders(ticker,txn_type,quantity):
    global etr_inst,tr_insts
    logger.info('===================')
    logger.info(f'placing {txn_type} order')
    logger.info('===================')
    # placeOrder()
    etr_inst['txn_type'] = txn_type
    etr_inst['qty'] = quantity
    etr_inst['tr_qty'] = quantity if txn_type == 'buy' else -quantity
    etr_inst['name'] = ticker
    etr_inst['symbol'] = instrumentLookup(instrument_df,ticker) #todo symbol should be calculated here
    etr_inst['orderID'] = None
    etr_inst['tradedPrice'] = None
    orderID, tradedPrice, dateTime = placeOrder(etr_inst['symbol'], etr_inst['txn_type'], etr_inst['qty'])
    etr_inst['orderID'] = orderID
    etr_inst['tradedPrice'] = tradedPrice
    etr_inst['dateTime'] = dateTime
    if orderID and tradedPrice:
        etr_inst['set_type'] = 'Entry'
        logger.info(f'Entry details : {tr_insts}')
        tr_insts.append(etr_inst.copy())
        # logger.info(f'Entry tr_insts: {tr_insts}')


def getLTP():
    global ltp
    # ltp={}
    if tr_insts:
        # logger.info('inside tr_insts cond - getLTP')
        symbols=[i['symbol'] for i in tr_insts]
        instruments=[]
        for symbol in symbols:
            instruments.append({'exchangeSegment': 1, 'exchangeInstrumentID': symbol})
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
        df = df.astype(dtype={'txn_type': str, 'qty': int, 'tr_qty': int, \
                                 'name': str, 'symbol': int, 'orderID': int, 'tradedPrice': float, 'dateTime': str, \
                                 'set_type': str, 'tr_amount': float})
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


def slTgtCheck():
    global tr_insts, dead
    while not dead:
        time.sleep(5)
        if tr_insts:
            for trade in tr_insts:
                if trade['set_type'] == 'Entry':
                    if trade['symbol'] in ltp.keys():
                        logger.info(f'sl-tgt check on {trade["name"]}')
                        if  ((ltp[trade['symbol']] >= (trade['tradedPrice'] + trade['tradedPrice']*(1.5/100))) \
                              or (ltp[trade['symbol']] <= (trade['tradedPrice'] - trade['tradedPrice']*(1/100)))) \
                                  and trade['txn_type'] == 'buy':
                            logger.info(f'stoploss or targrt condition met in buy side. Closing the position {trade["name"]}')
                            # side = 'sell' if trade['txn_type'] == 'buy' else 'buy'
                            rpr_inst['txn_type'] = 'sell'
                            rpr_inst['qty'] = trade['qty']
                            rpr_inst['tr_qty'] = -rpr_inst['qty']
                            rpr_inst['name'] = trade['name']
                            rpr_inst['symbol'] = trade['symbol']
                            rpr_inst['orderID'] = None
                            rpr_inst['tradedPrice'] = None
                            orderID, tradedPrice, dateTime = placeOrder(rpr_inst['symbol'],rpr_inst['txn_type'], rpr_inst['qty'])
                            rpr_inst['orderID'] = orderID
                            rpr_inst['tradedPrice'] = tradedPrice
                            rpr_inst['dateTime'] = dateTime
                            if orderID and tradedPrice:
                                rpr_inst['set_type'] = 'Repair'
                                trade['set_type'] = 'Repaired'
                                logger.info(f'Repair details : {rpr_inst}')
                                tr_insts.append(rpr_inst.copy())
                                logger.info(f' Repair tr_insts: {tr_insts}')

                        elif  ((ltp[trade['symbol']] <= (trade['tradedPrice'] - trade['tradedPrice']*(1.5/100))) \
                              or (ltp[trade['symbol']] >= (trade['tradedPrice'] + trade['tradedPrice']*(1/100)))) \
                                  and trade['txn_type'] == 'sell':
                            logger.info(f'stoploss or targrt condition met in sell side. Closing the position {trade["name"]}')
                            # orderID, tradedPrice, dateTime = placeOrder(trade['symbol'], 'buy', trade['qty'])
                            rpr_inst['txn_type'] = 'buy'
                            rpr_inst['qty'] = trade['qty']
                            rpr_inst['tr_qty'] = rpr_inst['qty']
                            rpr_inst['name'] = trade['name']
                            rpr_inst['symbol'] = trade['symbol']
                            rpr_inst['orderID'] = None
                            rpr_inst['tradedPrice'] = None
                            orderID, tradedPrice, dateTime = placeOrder(rpr_inst['symbol'],rpr_inst['txn_type'], rpr_inst['qty'])
                            rpr_inst['orderID'] = orderID
                            rpr_inst['tradedPrice'] = tradedPrice
                            rpr_inst['dateTime'] = dateTime
                            if orderID and tradedPrice:
                                rpr_inst['set_type'] = 'Repair'
                                trade['set_type'] = 'Repaired'
                                logger.info(f'Repair details : {rpr_inst}')
                                tr_insts.append(rpr_inst.copy())
                                logger.info(f'Repair tr_insts: {tr_insts}')

    logger.info('flop checker ends - squaring off remaining trades')
    if tr_insts:
        for trades in tr_insts:
            if trade['set_type'] == 'Entry':
                if trade['txn_type'] == 'buy':
                    ext_inst['txn_type'] = 'sell'
                    ext_inst['qty'] = trade['qty']
                    ext_inst['tr_qty'] = -ext_inst['qty']
                    ext_inst['name'] = trade['name']
                    ext_inst['symbol'] = trade['symbol']
                    ext_inst['orderID'] = None
                    ext_inst['tradedPrice'] = None
                    orderID, tradedPrice, dateTime = placeOrder(ext_inst['symbol'],ext_inst['txn_type'], ext_inst['qty'])
                    ext_inst['orderID'] = orderID
                    ext_inst['tradedPrice'] = tradedPrice
                    ext_inst['dateTime'] = dateTime
                    if orderID and tradedPrice:
                        ext_inst['set_type'] = 'Exit'
                        trade['set_type'] = 'Exited'
                        logger.info(f'Repair details : {ext_inst}')
                        tr_insts.append(ext_inst.copy())
                        logger.info(f' Repair tr_insts: {tr_insts}')
                if trade['txn_type'] == 'sell':
                    ext_inst['txn_type'] = 'buy'
                    ext_inst['qty'] = trade['qty']
                    ext_inst['tr_qty'] = ext_inst['qty']
                    ext_inst['name'] = trade['name']
                    ext_inst['symbol'] = trade['symbol']
                    ext_inst['orderID'] = None
                    ext_inst['tradedPrice'] = None
                    orderID, tradedPrice, dateTime = placeOrder(ext_inst['symbol'],ext_inst['txn_type'], ext_inst['qty'])
                    ext_inst['orderID'] = orderID
                    ext_inst['tradedPrice'] = tradedPrice
                    ext_inst['dateTime'] = dateTime
                    if orderID and tradedPrice:
                        ext_inst['set_type'] = 'Exit'
                        trade['set_type'] = 'Exited'
                        logger.info(f'Exit Buy details : {ext_inst}')
                        tr_insts.append(ext_inst.copy())
                        logger.info(f'tr_insts: {tr_insts}')
            
    
def main(capital):
    global refid, flop, mark
    #msg_sent = False
    try:
        for ticker in tickers:
            try:
                logger.info(f"Checking for {ticker} at {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
                if ticker not in flop:
                    flop[ticker] = []
                if ticker not in mark:
                    mark[ticker] = []
                data_df = fetchOHLC(ticker, 60)
                df = vWAP(data_df)
                logger.info(f"tick {df['Timestamp'].iloc[-2]}")
                #logger.info(f"{df.iloc[-2]}")
                quantity = int(capital/df["Close"].iloc[-1])
                if pd.Timestamp(df['Timestamp'].iloc[-1]) >= pd.Timestamp(cdate+" "+'09:31:00'):
                    idx = len(flop[ticker])-1
                    if df['Close'].iloc[-2] >= df['uB'].iloc[-2] :
                        logger.info(f'Upper bound break in {ticker}')
                        # print('Long', df['Timestamp'].values[i])
                        if not flop[ticker]:
                            flop[ticker].append('Long')
                            mark[ticker].append({'refid':refid, 'side': 'Long', 'time': df['Timestamp'].iloc[-2], 'price': df['Close'].iloc[-2]})
                            refid += 1
                            logger.info(f'1st flop list of {ticker}          is : {flop[ticker]}')
                            logger.info(f'1st mark list of {ticker} is : {mark[ticker]}')
                        elif flop[ticker][-1] != 'Long':
                            lowPriceAfterFlop = df[df.Timestamp.between(mark[ticker][idx]['time'],df['Timestamp'].values[-2])]['Close'].min()
                            if (mark[ticker][idx]['price'] - lowPriceAfterFlop) < (mark[ticker][idx]['price'] * (0.5/100)):
                                flop[ticker].append('Long')
                                mark[ticker].append({'set':refid, 'side': 'Long',
                                             'time': df['Timestamp'].values[-2],
                                             'price': df['Close'].values[-2]})
                                refid += 1
                                logger.info(f'flop list of {ticker} is : {flop[ticker]}')
                                logger.info(f'mark list of {ticker} is : {mark[ticker]}')
    
                                if len(flop[ticker]) >= 3:
                                    msg = f'Flop condition satisified in ==> {ticker} ==> Go Long'
                                    #if msg_sent == False:
                                    bot_sendtext(msg)
                                    #    msg_sent = True
                                    preparePlaceOrders(ticker,'buy',quantity)
                            else:
                                logger.info('Previous break is not a flop.. starting from begining')
                                flop[ticker]=[]
                                mark[ticker]=[]
    
                    if df['Close'].values[-2] <= df['lB'].values[-2]:
                        idx = len(flop[ticker])-1
                        if not flop[ticker]:
                            flop[ticker].append('Short')
                            mark[ticker].append({'set':refid, 'side': 'Short',
                                         'time': df['Timestamp'].values[-2],
                                         'price': df['Close'].values[-2]})
                            refid += 1
                            logger.info(f'1st flop list of {ticker} is : {flop[ticker]}')
                            logger.info(f'1st mark list of {ticker} is : {mark[ticker]}')
                        elif flop[ticker][-1] != 'Short':
                            highPriceAfterFlop = df[df.Timestamp.between(mark[ticker][idx]['time'],df['Timestamp'].values[-2])]['High'].max()
                            if (highPriceAfterFlop - mark[ticker][idx]['price']) < (mark[ticker][idx]['price'] * (0.5/100)):
                                flop[ticker].append('Short')
                                mark[ticker].append({'set':refid, 'side': 'Short',
                                            'time': df['Timestamp'].values[-2],
                                            'price': df['Close'].values[-2]})
                                refid += 1
                                logger.info(f'flop list of {ticker} is : {flop[ticker]}')
                                logger.info(f'mark list of {ticker} is : {mark[ticker]}')
    
                                if len(flop) >= 3:
                                    msg = f'Flop condition satisified in ==> {ticker} ==> Go Short'
                                    if msg_sent == False:
                                        bot_sendtext(msg)
                                        msg_sent = True
                                    preparePlaceOrders(ticker,'sell',quantity)
                            else:
                                logger.info('Previous break is not a flop.. starting from begining')
                                flop[ticker]=[]
                                mark[ticker]=[]
            except:
                logger.exception("API error for ticker :",ticker)
    except KeyboardInterrupt:
        raise
        logger.error('\n\nKeyboard exception received. Exiting.')


def dataToExcel(pnl_dump):
    if pnl_dump:
        try:
            pnl_df = pd.DataFrame(pnl_dump,columns=['date','pl'])
            pnl_df = pnl_df.set_index(['date'])
            pnl_df.index = pd.to_datetime(pnl_df.index, format='%d-%m-%Y %H:%M:%S')
            resampled_df = pnl_df['pl'].resample('1min').ohlc()
            #writing the output to excel sheet
            writer = pd.ExcelWriter('../pnl/FlopBasedEqStrategy_PnL.xlsx',engine='openpyxl')
            writer.book = load_workbook('../pnl/FlopBasedEqStrategy_PnL.xlsx')
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
        except Exception:
            logger.exception('Saving data to Excel Failed')



if __name__ == '__main__':
    masterEqDump()
    logger.info('Waiting to start the script at 09:29 AM')
    while datetime.now() >= pd.Timestamp(cdate+" "+'09:29:00'):
        logger.info('Starting background threads to fetch ltps, pnl')
        fetchLtp = timer.RepeatedTimer(5, getLTP)
        fetchPnL = timer.RepeatedTimer(10, getGlobalPnL)
        sltgt_thread = Thread(target=slTgtCheck)
        sltgt_thread.start()
        break
        
    # for ticker in tickers:
    #     preparePlaceOrders(ticker,'buy',10)
    while datetime.now() >= pd.Timestamp(cdate+" "+'09:29:00'):
        
    startin = time.time()
    #timeout = time.time() + ((60*60*6) - 300) # 60 seconds times 360 meaning 6 hrs
    while datetime.now() >= pd.Timestamp(cdate+" "+'15:05:00')::
        try:
            main(100000) #flop checker
            time.sleep(60 - ((time.time() - startin) % 60.0))
        except KeyboardInterrupt:
            logger.exception('\n\nKeyboard exception received. Exiting.')
            exit()
        except:
            logger.exception('\n\nCritical main function error.. Exiting.')
            exit()
        # finally:
    # main function might have ended based on condition or by exception hence below actions
    dead = True #to stop the background thread
    logger.info('stopping bg threads..')
    fetchLtp.stop()
    fetchPnL.stop()
    sltgt_thread.join()
    dataToExcel(pnl_dump)
    logger.info('--------------------------------------------')
    logger.info(f'Total Orders and its status: \n {tr_insts} \n')
    logger.info('Summary')
    logger.info(f'\n\n PositionList: \n {df}')
    logger.info(f'\n\n CombinedPositionsLists: \n {gdf}')
    logger.info(f'\n\n Global PnL : {gl_pnl} \n')
    logger.info('--------------------------------------------')
    logger.info('============================== END =================================')



# ['AUROPHARMA', 'AXISBANK', 'BPCL', 'BANDHANBNK', 'BAJFINANCE', 'DLF', 'HINDALCO', 'IBULHSGFIN', 'INDUSINDBK', 'ICICIBANK', 'INDIGO', 'JINDALSTEL', 'L&TFH', 'LICHSGFIN', 'MANAPPURAM', 'MARUTI', 'RBLBANK', 'SBIN', 'TATAMOTORS', 'TATASTEEL', 'VEDL']
