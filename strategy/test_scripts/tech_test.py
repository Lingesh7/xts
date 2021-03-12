# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 11:41:46 2021

@author: Welcome
"""

from datetime import datetime,date
from dateutil.relativedelta import relativedelta, TH, WE
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
import argparse
import timer
from threading import Thread
from openpyxl import load_workbook
from logging.handlers import TimedRotatingFileHandler
from sys import exit
import os
import numpy as np

try:
    os.chdir(r'D:\Python\First_Choice_Git\xts\strategy\scripts')
except:
    pass

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

filename='../logs/techTest_log.txt'

#file_handler = logging.FileHandler(filename)
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
    exit()


# xt.get_balance()

# instruments = [{'exchangeSegment': 1, 'exchangeInstrumentID': 2885}]
# quote_resp = xt.get_quote(
#     Instruments=instruments,
#     xtsMessageCode=1502,
#     publishFormat='JSON')
# print('Quote :', quote_resp)


# subs_resp=xt.send_subscription(Instruments=instruments,xtsMessageCode=1502)
# print('Quote :', subs_resp)


nowtime= datetime.now().strftime('%H%M%S')

ohlc=xt.get_ohlc(exchangeSegment=xt.EXCHANGE_NSECM,
                    exchangeInstrumentID=1333,
                    startTime='Mar 12 2021 091500',
                    endTime=f'Mar 12 2021 {nowtime}',
                    compressionValue=300)

dataresp= ohlc['result']['dataReponse']
spl = dataresp.split(',')
spl_df = pd.DataFrame([sub.split("|") for sub in spl],columns=(['Timestamp','Open','High','Low','Close','Volume','OI','NA']))
spl_df.drop(spl_df.columns[[-1,-2]], axis=1, inplace=True)

spl_df = spl_df.astype(dtype={'Open': float, 'High': float, 'Low': float, 'Close': float, 'Volume': int})
spl_df['Timestamp'] = pd.to_datetime(spl_df['Timestamp'].astype('int'), unit='s')
df = spl_df.copy()
df['vwap'] = (df.Volume*(df.High+df.Low+df.Close)/3).cumsum() / df.Volume.cumsum()
df['uB'] = df.vwap * 1.002
df['lB'] = df.vwap * 0.998

flop=[]
for i in range(len(df)):
    if df['Close'].values[i] >= df['uB'].values[i]:
        print('Long', df['Timestamp'].values[i])
        flop.append('Long')
    if df['Close'].values[i] <= df['lB'].values[i]:
        print('Short', df['Timestamp'].values[i])
        flop.append('Short')



vWAP = df['vwap'].iloc[-1]
uB = vWAP * 1.002
lB = vWAP * 0.998

# df.to_excel('hdfs_12Mar2021.xlsx')

if df['Close'].iloc[-2] <= uB:
    pass

if df['Close'].iloc[-2] <= lB:
    pass












