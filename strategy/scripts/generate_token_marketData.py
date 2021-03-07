# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 02:56:59 2021

@author: mling
"""

from XTConnect.Connect import XTSConnect
from pathlib import Path
from datetime import date,datetime
import configparser

cdate=datetime.now().strftime('%d-%m-%Y')

token_file=f'access_token_{cdate}.txt'
file = Path(token_file)
if file.exists() and (date.today() == date.fromtimestamp(file.stat().st_mtime)):
    print('Token file exists and created today')
else:
    cfg = configparser.ConfigParser()
    cfg.read('../../XTConnect/config.ini')

    source = cfg['user']['source']
    appKey = cfg.get('user', 'marketdata_appkey')
    secretKey = cfg.get('user', 'marketdata_secretkey')
    xt = XTSConnect(appKey, secretKey, source)
    print('Creating token file')   
    response = xt.marketdata_login()
    print(response['description'])
    if "token" in response['result']:
        with open (token_file,'w') as file:
            file.write('{}\n{}\n'.format(response['result']['token'], response['result']['userID']
                                           ))
    else:
        print('Issue with interactive login')