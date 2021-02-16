# -*- coding: utf-8 -*-
"""
Spyder Editor
Script to get daily OHLC   on EQ stocks
"""

from datetime import datetime,date
import pandas as pd
from XTConnect import XTSConnect
import configparser
from pathlib import Path

cfg = configparser.ConfigParser()
cfg.read('../../XTConnect/config.ini')

source = cfg['user']['source']
appKey = cfg.get('user', 'marketdata_appkey')
secretKey = cfg.get('user', 'marketdata_secretkey')

xt = XTSConnect(appKey, secretKey, source)

file = Path('access_token.txt')
if file.exists() and (date.today() == date.fromtimestamp(file.stat().st_mtime)):
    print('Token file exists and created today')
    in_file = open('access_token.txt','r').read().split()
    access_token = in_file[0]
    userID=in_file[1]
    # isInvestorClient=in_file[2]
    print('Initializing session with token..')
    xt._set_common_variables(access_token, userID)
else:
    print('Creating token file')   
    response = xt.marketdata_login()
    print(response)
    if "token" in response['result']:
        with open ('access_token.txt','w') as file:
            file.write('{}\n{}\n'.format(response['result']['token'], response['result']['userID']
                                           )) 


cdate = datetime.strftime(datetime.now(), "%b %d %Y")

watch = {"NSECM":{"ACC":22,"ADANIENT":25,"ADANIPORTS":15083,"ADANIPOWER":17388,"AMARAJABAT":100,"AMBUJACEM":1270,"APOLLOHOSP":157,"APOLLOTYRE":163,"ASHOKLEY":212,"ASIANPAINT":236,"AUROPHARMA":275,"AXISBANK":5900,"BAJAJ-AUTO":16669,"BAJAJFINSV":16675,"BAJFINANCE":317,"BALKRISIND":335,"BANDHANBNK":2263,"BANKBARODA":4668,"BATAINDIA":371,"BEL":383,"BHARTIARTL":10604,"BHEL":438,"BIOCON":11373,"BOSCHLTD":2181,"BPCL":526,"BRITANNIA":547,"CADILAHC":7929,"CANBK":10794,"CENTURYTEX":625,"CHOLAFIN":685,"CIPLA":694,"COALINDIA":20374,"COLPAL":15141,"CONCOR":4749,"CUMMINSIND":1901,"DABUR":772,"DIVISLAB":10940,"DLF":14732,"DRREDDY":881,"EICHERMOT":910,"EQUITAS":16852,"ESCORTS":958,"EXIDEIND":676,"FEDERALBNK":1023,"GAIL":4717,"GLENMARK":7406,"GMRINFRA":13528,"GODREJCP":10099,"GODREJPROP":17875,"GRASIM":1232,"HAVELLS":9819,"HCLTECH":7229,"HDFC":1330,"HDFCBANK":1333,"HDFCLIFE":467,"HEROMOTOCO":1348,"HINDALCO":1363,"HINDPETRO":1406,"HINDUNILVR":1394,"IBULHSGFIN":30125,"ICICIBANK":4963,"ICICIPRULI":18652,"IDEA":14366,"IDFCFIRSTB":11184,"IGL":11262,"INDIGO":11195,"INDUSINDBK":5258,"INFRATEL":29135,"INFY":1594,"IOC":1624,"ITC":1660,"JINDALSTEL":6733,"JSWSTEEL":11723,"JUBLFOOD":18096,"JUSTDIAL":29962,"KOTAKBANK":1922,"L&TFH":24948,"LICHSGFIN":1997,"LT":11483,"LUPIN":10440,"M&M":2031,"M&MFIN":13285,"MANAPPURAM":19061,"MARICO":4067,"MARUTI":10999,"MCDOWELL-N":10447,"MFSL":2142,"MGL":17534,"MINDTREE":14356,"MOTHERSUMI":4204,"MRF":2277,"MUTHOOTFIN":23650,"NATIONALUM":6364,"NAUKRI":13751,"NCC":2319,"NESTLEIND":17963,"NIITTECH":11543,"NMDC":15332,"NTPC":11630,"ONGC":2475,"PAGEIND":14413,"PEL":2412,"PETRONET":11351,"PFC":14299,"PIDILITIND":2664,"PNB":10666,"POWERGRID":14977,"PVR":13147,"RAMCOCEM":2043,"RBLBANK":18391,"RECLTD":15355,"RELIANCE":2885,"SAIL":2963,"SBIN":3045,"SHREECEM":3103,"SIEMENS":3150,"SRF":3273,"SRTRANSFIN":4306,"SUNPHARMA":3351,"SUNTV":13404,"TATACHEM":3405,"TATACONSUM":3432,"TATAMOTORS":3456,"TATAPOWER":3426,"TATASTEEL":3499,"TCS":11536,"TECHM":13538,"TITAN":3506,"TORNTPHARM":3518,"TORNTPOWER":13786,"TVSMOTOR":8479,"UBL":16713,"UJJIVAN":17069,"ULTRACEMCO":11532,"UPL":11287,"VEDL":3063,"VOLTAS":3718,"WIPRO":3787,"ZEEL":3812}}
tickers=['ASHOKLEY','AUROPHARMA','AXISBANK','BPCL','BAJFINANCE','DLF','DRREDDY','ESCORTS','IBULHSGFIN','ICICIBANK','INDUSINDBK','INFY','INDIGO','JINDALSTEL','LICHSGFIN','L&TFH','MARUTI','RELIANCE','RBLBANK','SBIN','TATAMOTORS','TATASTEEL','VEDL']
symbols = [ watch['NSECM'][ticker] for ticker in tickers ] 

tsym=zip(tickers,symbols)

if __name__ == '__main__':
    with pd.ExcelWriter(f'..\ohlc\EQ_{datetime.strftime(datetime.now(),"%d%b%Y")}.xlsx',engine='xlsxwriter') as writer:
        for ticker,symbol in tsym:
            print(ticker)
            ohlc = xt.get_ohlc(
                        exchangeSegment=xt.EXCHANGE_NSECM,
                        exchangeInstrumentID=symbol,
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
            spl_df.to_excel(writer, sheet_name=(ticker), index=False,)
        print('==========================================')
        # xt.marketdata_logout()

