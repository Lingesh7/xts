# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 23:21:16 2020

@author: mling
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta, TH
from XTConnect.Connect import XTSConnect

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


def placeSLMOrder(symbol,):
    
     print(f'''oder_resp = xt.place_order(exchangeSegment=xt.EXCHANGE_NSEFO,
                   exchangeInstrumentID= {eID} ,
                   productType=xt.PRODUCT_MIS, 
                   orderType=xt.ORDER_TYPE_MARKET,                   
                   orderSide={t_type},
                   timeInForce=xt.VALIDITY_DAY,
                   disclosedQuantity=0,
                   orderQuantity={quantity},
                   # orderUniqueIdentifier="1test1"
                   )''')

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
    print(f'''oder_resp = xt.place_order(exchangeSegment=xt.EXCHANGE_NSEFO,
                   exchangeInstrumentID= {eID} ,
                   productType=xt.PRODUCT_MIS, 
                   orderType=xt.ORDER_TYPE_MARKET,                   
                   orderSide={t_type},
                   timeInForce=xt.VALIDITY_DAY,
                   disclosedQuantity=0,
                   orderQuantity={quantity},
                   # orderUniqueIdentifier="1test1"
                   )''')
    # print("Place Order: ", oder_resp)
    # return oder_resp

placeMarketOrder("NIFTY","SELL","ce",lThu,1)
placeMarketOrder("BANKNIFTY","SELL","pe",nThu,2)
# # extracting the order id from response
# if oder_resp['type'] != 'error':
#     OrderID = oder_resp['result']['AppOrderID']
        

from nsetools import Nse
nse = Nse()

nfty_ltp = nse.get_index_quote("nifty 50")['lastPrice']
bnknfty_ltp = nse.get_index_quote("nifty bank")['lastPrice']

def strkPrcCalc(ltp,base):    
    return base * round(ltp/base)

def get_eID(symbol,ce_pe,expiry):
    if ce_pe == "ce":
        oType="CE"
    elif ce_pe == "pe":
        oType="PE"
    if symbol == "NIFTY":
        strikePrice= strkPrcCalc(nfty_ltp,50)
    elif symbol == "BANKNIFTY":
        strikePrice= strkPrcCalc(bnknfty_ltp,100)
    response = xt.get_option_symbol(
    exchangeSegment=2,
    series='OPTIDX',
    symbol=symbol,
    expiryDate=expiry,
    optionType=oType,
    strikePrice=strikePrice)
    print('Option Symbol:', str(response))
    print((int(response["result"][0]["ExchangeInstrumentID"])))
    return int(response["result"][0]["ExchangeInstrumentID"])
    

def get_eID1(symbol,ce_pe,expiry):
    print(symbol , ce_pe , expiry)
    response = xt.get_option_symbol(
    exchangeSegment=2,
    series='OPTIDX',
    symbol=symbol,
    expiryDate=expiry,
    optionType=ce_pe,
    strikePrice=13500)
    #print('Option Symbol:', str(response))
    print((int(response["result"][0]["ExchangeInstrumentID"])))
    
response = xt.get_option_symbol(
    exchangeSegment=2,
    series='OPTIDX',
    symbol='BANKNIFTY',
    expiryDate='24Dec2020',
    optionType='CE',
    strikePrice=32500)
print('Option Symbol:', str(response))

get_eID("NIFTY","ce",nThu)
get_eID("BANKNIFTY","pe",lThu)


orderBook = {'type': 'success', 'code': 's-orders-0001', 'description': 'Success order book', 'result': [{'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10026335, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_30698353', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 39972, 'OrderSide': 'Buy', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '23.90', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-21T14:59:41.1535468', 'ExchangeTransactTime': '2020-12-21T14:59:42+05:30', 'LastUpdateDateTime': '2020-12-21T14:59:42.1276213', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': '123888','IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 307029544559178}, {'LoginID': 'IIFL24', 'ClientID': 'IIFL24', 'AppOrderID': 10026325, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_30698343', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 39972, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '31.80', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2020-12-21T14:49:16.0287269', 'ExchangeTransactTime': '2020-12-21T14:49:16+05:30', 'LastUpdateDateTime': '2020-12-21T14:49:16.350748', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': '123777', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 307029544559177}]}
orderId = 10026335
orderList = orderBook["result"]

for i in orderList:
    # print(i)
    print(i["AppOrderID"])
    if orderId == i["AppOrderID"] and i["OrderStatus"] == 'Filled':
        orderPrice = float(( i["OrderAverageTradedPrice"]))

type(orderPrice)





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



