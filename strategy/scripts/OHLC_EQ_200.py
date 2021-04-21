# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 15:46:33 2021

@author: WELCOME
"""
from datetime import datetime
import pandas as pd
import sqlite3
import time
import os
# from XTConnect import XTSConnect
# import configparser
# from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
import logging

try:
    os.chdir(r'D:\Python\First_Choice_Git\xts\strategy\test_scripts')
except:
    pass

from utils.utils import xts_init, configure_logging


# this is referring the main script logger
log_name = os.path.basename(__file__).split('.')[0]
# print(log_name)
logger = configure_logging(log_name)

xt = xts_init(market=True)

if __name__ == '__main__':
    ins_df = xt.master_eq_dump()
    cdate1 = datetime.strftime(datetime.now(), "%b %d %Y")
    tickers = ['ACC', 'AUBANK', 'AARTIIND', 'ABBOTINDIA', 'ADANIENT', 
               'ADANIGREEN', 'ADANIPORTS', 'ATGL', 'ADANITRANS', 'ABCAPITAL',
               'ABFRL', 'AJANTPHARM', 'APLLTD', 'ALKEM', 'AMARAJABAT', 'AMBUJACEM',
               'APOLLOHOSP', 'APOLLOTYRE', 'ASHOKLEY', 'ASIANPAINT', 'AUROPHARMA',
               'DMART', 'AXISBANK', 'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV',
               'BAJAJHLDNG', 'BALKRISIND', 'BANDHANBNK', 'BANKBARODA', 'BANKINDIA',
               'BATAINDIA', 'BERGEPAINT', 'BEL', 'BHARATFORG', 'BHEL', 'BPCL', 
               'BHARTIARTL', 'BIOCON', 'BBTC', 'BOSCHLTD', 'BRITANNIA', 'CESC', 
               'CADILAHC', 'CANBK', 'CASTROLIND', 'CHOLAFIN', 'CIPLA', 'CUB', 
               'COALINDIA', 'COFORGE', 'COLPAL', 'CONCOR', 'COROMANDEL', 'CROMPTON', 
               'CUMMINSIND', 'DLF', 'DABUR', 'DALBHARAT', 'DEEPAKNTR', 'DHANI',
               'DIVISLAB', 'DIXON', 'LALPATHLAB', 'DRREDDY', 'EICHERMOT', 'EMAMILTD', 
               'ENDURANCE', 'ESCORTS', 'EXIDEIND', 'FEDERALBNK', 'FORTIS', 'GAIL', 
               'GMRINFRA', 'GLENMARK', 'GODREJAGRO', 'GODREJCP', 'GODREJIND', 'GODREJPROP',
               'GRASIM', 'GUJGASLTD', 'GSPL', 'HCLTECH', 'HDFCAMC', 'HDFCBANK', 'HDFCLIFE',
               'HAVELLS', 'HEROMOTOCO', 'HINDALCO', 'HAL', 'HINDPETRO', 'HINDUNILVR',
               'HINDZINC', 'HDFC', 'ICICIBANK', 'ICICIGI', 'ICICIPRULI', 'ISEC',
               'IDFCFIRSTB', 'ITC', 'IBULHSGFIN', 'INDIAMART', 'INDHOTEL', 'IOC',
               'IRCTC', 'IGL', 'INDUSTOWER', 'INDUSINDBK', 'NAUKRI', 'INFY', 'INDIGO',
               'IPCALAB', 'JSWENERGY', 'JSWSTEEL', 'JINDALSTEL', 'JUBLFOOD', 'KOTAKBANK', 
               'L&TFH', 'LTTS', 'LICHSGFIN', 'LTI', 'LT', 'LAURUSLABS', 'LUPIN', 'MRF',
               'MGL', 'M&MFIN', 'M&M', 'MANAPPURAM', 'MARICO', 'MARUTI', 'MFSL', 'MINDTREE',
               'MOTHERSUMI', 'MPHASIS', 'MUTHOOTFIN', 'NATCOPHARM', 'NMDC', 'NTPC',
               'NAVINFLUOR', 'NESTLEIND', 'NAM-INDIA', 'OBEROIRLTY', 'ONGC', 'OIL',
               'PIIND', 'PAGEIND', 'PETRONET', 'PFIZER', 'PIDILITIND', 'PEL', 'POLYCAB',
               'PFC', 'POWERGRID', 'PRESTIGE', 'PGHH', 'PNB', 'RBLBANK', 'RECLTD',
               'RELIANCE', 'SBICARD', 'SBILIFE', 'SRF', 'SANOFI', 'SHREECEM',
               'SRTRANSFIN', 'SIEMENS', 'SBIN', 'SAIL', 'SUNPHARMA', 'SUNTV',
               'SYNGENE', 'TVSMOTOR', 'TATACHEM', 'TCS', 'TATACONSUM', 'TATAELXSI', 
               'TATAMOTORS', 'TATAPOWER', 'TATASTEEL', 'TECHM', 'RAMCOCEM', 'TITAN',
               'TORNTPHARM', 'TORNTPOWER', 'TRENT', 'UPL', 'ULTRACEMCO', 'UNIONBANK',
               'UBL', 'MCDOWELL-N', 'VGUARD', 'VBL', 'VEDL', 'IDEA', 'VOLTAS',
               'WHIRLPOOL', 'WIPRO', 'YESBANK', 'ZEEL',]
    symbols = [ xt.eq_lookup(ticker, ins_df) for ticker in tickers ]
    ticker_dict = {}
    for ticker,symbol in zip(tickers,symbols):
        ticker_dict[ticker] = symbol
    
    ticker_dict['NIFTY_50']="NIFTY 50"
    ticker_dict['NIFTY_BANK']="NIFTY BANK"
    
    skipped = []
    logger.info(f'Connecting to DB ../ohlc/EQ_{datetime.now().strftime("%B").upper()}_OHLC.db')
    db = sqlite3.connect(f'../ohlc/EQ_{datetime.now().strftime("%B").upper()}_OHLC.db')
    cur = db.cursor()
    for ticker,symbol in ticker_dict.items():
        try:
            logger.info(f'Saving OHLC for - {ticker}')
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
            time.sleep(1)
        except ConnectionError:
            skipped.append({ticker:symbol})
            pass
        # pd.read_sql_query("SELECT * from JSWSTEEL", db)
    logger.warning(f'OHLC data import failed for : {skipped}')
    cur.close()
    db.close()
    logger.info('==================END========================')


