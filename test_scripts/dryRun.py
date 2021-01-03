# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 23:21:16 2020
@author: mling
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta, TH
from XTConnect.Connect import XTSConnect
import time
# Trading Interactive Creds
API_KEY = "ebaa4a8cf2de358e53c942"
API_SECRET = "Ojre664@S9"

# MarketData Creds
# API_KEY = "ebaa4a8cf2de358e53c942"
# API_SECRET = "Ojre664@S9"


XTS_API_BASE_URL = "https://xts-api.trading"
source = "WEBAPI"
xt = XTSConnect(API_KEY, API_SECRET, source)

response = xt.interactive_login()
# response = xt.marketdata_login()

print("Login: ", response)

def nextThu_and_lastThu_expiry_date ():

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
    str_month_last_thu_expiry=str(int(month_last_thu_expiry.strftime("%d")))+month_last_thu_expiry.strftime("%b").capitalize()+month_last_thu_expiry.strftime("%Y")
    str_next_thursday_expiry=str(int(next_thursday_expiry.strftime("%d")))+next_thursday_expiry.strftime("%b").capitalize()+next_thursday_expiry.strftime("%Y")
    return (str_next_thursday_expiry,str_month_last_thu_expiry)

nThu,lThu=nextThu_and_lastThu_expiry_date()


from nsetools import Nse
nse = Nse()

nfty_ltp = nse.get_index_quote("nifty 50")['lastPrice']
bnknfty_ltp = nse.get_index_quote("nifty bank")['lastPrice']

print("Current nifty price is:", nfty_ltp)
print("Current BankNifty price is:", bnknfty_ltp)

def strkPrcCalc(ltp,base):    
    return base * round(ltp/base)

def get_eID(symbol,ce_pe,expiry):
    nfty_ltp = nse.get_index_quote("nifty 50")['lastPrice']
    bnknfty_ltp = nse.get_index_quote("nifty bank")['lastPrice']

    print("Current nifty price is:", nfty_ltp)
    print("Current BankNifty price is:", bnknfty_ltp)
    if ce_pe == "ce":
        oType="CE"
    elif ce_pe == "pe":
        oType="PE"
    if symbol == "NIFTY":
        strikePrice= strkPrcCalc(nfty_ltp,50)
    elif symbol == "BANKNIFTY":
        strikePrice= strkPrcCalc(bnknfty_ltp,100)
    print("strike Price calculated as :", strikePrice)
    print("expiry date caluclated as :", expiry)
    response = xt.get_option_symbol(
    exchangeSegment=2,
    series='OPTIDX',
    symbol=symbol,
    expiryDate=expiry,
    optionType=oType,
    strikePrice=strikePrice)
    #print('Option Symbol:', str(response))
    print("ExchangeInstrumentID is:", (int(response["result"][0]["ExchangeInstrumentID"])))
    return int(response["result"][0]["ExchangeInstrumentID"])
   
xt.get_option_symbol(
    exchangeSegment=2,
    series='OPTIDX',
    symbol='NIFTY',
    expiryDate='07JAN2021',
    optionType='CE',
    strikePrice=13750)


 

get_eID("NIFTY","pe",nThu)
# get_eID("BANKNIFTY","pe",lThu)

