# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 09:39:28 2021
login script to generate token in a file
@author: lmahendran
"""
from XTConnect.Connect import XTSConnect
from pathlib import Path
from datetime import date,datetime
import configparser
import os, shutil

try:
    os.chdir(r'D:\Python\First_Choice_Git\xts\strategy\scripts')
except:
    pass
cdate=datetime.now().strftime('%d-%m-%Y')

token_file=f'access_token_{cdate}.txt'
file = Path(token_file)
if file.exists() and (date.today() == date.fromtimestamp(file.stat().st_mtime)):
    print('Token file exists and created today')
else:
    cfg = configparser.ConfigParser()
    cfg.read('../../XTConnect/config.ini')

    source = cfg['user']['source']
    appKey = cfg.get('user', 'interactive_appkey')
    secretKey = cfg.get('user', 'interactive_secretkey')
    xt = XTSConnect(appKey, secretKey, source)
    print('Creating token file')   
    response = xt.interactive_login()
    print(response['description'])
    if "token" in response['result']:
        with open (token_file,'w') as file:
            file.write('{}\n{}\n{}\n'.format(response['result']['token'], response['result']['userID'],
                                           response['result']['isInvestorClient']))
    else:
        print('Issue with interactive login')

shutil.copy2(token_file, r'D:\Python\First_Choice_Git\xts\strategy\access_token')