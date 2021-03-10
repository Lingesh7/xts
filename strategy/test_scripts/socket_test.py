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
class Example:

    def __init__(self):
        pass

    def ex(self):
        """Redirect the user to the login url obtained from xt.login_url(), and receive the token"""

        """Globally declaring and initializing the Interactive and MarketData XTConnection objects"""
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
        print (appKey+"  "+secretKey)
        """Using the xt object we created call the marketdata login Request"""
        response = xt.marketdata_login()
        print(response);
        self.set_marketDataToken = response['result']['token']
        self.set_muserID = response['result']['userID']
        print("Login: ", response)
        
        self.set_marketDataToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySUQiOiJJSUZMMjhfTUFSS0VUREFUQSIsInB1YmxpY0tleSI6Ijk4YTI3YTVlMWI4MWE1OWE3ZGYyMjAiLCJpYXQiOjE2MTUzNjY1ODgsImV4cCI6MTYxNTQ1Mjk4OH0.sAOocIYvQMCstircnSZI8FkH8Lk49jAly_wRNZcLqrg'
        self.set_muserID = 'IIFL28'

        # marketdata SOCKET STREAMING
        soc = MDSocket_io(self.set_marketDataToken, self.set_muserID)
        """Connected to the socket"""

        Thread(target=self.connectsocket).start()

        # marketdata logout
        # xt.marketdata_logout()

        # Instruments = [{'exchangeSegment': 51, 'exchangeInstrumentID': 217512}]
        Instruments = [{'exchangeSegment': 1, 'exchangeInstrumentID': 22},
                       {'exchangeSegment': 1, 'exchangeInstrumentID': 2885}]
        res=xt.send_subscription(Instruments, 1501)
        print(res)
      
        

    def on_message1501_json_full(self, data):
        now = datetime.now()
        today=now.strftime("%H:%M:%S")
        print(today,'in main 1501 Level1,Touchline message!' + data+' \n')
        new_file=open("newfile.txt",mode="a+",encoding="utf-8")
        new_file.write(today, data,'\n')
        
    def on_disconnect(self,reason):
        print('\033[93m Market Data Socket disconnected!  \033[0m'+reason)
        new_file=open("disconnect.txt",mode="a+",encoding="utf-8")
        new_file.write('Market Data Socket disconnected!! \n');     
 
    def connectsocket(self):
        soc = MDSocket_io(self.set_marketDataToken, self.set_muserID)
        el = soc.get_emitter()
        el.on('1501-json-full', self.on_message1501_json_full)
       # el.on('disconnect', self.on_disconnect)
        socketconnect = soc.connect()

    

    # END of Socket Streaming Section


if __name__ == "__main__":
    c1 = Example()
    c1.ex()

    URL = '/marketdata/auth/login'

    Exit = input("Press Enter to Exit")