import os,time
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
from sys import exit

############## logging configs ##############
os.chdir(r'D:\Python\First_Choice_Git\xts\strategy\scripts')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

filename='../logs/test1_log.txt'

file_handler = logging.FileHandler(filename)
# file_handler=logging.handlers.TimedRotatingFileHandler(filename, when='d', interval=1, backupCount=5)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


import requests

if __name__ == '__main__':
    a=0    
    while a < 100:
        response = a
        if response < 98:
            print('Success!')
        elif response == 99:
            print('Not Found.')
            print('running in while loop')
        a += 1
        time.sleep(0.5)

