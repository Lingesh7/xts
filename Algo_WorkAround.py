Install Python 3.8 Win AMD 64 Exe file
echo %PATH% variable - check python added --;C:\Users\SYUS2\AppData\Local\Programs\Python\Python38\

Install pip
>python -m pip install pypiwin32

pip install alice_blue


import logging
logging.basicConfig(level=logging.DEBUG)

from alice_blue import *

access_token = AliceBlue.login_and_get_access_token(username='username', password='password', twoFA='a',  api_secret='api_secret')

TC744 - Welcom@123

cd C:\Users\SYUS2\AppData\Local\Programs\Python\Python38


---------------------------------------------------------
install requests, six

place a folder xts contains a file -- initfile and another folder named XTConnect

from XTConnect.Connect import XTSConnect
API_KEY = "ebaa4a8cf2de358e53c942"
API_SECRET = "Ojre664@S9"
XTS_API_BASE_URL = "https://xts-api.trading"
source = "WEBAPI"
xt = XTSConnect(API_KEY, API_SECRET, source)
response = xt.interactive_login()
print("Login: ", response)

"""Order book Request"""
response = xt.get_order_book()
print("Order Book: ", response)

---------------------------------------------------------
Dear RAJA1310,

You have successfully create a new application with IIFL dashboard APIs. With package Interactive Order API this package will valid till 30 Sep 2020.

Application Name :	IIFLXTS
App Key :	2f899dc8ef15881e844463
App Secret :	Ykyi834#tr


---------------------------------------------------------

Please find below test environment details:

Broker Name: SYMPHONY

User ID : IIFL24
Password: Xts@123456

MarketData Key :1f69e651e541597cedd513
MarketData: secretKey: Dqkv635$Y3

Trading Key: ebaa4a8cf2de358e53c942
Trading secretKey: Ojre664@S9


Following are the urls to connect to the API server :
 
https://developers.symphonyfintech.in/interactive
https://developers.symphonyfintech.in/marketdata  
 
Interactive API Document :
https://developers.symphonyfintech.in/doc/interactive/  

 

MarketData API Document :
https://developers.symphonyfintech.in/doc/marketdata/  
 
Git Hub link :
ttps://github.com/symphonyfintech


Regards, 
. 
Keval Shah
Product Manager | Algo Desk
IP - 536405 | 022 61086405 | +91 8879610532


API_KEY = "1f69e651e541597cedd513"
API_SECRET = "Dqkv635$Y3"
XTS_API_BASE_URL = "https://developers.symphonyfintech.in"
source = "WEBAPI"

https://medium.com/datadriveninvestor/python-utility-to-derive-nifty-support-and-resistance-zone-based-on-live-weekly-monthly-option-1b02bd3b31dd

https://www.capitalzone.in/python-code-to-read-data-scrapping-strike-price-expiry-date-from-nse-option-chain/
https://blog.quantinsti.com/stock-market-data-analysis-python/#futures

https://www.datacamp.com/community/tutorials/finance-python-trading
https://nsetools.readthedocs.io/en/latest/usage.html#getting-a-stock-quote  





14100 --- 10:30 == > +40pts ce square off - sell ce next strike

 					 -40pts pe square off - sell pe next strike


IIFL28 // login - May@123 // tranx - May@1234
#Live Account -- 

iiflxts
53051399e954a1b599d112
Tuum275@DB




Thank you VERY much! Adding future.result() it seems to work just like expected: goes ok if the code is correct, prints the error if there's something wrong... Anyway I think it would be important to report this strange behaviour to users which are/will be in the same situation as me – Alessio Martorana Feb 20 '19 at 10:15
future = executor.submit(f, vars) followed by print(f'{future.result()}') worked for me as well. My thanks to both of you for this solution!

logging-vs-performance:
https://stackoverflow.com/questions/33715344/python-logging-vs-performance

Get-Content .\A1_Strategy_1_log.txt  -Wait -Tail 10

import glob

for file in glob.glob('D:/Python/fc-page*.json'):
    data=json.load(open(file))
    df=pd.DataFrame(data['data'])
    print(df[['id','sum_of_pnl']])


dfs=[]
for line in open('D:/Python/fc-page1.json', 'r'):
    data=json.loads(line)
    df=pd.DataFrame(data['data'])
    dfs.append(df[['id','sum_of_pnl']])
final_df = pd.concat(dfs)
final_df.to_excel(r'C:/Users/Welcome/Desktop/pnl_data.xlsx')

---------------------------------
'open an excel and write to separate sheets'
import pandas as pd

df = pd.read_excel("input.xlsx")

with pd.ExcelWriter("output.xlsx") as writer:
    for name, group in df.groupby("column_name"):
        group.to_excel(writer, index=False, sheet_name=name[:31])

--------------------------------

Broker Name: SYMPHONY
User ID: IIFL28
Password: Apr@123  - tr Apr@1234
MarketData Key:98a27a5e1b81a59a7df220
MarketData: secretKey: Naip137#fo
Trading Key: 8a2c9c2c650b2334c0e432
Trading :secretKey: Yuis804$IK

=============
@ECHO OFF 
TITLE Execute python script on anaconda environment
ECHO Please Wait...
:: Section 1: Activate the environment.
ECHO ============================
ECHO Conda Activate
ECHO ============================
@CALL "C:\Users\Welcome\Anaconda3\Scripts\activate.bat" base
:: Section 2: Execute python script.
ECHO ============================
ECHO Python test.py
ECHO ============================
python D:\Python\First_Choice_Git\xts\strategy\scripts\NFOPanther_Live.py

ECHO ============================
ECHO End
ECHO ============================

PAUSE
==================

git  to include new files/folders added to gitignore 'git rm --cached -r strategy'



https://ttblaze.iifl.com/dashboard#!/app
interactive:
53051399e954a1b599d112
Tuum275@DB

market:
5e231aa3ba41dc751be459


kite.historical_data(instrument_token=54743047,from_date='2017-01-01', to_date='2019-01-01', interval="day",continuous=1)
