"""
Created on Fri Mar 12 11:41:46 2021
Flop Strategey on EQ
@author: Welcome
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
import os

try:
    os.chdir(r'D:\Python\First_Choice_Git\xts\strategy\test_scripts')
except:
    pass

############## logging ##############
logger = logging.getLogger('__main__')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

filename='../logs/superSix_test_log.txt'

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
    
raw_df = pd.read_excel(
    r'D:\Python\First_Choice_Git\xts\strategy\test_scripts\INFY_01Mar2021.xlsx')

raw_df.drop(raw_df.columns[[-1]], axis=1, inplace=True)
raw_df = raw_df.astype(dtype={'Open': float, 'High': float, 'Low': float, 'Close': float, 'Volume': int})
raw_df['Timestamp'] = pd.to_datetime(raw_df['Timestamp'])
df = raw_df.copy()

startTime = datetime.strptime(('01-03-2021 09:20:01' ),"%d-%m-%Y %H:%M:%S")
# startTime = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
flop=[]
mark=[]


for i in range(len(df)):
    if pd.Timestamp(df['Timestamp'].values[i]) >= pd.Timestamp(startTime):
        print('Long', df['Timestamp'].values[i],df['Close'].values[i])
        
cur.execute("SELECT * from INFY where timestamp >= '2021-03-01' limit 5;").fetchall()


adf = pd.read_sql_query("SELECT * from INFY", db)
adf['Timestamp'] = pd.to_datetime(adf['Timestamp'])
# adf = adf.set_index(['Timestamp'])
# adf.loc['2021-3-3']

asdf = adf[(adf['Timestamp'] > '2021-3-25') & (adf['Timestamp'] <= '2021-3-26')]


