# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 19:48:49 2021

@author: mling
"""

from datetime import datetime,date
import pandas as pd
from XTConnect import XTSConnect
import configparser
from pathlib import Path
import sqlite3

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
    
def masterEqDump():
    global instrument_df
    filename=f'../ohlc/NSE_EQ_Instruments_{cdate}.csv'
    file = Path(filename)
    if file.exists() and (date.today() == date.fromtimestamp(file.stat().st_mtime)):
        print('MasterDump already exists.. reading directly')
        instrument_df=pd.read_csv(filename,header='infer')
    else:
        print('Creating MasterDump..')
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
        return instrument_df[instrument_df.Name==ticker].ExchangeInstrumentID.values[0]
    except:
        return -1
    
masterEqDump()
cdate1 = datetime.strftime(datetime.now(), "%b %d %Y")   
tickers = ['JSWSTEEL', 'TECHM', 'TATASTEEL', 'HINDALCO', 'INDUSINDBK', 'POWERGRID', 'EICHERMOT', 'HCLTECH', 'SBIN', 'NTPC', 'COALINDIA', 'TITAN', 'BPCL', 'BRITANNIA', 'NESTLEIND', 'SBILIFE', 'TATAMOTORS', 'WIPRO', 'HINDUNILVR', 'ITC', 'TCS', 'SHREECEM', 'GRASIM', 'UPL', 'INFY', 'MARUTI', 'IOC', 'BHARTIARTL', 'CIPLA', 'AXISBANK', 'ONGC', 'KOTAKBANK', 'HDFCLIFE', 'ULTRACEMCO', 'M&M', 'SUNPHARMA', 'HDFC', 'HDFCBANK', 'ICICIBANK', 'RELIANCE', 'ASIANPAINT', 'ADANIPORTS', 'DRREDDY', 'LT', 'BAJAJ-AUTO', 'HEROMOTOCO', 'BAJFINANCE', 'GAIL', 'BAJAJFINSV', 'DIVISLAB', 'ASHOKLEY','AUROPHARMA','DLF','DRREDDY','ESCORTS','IBULHSGFIN','INDIGO','JINDALSTEL','LICHSGFIN','L&TFH','RBLBANK','VEDL']
# tickers = ['JSWSTEEL']
symbols = [ instrumentLookup(instrument_df,ticker) for ticker in tickers ]

ticker_dict = {}
for ticker,symbol in zip(tickers,symbols):
    ticker_dict[ticker] = symbol

    
db = sqlite3.connect(f'../ohlc/EQ_{datetime.now().strftime("%B").upper()}_OHLC.db')
cur = db.cursor()
for ticker,symbol in ticker_dict.items():
    print(ticker)
    ohlc = xt.get_ohlc(
                exchangeSegment=xt.EXCHANGE_NSECM,
                exchangeInstrumentID=symbol,
                startTime=cdate1+' 091500',
                endTime=cdate1+' 153000',
                compressionValue=60)
    # print("OHLC: " + str(ohlc))
    dataresp= ohlc['result']['dataReponse']
    spl = dataresp.split(',')
    df = pd.DataFrame([sub.split("|") for sub in spl],columns=(['Timestamp','Open','High','Low','Close','Volume','OI','NA']))
    df.drop(df.columns[[-1,-2]], axis=1, inplace=True)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'].astype('int'), unit='s')
    df = df.astype(dtype={'Open': float, 'High': float, 'Low': float, 'Close': float, 'Volume': int})
    df.to_sql(ticker,db,if_exists='append',index=False)
    # pd.read_sql_query("SELECT * from JSWSTEEL", db)
cur.close()
db.close()
print('==================END========================')
    
    
    
    
    
    
    