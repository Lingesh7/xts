# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 09:21:01 2021
login py
@author: lmahendran
"""

from XTConnect import XTSConnect
import configparser
        
cfg = configparser.ConfigParser()
cfg.read('../../XTConnect/config.ini')

source = cfg['user']['source']
appKey = cfg.get('user', 'interactive_appkey')
secretKey = cfg.get('user', 'interactive_secretkey')

xt = XTSConnect(appKey, secretKey, source)
response = xt.interactive_login()

# response = xt.marketdata_login()
 
with open ('access_token.txt','w') as file:
    file.write('{}\n{}\n{}\n'.format(response['result']['token'], response['result']['userID'],
                                           response['result']['isInvestorClient']))
    