def placeMarketOrder(symbol,buy_sell,ce_pe,exp,mul=1):    
    # Place an intraday market order on NSE
    if buy_sell == "BUY":
        t_type=xt.TRANSACTION_TYPE_BUY
    elif buy_sell == "SELL":
        t_type=xt.TRANSACTION_TYPE_SELL
    if symbol == "NIFTY":
        eID = get_eID(symbol,ce_pe,exp)
        quantity = mul*75
    elif symbol == "BANKNIFTY":
        eID = get_eID(symbol,ce_pe,exp)
        quantity = mul*25
    print("placing market order::")
    order_resp = xt.place_order(exchangeSegment=xt.EXCHANGE_NSEFO,
                   exchangeInstrumentID= eID ,
                   productType=xt.PRODUCT_MIS, 
                   orderType=xt.ORDER_TYPE_MARKET,                   
                   orderSide=t_type,
                   timeInForce=xt.VALIDITY_DAY,
                   disclosedQuantity=0,
                   orderQuantity=quantity,
                   limitPrice=0,
                   stopPrice=0,
                   orderUniqueIdentifier="pl_test5"
                   )
    # print(f'''placing Market  Order = xt.place_order(exchangeSegment=xt.EXCHANGE_NSEFO,
    #                exchangeInstrumentID= {eID} ,
    #                productType=xt.PRODUCT_MIS, 
    #                orderType=xt.ORDER_TYPE_MARKET,                   
    #                orderSide={t_type},
    #                timeInForce=xt.VALIDITY_DAY,
    #                disclosedQuantity=0,
    #                orderQuantity={quantity},
    #                # orderUniqueIdentifier="1test1"
    #                )''')
    # print("Place Order: ", oder_resp)
    # return oder_resp
    # oder_resp = {'type': 'success', 'code': 's-orders-0001', 'description': 'Request sent', 'result': {'AppOrderID': 10026325, 'OrderUniqueIdentifier': '123777', 'ClientID': 'IIFL24'}}
    # # extracting the order id from response
    if order_resp['type'] != 'error':
         orderID = order_resp['result']['AppOrderID']
         print("order id after ordering place market order function", orderID)
    time.sleep(15)
    orderBook = xt.get_order_book()
    print(":::getting orderBook:::")
    orderBook =  {'type': 'success', 'code': 's-orders-0001', 'description': 'Success order book', 'result': [{'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10026325, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_30698343', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 39972, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '31.80', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-21T14:49:16.0287269', 'ExchangeTransactTime': '2020-12-21T14:49:16+05:30', 'LastUpdateDateTime': '2020-12-21T14:49:16.350748', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': '123777', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 307029544554927}]}
    orderList = orderBook["result"]
    print("orderList has:", orderList)
    
    orderBook['result']
    
    for i in orderList:
        # print(i)
        # print(i["AppOrderID"])
        if orderID == i["AppOrderID"] and i["OrderStatus"] == 'Filled':
            orderPrice = float(( i["OrderAverageTradedPrice"]))
            if  i["OrderSide"] == 'Sell':
                sl_tType = 'BUY'
            elif i["OrderSide"] == 'Buy':
                sl_tType = 'SELL'
            print("orderid:",i["AppOrderID"] , "orderprice:", orderPrice,"sl_type:",sl_tType,"eid:",eID,"qty:",quantity)
            placeSLMOrder(eID,orderPrice,sl_tType,quantity)
        else:
            print(":::Not booked SL order:::", i["OrderStatus"])
            
    
def placeSLMOrder(eID,orderPrice,sl_tType,quantity): 
    print("inside SLM order def:::")
    if sl_tType == "BUY":
        t_type=xt.TRANSACTION_TYPE_BUY
    elif sl_tType == "SELL":
        t_type=xt.TRANSACTION_TYPE_SELL
    print("triggereing StopLoss Order:::")
    SL_Order_resp = xt.place_order(exchangeSegment=xt.EXCHANGE_NSEFO,
                   exchangeInstrumentID= eID ,
                   productType=xt.PRODUCT_MIS, 
                   orderType=xt.ORDER_TYPE_MARKET,                   
                   orderSide=t_type,
                   timeInForce=xt.VALIDITY_DAY,
                   disclosedQuantity=0,
                   orderQuantity=quantity,
                   limitPrice=0,
                   stopPrice=orderPrice+15,
                   orderUniqueIdentifier="sl_test5"
                   )
    # print(f'''StopLoss order after place order = xt.place_order(exchangeSegment=xt.EXCHANGE_NSEFO,
    #                exchangeInstrumentID= {eID} ,
    #                productType=xt.PRODUCT_MIS, 
    #                orderType=xt.ORDER_TYPE_STOPMARKET,                   
    #                orderSide={t_type},
    #                timeInForce={xt.VALIDITY_DAY},
    #                disclosedQuantity=0,
    #                orderQuantity={quantity},
    #                stopPrice={orderPrice+15}
    #                )''')
    print(SL_Order_resp)
    if SL_Order_resp['type'] != 'error':
         SL_orderID = SL_Order_resp['result']['AppOrderID']
         print("order id after ordering place StopLoss market order function:", SL_orderID)

            
         
# placeMarketOrder("NIFTY","BUY","pe",lThu,1)
# placeMarketOrder("BANKNIFTY","SELL","pe",nThu,2)


placeMarketOrder("NIFTY","SELL","ce",nThu,4) #sl_test2 pl_test2

placeMarketOrder("NIFTY","BUY","ce",nThu,4) #sl_test3 pl_test3

placeMarketOrder("BANKNIFTY","SELL","ce",lThu,1) #sl_test5 pl_test5



sq_off = xt.squareoff_position(
    exchangeSegment=xt.EXCHANGE_NSECM,
    exchangeInstrumentID=39992,
    productType=xt.PRODUCT_MIS,
    squareoffMode=xt.SQUAREOFF_DAYWISE,
    positionSquareOffQuantityType=xt.SQUAREOFFQUANTITY_EXACTQUANTITY,
    squareOffQtyValue=0,
    blockOrderSending=True,
    cancelOrders=True)
print("Position Squareoff: ", sq_off)



response = xt.get_order_book()
print("Order Book: ", response)

response = xt.get_trade()
print("Trade Book: ", response)

"""Get Position by DAY Request"""
response = xt.get_position_daywise()
print("Position by Day: ", response)

ab = round((77.77+15),2)

