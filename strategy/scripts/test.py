import os,time
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
from sys import exit
from logging.handlers import TimedRotatingFileHandler

parser = argparse.ArgumentParser(description='OptionScalper Script')
parser.add_argument('-t', '--ticker',type=str, required=True, help='NIFTY or BANKNIFTY')
args = parser.parse_args()
ticker = args.ticker
############## logging configs ##############
os.chdir(r'D:\Python\First_Choice_Git\xts\strategy\scripts')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

filename=f"../logs/test1_{ticker.replace(':','_')}_log.txt"

#file_handler = logging.FileHandler(filename)
file_handler=TimedRotatingFileHandler(filename, when='d', interval=1, backupCount=5)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


import requests

if __name__ == '__main__':
    a=0    
    while a < 100:
        response = a
        if response < 98:
            print(f'{ticker} Success!')
            logger.info(f'{ticker} Success!')
        elif response == 99:
            print(f' {ticker} Not Found.')
            logger.info(f' {ticker} Not Found.')
            print('{ticker} running in while loop')
            logger.info(f'{ticker} running in while loop')
        a += 1
        time.sleep(0.5)

