# -*- coding: utf-8 -*-
"""
Spyder Editor
Script to get daily OHLC based on the strike price of Index at 09:20 AM everyday.
change the variable bankniftyAt920, excelsheet file name
"""
from datetime import datetime
import pandas as pd
from XTConnect import XTSConnect
# API_KEY = "ebaa4a8cf2de358e53c942"
# API_SECRET = "Ojre664@S9"
API_KEY = "1f69e651e541597cedd513"
API_SECRET = "Dqkv635$Y3"
XTS_API_BASE_URL = "https://xts-api.trading"
source = "WEBAPI"
xt = XTSConnect(API_KEY, API_SECRET, source)
response = xt.marketdata_login()
print("Login: ", response)

def strkPrcCalc(spot,base):
    strikePrice = base * round(spot/base)
    # logger.info(f'StrikePrice computed as : {strikePrice}')
    print(f'StrikePrice computed as : {strikePrice}')
    return strikePrice

cdate = datetime.strftime(datetime.now(), "%b %d %Y")
bankniftyAt920 = 35880.60
strikePrice = strkPrcCalc(bankniftyAt920, 100)

if __name__ == '__main__':
   with pd.ExcelWriter(f'..\ohlc\BANKNIFTY_{datetime.strftime(datetime.now(),"%d%b%Y")}.xlsx',engine='xlsxwriter') as writer:
        for i in range(strikePrice-500,strikePrice+600,100):
            print(i)
            for j in ['CE','PE']:
                print(j)
                resp=xt.get_option_symbol(
                exchangeSegment=2,
                series='OPTIDX',
                symbol='BANKNIFTY',
                expiryDate='11Feb2021',
                optionType=j,
                strikePrice=i)
                # alist.append([resp['result'][0]['ExchangeInstrumentID'],resp['result'][0]['DisplayName']])
                # print(resp)
                eid=resp['result'][0]['ExchangeInstrumentID']
                name=resp['result'][0]['Description']
                print(eid, name)
                ohlc = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=eid,
                startTime=cdate+' 091500',
                endTime=cdate+' 153000',
                compressionValue=60)
                # print("OHLC: " + str(ohlc))
                dataresp= ohlc['result']['dataReponse']
                spl = dataresp.split(',')
                spl_df = pd.DataFrame([sub.split("|") for sub in spl],columns=(['Timestamp','Open','High','Low','Close','Volume','OI','NA']))
                spl_df.drop(spl_df.columns[[-1,]], axis=1, inplace=True)
                spl_df['Timestamp'] = pd.to_datetime(spl_df['Timestamp'].astype('int'), unit='s')
                spl_df.head()
                # writer = pd.ExcelWriter(r'..\logs\ohlc1.xls',engine='xlsxwriter')
                spl_df.to_excel(writer, sheet_name=(name+'_'+j), index=False,)
        print('==========================================')

    
