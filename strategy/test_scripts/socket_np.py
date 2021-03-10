import configparser
import json
import time
from threading import Thread
from XTConnect.MarketDataSocketClient import MDSocket_io
from XTConnect.InteractiveSocketClient import OrderSocket_io
from datetime import datetime,date
from pathlib import Path
from XTConnect.Connect import XTSConnect

global response
global new_file
global xt
global new_file

"""Get the configurations from config.ini file"""
cfg = configparser.ConfigParser()
cfg.read('../../XTConnect/config.ini')
appKey = cfg.get('user', 'marketdata_appkey')
secretKey = cfg.get('user', 'marketdata_secretkey')
source = cfg['user']['source']

"""Make XTSConnect object by passing your interactive API appKey, secretKey and source"""
xt = XTSConnect(appKey, secretKey, source)
"""Using the xt object we created call the marketdata login Request"""

response = xt.marketdata_login()
print(response)
set_marketDataToken = response['result']['token']
set_muserID = response['result']['userID']
# print("Login: ", response)

# marketdata SOCKET STREAMING
soc = MDSocket_io(set_marketDataToken, set_muserID)
"""Connected to the socket"""

# Thread(target=connectsocket).start()

Instruments = [{'exchangeSegment': 1, 'exchangeInstrumentID': 22},
               {'exchangeSegment': 1, 'exchangeInstrumentID': 2885}]
res=xt.send_subscription(Instruments, 1501)
print("res: ", res)

def on_message1501_json_full(data):
        now = datetime.now()
        today=now.strftime("%H:%M:%S")
        print(today,' DATA :',data,'\n')
        new_file=open("newfile.txt",mode="a+",encoding="utf-8")
        new_file.write(today, data);
        
def on_disconnect(reason):
    print('\033[93m Market Data Socket disconnected!  \033[0m'+reason)
    new_file=open("disconnect.txt",mode="a+",encoding="utf-8")
    new_file.write('Market Data Socket disconnected!! \n');     

# soc = MDSocket_io(self.set_marketDataToken, self.set_muserID)
el = soc.get_emitter()
el.on('1501-json-full', on_message1501_json_full)
# el.on('disconnect', self.on_disconnect)
soc.connect()
# soc.disconnect()