placed_order = xt.place_order(exchangeSegment=xt.EXCHANGE_NSEFO,
                   exchangeInstrumentID=39992,
                   productType=xt.PRODUCT_MIS, 
                   orderType=xt.ORDER_TYPE_MARKET,                   
                   orderSide=xt.TRANSACTION_TYPE_SELL,
                   timeInForce=xt.VALIDITY_DAY,
                   disclosedQuantity=0,
                   orderQuantity=75,
                   limitPrice=0,
                   stopPrice=0,
                   orderUniqueIdentifier="dec29_1"
                   )
if placed_order['type'] != 'error':
         placed_orderID = placed_order['result']['AppOrderID']
         print("order id after ordering place StopLoss market order function", placed_orderID)

dummy_SL_resp= xt.place_order(exchangeSegment=xt.EXCHANGE_NSEFO,
                   exchangeInstrumentID= 39992 ,
                   productType=xt.PRODUCT_MIS, 
                   orderType="StopMarket",                   
                   orderSide=xt.TRANSACTION_TYPE_SELL,
                   timeInForce=xt.VALIDITY_DAY,
                   disclosedQuantity=0,
                   orderQuantity=75,
                   limitPrice=0,
                   stopPrice=88.85+15,
                   orderUniqueIdentifier="slm_dummy1"
                   )
if dummy_SL_resp['type'] != 'error':
         dummy_SL_OID = dummy_SL_resp['result']['AppOrderID']
         print("order id after ordering place StopLoss market order function", dummy_SL_OID)

   

orderBook = {'type': 'success', 'code': 's-orders-0001', 'description': 'Success order book', 'result': [{'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10026335, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_30698353', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 39972, 'OrderSide': 'Buy', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '23.90', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-21T14:59:41.1535468', 'ExchangeTransactTime': '2020-12-21T14:59:42+05:30', 'LastUpdateDateTime': '2020-12-21T14:59:42.1276213', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': '123888','IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 307029544559178}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10026325, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_30698343', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 39972, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '31.80', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-21T14:49:16.0287269', 'ExchangeTransactTime': '2020-12-21T14:49:16+05:30', 'LastUpdateDateTime': '2020-12-21T14:49:16.350748', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': '123777', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 307029544559177}]}
# orderID = 10026325
orderList = orderBook["result"]
sl_tType ='Sell'
for i in orderList:
    # print(i)
    print(i["AppOrderID"], i["OrderStatus"],i["OrderAverageTradedPrice"], i["OrderPrice"])
    # if orderID == i["AppOrderID"] and i["OrderStatus"] == 'Filled':
    #         orderPrice = float(( i["OrderAverageTradedPrice"]))
    #         if  i["OrderSide"] == 'Sell':
    #             sl_tType = 'BUY'
    #         elif i["OrderSide"] == 'Buy':
    #             sl_tType = 'SELL'
    #         print(orderPrice,sl_tType)
            
type(orderList[0])


orderDf = pd.DataFrame(orderList)
print(df)
type(df)

df1 = df[['LoginID','OrderSide','AppOrderID','OrderAverageTradedPrice','OrderStatus']]

df.AppOrderID
df['AppOrderID']
df.iloc[0]
df3 = df.iloc[[0],[0]]




    

import pandas as pd
tradeBook =  xt.get_trade()
tradeList = tradeBook["result"]
for i in tradeList:
    print(i["OrderUniqueIdentifier"],i["AppOrderID"], i["OrderSide"],i["OrderStatus"], i["OrderPrice"], i["OrderAverageTradedPrice"])
##################################







instruments = [
    {'exchangeSegment': 2, 'exchangeInstrumentID': 39992}]

"""Get Quote Request"""
response = xt.get_quote(
    Instruments=instruments,
    xtsMessageCode=1504,
    publishFormat='JSON')
print('Quote :', response)



"""Search Instrument by Scriptname Request"""
response = xt.search_by_scriptname(searchString='INFY')
print('Search By Symbol :', str(response))


"""instruments list"""
instruments = [
    {'exchangeSegment': 2, 'exchangeInstrumentID': 39502},
    {'exchangeSegment': 2, 'exchangeInstrumentID': 47496}]

"""Get Quote Request"""
response = xt.get_quote(
    Instruments=instruments,
    xtsMessageCode=1504,
    publishFormat='JSON')
print('Quote :', response)

"""Search Instrument by ID Request"""
response = xt.search_by_instrumentid(Instruments=instruments)
print('Search By Instrument ID:', str(response))


"""Get Index List Request"""
response = xt.get_index_list(exchangeSegment=xt.EXCHANGE_NSECM)
print('Index List:', str(response))


"""Get Master Instruments Request"""
exchangesegments = [xt.EXCHANGE_NSEFO]
response = xt.get_master(exchangeSegmentList=exchangesegments)
print("Master: " + str(response))

"""Get Config Request"""
response = xt.get_config()
print('Config :', response)