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
    list_ltp = []
    
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
        
        # self.set_marketDataToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySUQiOiJJSUZMMjhfTUFSS0VUREFUQSIsInB1YmxpY0tleSI6Ijk4YTI3YTVlMWI4MWE1OWE3ZGYyMjAiLCJpYXQiOjE2MTUzNjY1ODgsImV4cCI6MTYxNTQ1Mjk4OH0.sAOocIYvQMCstircnSZI8FkH8Lk49jAly_wRNZcLqrg'
        # self.set_muserID = 'IIFL28'

        # marketdata SOCKET STREAMING
        soc = MDSocket_io(self.set_marketDataToken, self.set_muserID)
        """Connected to the socket"""

        Thread(target=self.connectsocket).start()

        # marketdata logout
        # xt.marketdata_logout()

        # Instruments = [{'exchangeSegment': 51, 'exchangeInstrumentID': 217512}]
        Instruments = [{'exchangeSegment': 1, 'exchangeInstrumentID': 2885}]
        res = xt.send_subscription(Instruments, 1501)
        # res['result']
        # print("#Result: ", res)
        # list_ltp = res[listQuotes]['ltp']
        # quote_resp = xt.get_quote(Instruments=Instruments,xtsMessageCode=1501, publishFormat='JSON')
        # ltp = json.loads(quote_resp['result']['listQuotes'][0])['LastTradedPrice']
        
        
    def on_message1501_json_full(self, data):
        # global list_ltp
        # now = datetime.now()
        # today=now.strftime("%H:%M:%S")
        # print('Touchline message!' + data+' \n')
        ltp = json.loads(data)['Touchline']['LastTradedPrice']
        print('###################ltp is:',ltp)
        # self.list_ltp.append(ltp)
        # print(self.list_ltp) 
        
        new_file = open("ltp.txt",mode="a+",encoding="utf-8")
        new_file.write(str(ltp) + '\n') 
        
                
    def on_disconnect(self):
        print('\033[93m Market Data Socket disconnected!  \033[0m')
        # new_file=open("disconnect.txt",mode="a+",encoding="utf-8")
        # new_file.write('Market Data Socket disconnected!! \n');     
 
    def connectsocket(self):
        soc = MDSocket_io(self.set_marketDataToken, self.set_muserID)
        el = soc.get_emitter()
        el.on('1501-json-full', self.on_message1501_json_full)
        el.on('disconnect', self.on_disconnect)
        socketconnect = soc.connect()

    

    # END of Socket Streaming Section


if __name__ == "__main__":
    c1 = Example()
    c1.ex()

    # URL = '/marketdata/auth/login'

    Exit = input("Press Enter to Exit")
    