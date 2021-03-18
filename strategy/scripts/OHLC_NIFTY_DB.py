# -*- coding: utf-8 -*-
"""
Spyder Editor

"""
from datetime import datetime,date
import pandas as pd
from XTConnect import XTSConnect
import configparser
from pathlib import Path
import sqlite3
import nsetools
nse = nsetools.Nse()
import time

cfg = configparser.ConfigParser()
cfg.read('../../XTConnect/config.ini')

source = cfg['user']['source']
appKey = cfg.get('user', 'marketdata_appkey')
secretKey = cfg.get('user', 'marketdata_secretkey')

cdate = datetime.strftime(datetime.now(), "%d-%m-%Y")
xt = XTSConnect(appKey, secretKey, source)

token_file=f'access_token_market_{cdate}.txt'
file = Path(token_file)
if file.exists() and (date.today() == date.fromtimestamp(file.stat().st_mtime)):
    print('Token file exists and created today')
    in_file = open(token_file,'r').read().split()
    access_token = in_file[0]
    userID=in_file[1]
    # isInvestorClient=in_file[2]
    print('Initializing session with token..')
    xt._set_common_variables(access_token, userID)


def masterDump():
    global instrument_df
    filename=f'../ohlc/NSE_Instruments_{cdate}.csv'
    file = Path(filename)
    if file.exists() and (date.today() == date.fromtimestamp(file.stat().st_mtime)):
        print('MasterDump already exists.. reading directly')
        instrument_df=pd.read_csv(filename,header='infer')
    else:
        print('Creating MasterDump..')
        exchangesegments = [xt.EXCHANGE_NSEFO]
        mastr_resp = xt.get_master(exchangeSegmentList=exchangesegments)
        # print("Master: " + str(mastr_resp))
        master=mastr_resp['result']
        spl=master.split('\n')
        mstr_df = pd.DataFrame([sub.split("|") for sub in spl],columns=(['ExchangeSegment','ExchangeInstrumentID','InstrumentType','Name','Description','Series','NameWithSeries','InstrumentID','PriceBand.High','PriceBand.Low','FreezeQty','TickSize',' LotSize','UnderlyingInstrumentId','UnderlyingIndexName','ContractExpiration','StrikePrice','OptionType']))
        instrument_df = mstr_df[mstr_df.Series == 'OPTIDX']
        instrument_df.to_csv(f"../ohlc/NSE_Instruments_{cdate}.csv",index=False)        
            
def strkPrcCalc(spot,base):
    strikePrice = base * round(spot/base)
    # logger.info(f'StrikePrice computed as : {strikePrice}')
    print(f'StrikePrice computed as : {strikePrice}')
    return strikePrice

niftyjson = nse.get_index_quote('NIFTY 50')
nifty50 =  niftyjson['lastPrice']
strikePrice = strkPrcCalc(nifty50, 50)
strikeRange = [str(i) for i in list(range(strikePrice-1000,strikePrice+1000,50))]
# strikeRange = list(range(strikePrice-2000,strikePrice+2000,100))
# strikeRangestr = [str(i) for i in strikeRange]

#main       
masterDump()
cdate1 = datetime.strftime(datetime.now(), "%b %d %Y")
df = instrument_df.copy()
# symbol_list = (df[(df.Name == 'NIFTY') & (df.Description.str.contains(f'NIFTY21{datetime.now().strftime("%b").upper()}'))]['ExchangeInstrumentID']).tolist()
filtrdf = df[(df.Name == 'NIFTY') & (df.Description.str.contains(f'NIFTY21{datetime.now().strftime("%b").upper()}'))]
nwfiltrdf = filtrdf[filtrdf.Description.str.contains('|'.join(strikeRange))]
keyv = dict(zip(nwfiltrdf.Description, nwfiltrdf.ExchangeInstrumentID))
skipped = []
db = sqlite3.connect(f'../ohlc/NIFTY_{datetime.now().strftime("%B").upper()}_OHLC.db')
cur = db.cursor()
for name,symbol in keyv.items():
    try:
        print(name,symbol)
        ohlc = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_NSEFO,
                exchangeInstrumentID=symbol,
                startTime=cdate1+' 091500',
                endTime=cdate1+' 153000',
                compressionValue=60)
                # print("OHLC: " + str(ohlc))
        dataresp= ohlc['result']['dataReponse']
        if dataresp != '':
            spl = dataresp.split(',')
            datadf = pd.DataFrame([sub.split("|") for sub in spl],columns=(['Timestamp','Open','High','Low','Close','Volume','OI','NA']))
            datadf.drop(datadf.columns[[-1,]], axis=1, inplace=True)
            datadf['Timestamp'] = pd.to_datetime(datadf['Timestamp'].astype('int'), unit='s')
            datadf.insert(0, 'Name', name)
            datadf.to_sql((f'NIFTY_{datetime.now().strftime("%B").upper()}'),db,if_exists='append',index=False)
            # pd.read_sql_query("SELECT * from NIFTY_MARCH", db) 
            time.sleep(2)             
    except ConnectionError:
        skipped.append({name:symbol})
        pass
cur.close()
db.close()
print('==================END========================')