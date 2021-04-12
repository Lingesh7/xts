# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 08:15:18 2021

@author: lmahendran
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
from renko import renko
# from stocktrends import Renko
import os

try:
    os.chdir(r'D:\Python\First_Choice_Git\xts\strategy\test_scripts')
except:
    pass

############## logging ##############
logger = logging.getLogger('__main__')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

filename='../logs/renko_log.txt'

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
# tickers= ['AUROPHARMA', 'AXISBANK', 'BPCL', 
#           'BANDHANBNK', 'BAJFINANCE', 'DLF', 
#           'HINDALCO', 'IBULHSGFIN', 'INDUSINDBK', 
#           'ICICIBANK', 'INDIGO', 'JINDALSTEL', 
#           'L&TFH', 'LICHSGFIN', 'MANAPPURAM', 
#           'MARUTI', 'RBLBANK', 'SBIN', 
#           'TATAMOTORS', 'TATASTEEL', 'VEDL']
tickers=['NIFTY2141514850CE','NIFTY2141514850PE']
refid=1
side = None


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
def masterDump():
    global instrument_df
    filename=f'../ohlc/NSE_Instruments_{cdate}.csv'
    file = Path(filename)
    if file.exists() and (date.today() == date.fromtimestamp(file.stat().st_mtime)):
        logger.info('MasterDump already exists.. reading directly')
        instrument_df = pd.read_csv(filename,header='infer')
    else:
        logger.info('Creating MasterDump..')
        exchangesegments = [xt.EXCHANGE_NSEFO]
        mastr_resp = xt.get_master(exchangeSegmentList=exchangesegments)
        # print("Master: " + str(mastr_resp))
        master=mastr_resp['result']
        spl=master.split('\n')
        mstr_df = pd.DataFrame([sub.split("|") for sub in spl],columns=(['ExchangeSegment','ExchangeInstrumentID','InstrumentType','Name','Description','Series','NameWithSeries','InstrumentID','PriceBand.High','PriceBand.Low','FreezeQty','TickSize',' LotSize']))
        instrument_df = mstr_df[mstr_df.Series == 'EQ']
        instrument_df.to_csv(f"../ohlc/NSE_Instruments_{cdate}.csv",index=False)


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

def main():
    global side
    for ticker in tickers:
        data = fetchOHLC(ticker, 60)
        renko_obj_atr = renko()
        renko_obj_atr.set_brick_size(auto = False, brick_size = .50)
        renko_obj_atr.build_history(prices = data.close)
        renko_box = renko_obj_atr.get_renko_directions()
        print('Renko bar directions: ', renko_box)
        if len(renko_box) > 3:
            print('quali')
            box_three = renko_box[-3:]
            if len(set(box_three)) == 1:
                if renko_box[-1] == 1:
                    side = 'Long'
                    bot_sendtext(f'Renko - go Long in {ticker}')
                elif renko_box[-1] == -1:
                    side = 'Short'
     
        

if __name__ == '__main__':
    masterDump()
    logger.info('Waiting to start the script at 09:16 AM')
    while datetime.now() >= pd.Timestamp(cdate+" "+'09:16:01'):
        main()
    startin = time.time()
    timeout = time.time() + ((60*60*6) - 300) # 60 seconds times 360 meaning 6 hrs
    while time.time() <= timeout:
        try:
            main()
            time.sleep(60 - ((time.time() - startin) % 60.0))
        except KeyboardInterrupt:
            logger.exception('\n\nKeyboard exception received. Exiting.')
            exit()
        except:
            logger.exception('\n\nCritical main function error.. Exiting.')
            exit()
    
        