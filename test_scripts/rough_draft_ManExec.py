# -*- coding: utf-8 -*-
"""
Created on Wed Dec 30 11:02:52 2020
Live execution - manual 
@author: Welcome
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta, TH
from XTConnect.Connect import XTSConnect
import time
import pandas as pd
from sys import exit
from nsetools import Nse
nse = Nse()
import schedule

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
    weekly_exp=str((month_last_thu_expiry.strftime("%d")))+month_last_thu_expiry.strftime("%b").capitalize()+month_last_thu_expiry.strftime("%Y")
    monthly_exp=str((next_thursday_expiry.strftime("%d")))+next_thursday_expiry.strftime("%b").capitalize()+next_thursday_expiry.strftime("%Y")
 
def strkPrcCalc(ltp,base):    
    return base * round(ltp/base)


def get_eID(symbol,ce_pe,expiry,strikePrice):
    # print("Current nifty price is:", nfty_ltp)
    # print("Current BankNifty price is:", bnknfty_ltp)
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
    return int(eID_resp["result"][0]["ExchangeInstrumentID"])

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

def placeOrderWithSL(symbols,buy_sell,quantity):  
    # Place an intraday stop loss order on NSE
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
        for symbol in symbols:
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
           # # extracting the order id from response
            if order_resp['type'] != 'error':
                 orderID = order_resp['result']['AppOrderID']
                 print(f''' Order ID for {t_type} {symbol} is: ", {orderID}''')
            elif order_resp['type'] == 'error':
                    print("Error placing Order.. Exiting...")
                    exit()
            # time.sleep(3)
            # stopPrice = 0
            #get trade price of the last order processed from orderList
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
            else:
                print("Error placing SL Order.. try again manually...")
        return True
    except:
        return False

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

def getPositionList():
    a = 0
    while a < 10:
        try:
           pos_resp = xt.get_position_daywise()
           positionList = pos_resp['result']['positionList']
           return positionList
           break
        except:
            print("Can't extract position data...retrying")
            a+=1
            
def get_global_PnL():
    global pos_df
    totalMTMdf = 0.0
    positionList=getPositionList()
    if positionList:
        posDf = pd.DataFrame(positionList)
        # posDf['MTM'].replace({',':''},regex=True).apply(pd.to_numeric,1).sum()
        totalMTMdf = posDf['MTM'].replace({',':''},regex=True).apply(pd.to_numeric,1).sum()
        return totalMTMdf
    else:
        return totalMTMdf
    
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
    
    
def prepareVars(ticker): 
    try:
        # for ticker in tickers:
        global net_cash, margin_ok, quantity,eID,strikePrice
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
        return True
    except:
        print("unable to set variables to place order")
        return False


def runOrders(go):
    # nstart=True
    # ndate = datetime.strftime(datetime.now(), "%d-%m-%Y")
    if go:
        if margin_ok:
            print("Required Margin Available.. Taking positions...")
            print(f"symbol = {ticker} EID = {eID} expiry = {weekly_exp} strikePrice = {strikePrice} ")#.format(ticker,expiry,Otype,strikePrice,eID))
            # while nstart:
            #     if (datetime.now() >= datetime.strptime(ndate + " 14:31:00", "%d-%m-%Y %H:%M:%S")):
            monitor = placeOrderWithSL(eID,'sell',quantity)
            runSqOffLogics(monitor)
            # placeOrderWithSL(eID2,'sell',quantity)
            # nstart = False
            # else:
            #         print("Waiting to place the order at 09:48...")
            #         time.sleep(5)
            #        else:
        else:
            # cur_cash = checkBalance()
            print(f''' \t Margin is less to place orders... 
                  Required cash : 55000
                   But cash available is: {net_cash}
                    Exiting without placing any orders.. 
                  ''')     
    else:
        print("vars not set....")
  

def runSqOffLogics(monitor):
    if monitor:
        cdate = datetime.strftime(datetime.now(), "%d-%m-%Y")
        check=True
        m=0
        bag=[]
        while check:
            cur_PnL = get_global_PnL()
            if (cur_PnL < -1500) or (cur_PnL >= 3000) or (datetime.now() >= datetime.strptime(cdate + " 15:10:00", "%d-%m-%Y %H:%M:%S")):
                #closing all open positions
                # positionList=xt.get_position_daywise()['result']['positionList']
                # pos_df = pd.DataFrame(positionList)
                for i in range(len(pos_df)):
                    if int(pos_df["Quantity"].values[i]) != 0:
                        symbol=pos_df['TradingSymbol'].values[i]
                        eid = pos_df["ExchangeInstrumentId"].values[i]
                        squareOff(eid,symbol)
                print("Position Squareoff COmpleted ")
                
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
                        
                check=False #exit this main loop
            else:
                # print(time.strftime("%d-%m-%Y %H:%M:%S"),",",get_global_PnL())
                # time.sleep(10)
                data = time.strftime("%d-%m-%Y %H:%M:%S"),",",cur_PnL
                # print(data)
                bag.append(data) 
                m+=1
                if len(bag) >= 10:
                    tup=bag[-1]
                    bagstr=" ".join(str(x) for x in tup)
                    print(bagstr)
                    bag = []
                    m=0
                # print(m,len(bag))
                time.sleep(2)
    else:
        print("No Orders Placed")
        
def scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)
###################################################
#maybe main()

ticker='NIFTY'

go = prepareVars(ticker)
runOrders(go)

# monitor=1
# runSqOffLogics(monitor)

# schedule.every().day.at('10:00').do(runOrders,go)

# scheduler()
# start = time.time()
# runOrders(prepareVars(ticker))
# print(f'Time: {time.time() - start}')



# schedule.every().day.at('09:45').do(runOrders,go)
    

# ###################################################
# #maybe main()    
    
# tickers = ["NIFTY"] 
# for ticker in tickers:
#     # for oType in "ce","pe":
#     weekly_exp,monthly_exp = nextThu_and_lastThu_expiry_date()
#     #expiry = get_expiry_from_option_chain(ticker)
#     # weekly_exp,monthly_exp=(expiry[:2])
#     if ticker == "NIFTY":
#          quantity = 75
#          nfty_ltp = nse.get_index_quote("nifty 50")['lastPrice']
#          strikePrice = strkPrcCalc(nfty_ltp,50)
#          margin_ok = int(checkBalance()) >= 55000
#     if ticker == "BANKNIFTY":
#         quantity = 25
#         bnknfty_ltp = nse.get_index_quote("nifty bank")['lastPrice']
#         strikePrice = strkPrcCalc(bnknfty_ltp,100)
#         margin_ok = int(checkBalance()) >= 55000
#     print(f"symbol = {ticker}  expiry = {weekly_exp}  strikePrice = {strikePrice } ")#.format(ticker,expiry,Otype,strikePrice,eID))
#     if margin_ok:
#         # eID = get_eID(ticker,oType,weekly_exp,strikePrice)
#         eID = [ (get_eID(ticker,i,weekly_exp,strikePrice)) for i in ['ce','pe'] ]
#         print("EID is :", eID)
#         nstart=True
#         ndate = datetime.strftime(datetime.now(), "%d-%m-%Y")
#         while nstart:
#             if (datetime.now() >= datetime.strptime(ndate + " 09:45:00", "%d-%m-%Y %H:%M:%S")):
#                 placeOrderWithSL(eID,'sell',quantity)
#                 nstart = False
#             else:
#                 print("Waiting to place the order at 09:48...")
#                 time.sleep(5)
#     else:
#         cur_cash = checkBalance()
#         print(f'''Margin is less to place orders... 
#                   Required cash avalable in your trading account should be 55000
#                   But cash available is: {cur_cash}
#                   Exiting without placing any orders.. 
#                   ''')
    

# print('#################--CODE ENDS HERE#--###################')

# get_global_PnL()

        
# print(time.strftime("%d-%m-%Y %H:%M:%S"),"|",get_global_PnL())            
# xt.get_position_daywise()['result']['positionList']        
# if get_global_PnL() > -200:
#     print(time.strftime("%d-%m-%Y %H:%M:%S"),"|",get_global_PnL())


# orderList=xt.get_order_book()['result']
# orderDf = pd.DataFrame(orderList)

# tradeList=xt.get_trade()['result']
# tradeDf = pd.DataFrame(tradeList)

# positionList=xt.get_position_daywise()['result']['positionList']
# posDf = pd.DataFrame(positionList)
