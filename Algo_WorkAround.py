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

Application Name :  IIFLXTS
App Key :   2f899dc8ef15881e844463
App Secret :    Ykyi834#tr


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


IIFL28 // login - Jun@123 // tranx - Jun@1234 updated on May 30
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


db = sqlite3.connect(f'../ohlc/BANKNIFTY_JUN_OHLC.db')
cur = db.cursor()
pd.read_sql("SELECT * FROM BANKNIFTY_JUNE WHERE date(Timestamp) = date('2021-06-08')" , db)
cur.execute("DELETE FROM BANKNIFTY_JUNE WHERE date(Timestamp) = date('2021-06-09');")
db.commit()


https://ttblaze.iifl.com/dashboard#!/app
interactive:
53051399e954a1b599d112
Tuum275@DB

market:
5e231aa3ba41dc751be459


kite.historical_data(instrument_token=54743047,from_date='2017-01-01', to_date='2019-01-01', interval="day",continuous=1)


pd.read_sql_query("SELECT * from ADANIPORTS  where date(Timestamp) = '2021-05-24'", db)


cur.execute("delete from ACC where date(Timestamp) = '2021-05-24'")


POSTGRESSQL:
-----------
PS D:\Python\PG\pgsql\bin> .\initdb.exe -D D:\Python\PG\pgsql\data -U postgres
The files belonging to this database system will be owned by user "lmahendran".
This user must also own the server process.

The database cluster will be initialized with locale "English_United States.1252".
The default database encoding has accordingly been set to "WIN1252".
The default text search configuration will be set to "english".

Data page checksums are disabled.

fixing permissions on existing directory D:/Python/PG/pgsql/data ... ok
creating subdirectories ... ok
selecting dynamic shared memory implementation ... windows
selecting default max_connections ... 100
selecting default shared_buffers ... 128MB
selecting default time zone ... Asia/Calcutta
creating configuration files ... ok
running bootstrap script ... ok
performing post-bootstrap initialization ... ok
syncing data to disk ... ok

initdb: warning: enabling "trust" authentication for local connections
You can change this by editing pg_hba.conf or using the option -A, or
--auth-local and --auth-host, the next time you run initdb.

Success. You can now start the database server using:

    D:/Python/PG/pgsql/bin/pg_ctl -D ^"D^:^\Python^\PG^\pgsql^\data^" -l logfile start

PS D:\Python\PG\pgsql\bin> D:/Python/PG/pgsql/bin/pg_ctl -D "D:\Python\PG\pgsql\data" -l logfile start
waiting for server to start.... done
server started\
==========================================
fcdb

user table -
    user_id, first_name, last_name, broker_id, mobile, mail, telegram_id, created
broker table -
    broker_id, broker_name

subscriber table -
    subscriber_id, strategy_id,

strategy table -
    strategy_id, strategy_name, strategy_params, min_multiple, capital_required, strategy_created, strategy_modified,
        deployment_date, deployment_type

deployed table -
     strategy_id, Instrument_name, quantity, price, underlying , option_type, exchange,
                        dateTime, ltp,




my values that i have -- {strategy_id, user_id, 'set': 2, 'txn_type': 'sell', 'strike': 14350,
                            'qty': 150, 'tr_qty': -150, 'expiry': '29Apr2021', 'optionType': 'PE',
                            'name': 'NIFTY21APR14350PE', 'symbol': 66585, 'orderID': 10036948,
                            'tradedPrice': None, 'dateTime': None}

positions_table - userid, counter = 10,
    strategy_id, Instrument, quantity, price, underlying, option_type, exchange entry_date,





in tradetron - when i give deployed/all/strategy_id this return
    date
    0----
        |___created_at  :   2021-02-26T03:52:38.000000Z
            created_by_id   :   12073                               --> user_id
            deployment_date :   2021-02-26T00:00:00.000000Z
            deployment_type :   LIVE OFFLINE
            id  :   1587191                                         --> users-strategy_id
            run_counter :   36
            status  :   Active
            display_run_counter_pnl :   true
            sum_of_pnl  :   4605.000750000008
            strategy_broker     {3}
                id  :   1580303
                exchange    :   NFO
                broker      {2}
                    id  :   8
                    name    :   AliceBlue
            strategy_template_id    :   389444
            subscriber_id   :   12073
            user        {2}
                id  :   12073
                name    :   FirstChoice Investments Consultant
            template        {10}
                id  :   389444
                name    :   NFO  Panther
                user        {2}
                    id  :   12073
                    name    :   FirstChoice Investments Consultant
                created_by_id   :   12073
                strategy_params :
                min_multiple    :   1
                country :   IN
                capital_required    :   900000
                variable_fee    :   10.00
                display_positions_to_non_subscribers    :   0
            user_notes  :   null
            calculated_positions        [4]                                                     --> this has all the entry exit details
            calculated_positions        [4]
                0       {17}
                    strategy_id :   1587191
                    Instrument  :   OPTIDX_NIFTY_29APR2021_PE_14350
                    quantity    :   0
                    price   :   170.8
                    underlying  :   NIFTY 50
                    option_type :   PE
                    exchange    :   NFO
                    entry_date  :   2021-04-23 09:35:05
                    ltp :   177
                    gamma   :   0.0009432833377726571
                    delta   :   -0.5101464365623238
                    iv  :   23.00703731827822
                    vega    :   7.328857634422564
                    theta   :   -14.051247986261508
                    pnl :   3101.2499999999973
                    exp :   0
                    entry_value :   -3101.25
            max_run_counter :   35
            has_zero_quantity   :   null
            blocked_term    :   null
            minimum_multiple    :   1
            deployed_display_type   :   1
            max_multiple    :   100
            exchange    :   NFO
            market_open :   null
            is_blur :   false
            globalPt    :   null
            filtered_run_counter        [35]
                0       {3}
                    strategy_id :   1587191
                    run_counter :   35
                    pnl :   4605.002975463867
            currency    :   ₹
            country :   IN
            all_pnl :   227621.2518721819

    1
    2
    3



position table:

id  :   164241198
strategy_id :   2059063
broker_id   :   167
order_id    :   906300211619170518.456
exchange    :   NFo
Instrument  :   OPTIDX_NIFTY_29APR2021_PE_14350
underlying  :   NIFTY 50
expiry  :   2021-04-29
instrument_type :   OPTIDX
strike  :   14350
option_type :   PE
txn_type    :   B
condition_type  :   Exit
condition_category  :   NORMAL
entry_date  :   2021-04-23 09:35:18
quantity    :   75
quantity_pending    :   0
quantity_limit  :   0
price   :   166.95
underlying_price    :   14337.6
atm_strike  :   14350
amount  :   12521.2
type_of_position    :   None
itm_otm :   ITM
condition_parent_id :   2430014
condition_id    :   2430021
leg_id  :   0
run_counter :   10
created :   2021-04-23 15:05:18
product :   MIS
deployment  :   LIVE AUTO
edit_price  :   true


orderbook sample from iifl api:

{'LoginID': 'IIFL28', 'ClientID': 'IIFL28', 'AppOrderID': 10028944, 'OrderReferenceID': '', 'GeneratedBy': 'TWSAPI', 'ExchangeOrderID': 'X_41846564', 'OrderCategoryType': 'NORMAL', 'ExchangeSegment': 'NSEFO', 'ExchangeInstrumentID': 66658, 'OrderSide': 'Sell', 'OrderType': 'Market', 'ProductType': 'MIS', 'TimeInForce': 'DAY', 'OrderPrice': 0, 'OrderQuantity': 75, 'OrderStopPrice': 0, 'OrderStatus': 'Filled', 'OrderAverageTradedPrice': '47.80', 'LeavesQuantity': 0, 'CumulativeQuantity': 75, 'OrderDisclosedQuantity': 0, 'OrderGeneratedDateTime': '2021-04-29T09:48:05.9745602', 'ExchangeTransactTime': '2021-04-29T09:48:06+05:30', 'LastUpdateDateTime': '2021-04-29T09:48:06.3075864', 'OrderExpiryDate': '1980-01-01T00:00:00', 'CancelRejectReason': '', 'OrderUniqueIdentifier': 'FC_MarketOrder', 'OrderLegStatus': 'SingleOrderLeg', 'IsSpread': False, 'MessageCode': 9004, 'MessageVersion': 4, 'TokenID': 0, 'ApplicationType': 0, 'SequenceNumber': 418486279571208}

id  :   21043001840271
subscriber_id :   1587191
strategy_position_id    :   21043001840271
order_id    :   719157991619771678.023
broker_id   :   8
broker_order_id :   null
exchange    :   NFO
instrument  :   OPTIDX_NIFTY_06MAY2021_PE_14800
quantity    :   225
price_old   :   null
price   :   227.95
trade_price :   0
executed_quantity   :   0
trade_price_old :   0.00
status  :   Initiated
Description :   null
tranch_id   :   1e2bdeaf-c0d4-477c-8f1e-c506ac4206f5
tranch_sequence :   1
run_state   :   1
cmd :   null

{strategy: 1587191,
deployment_type: LIVE OFFLINE,
broker_id_sb: 8,
user_id: 12073,
txn_type: B,
broker_binary: /tradetron/scripts/aliceblue,
exchange_symbol: OPTIDX_NIFTY_06MAY2021_PE_14800,
exchange_broker: NFO,
order_id: 719157991619771678.023,
quantity: 225.0,
order_type: MKT,
broker_id: 8,
exchange: NFO,
instrument: OPTIDX_NIFTY_06MAY2021_PE_14800,
underlying: NIFTY 50,
instrument_type: OPTIDX,
option_type: PE,
expiry: null,
strike: 14800.0,
condition_type: Universal Exit,
type_of_position: None,
condition_id: 3825799, condition_parent_id: 0,
price: 227.95, underlying_price: 14684.5, run_counter: 40, leg_id: 0, tranch_size: 100, tranch_wait_secs: 10, final_action: MARKET,
tick_size: 0.05, price_revision_attempts: 1, price_revision_timeout: 0, price_execution: Market Price, price_ticks_multiple: 1,
product: MIS, tranch: null, limit_price: 0, multiplier: 1, strategy_position: 21043001840271}







mydict =  {'user': 'Bot1', 'version': 0.11, 'items': 23, 'methods': 'standard',
           'time': 1536304833437, 'logs': 'no', 'status': 'completed'}

placeholders = ', '.join(['%s'] * len(mydict))
columns = ', '.join(mydict.keys())
sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % ('mytable', columns, placeholders)
cursor.execute(sql, mydict.values())

def database_retrieve(db_file, id):
    try:
        conn = sqlite3.connect(db_file)

        with conn:
            sql_command = "SELECT * FROM my_table WHERE id = "+id

            cur = conn.cursor()
            cur.execute(sql_command)
            result = cur.fetchall()

            return result

    except Exception as e:
        print(e)

db_file = 'testdb.db'
print(database_retrieve(db_file, 'subject1'))

-----------------------
mycursor.execute(
    "SELECT stop_id FROM stops WHERE stop_name=%s",
    [station],
)
stopid = mycursor.fetchone()


--------------------------------
--SQLS
--------------------------------
--------------------------------
SQLs
--------------------------------
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

----------------
CUSTOMER
----------------

DROP TABLE CUSTOMER;
CREATE TABLE "public".customer ( id smallserial NOT NULL ,
                                first_name varchar(100) ,
                                last_name varchar(100) ,
                                mobile bigint ,
                                mail varchar(50) ,
                                address varchar(200) ,
                                active boolean ,
                                telegram_id integer ,
                                created_at TIMESTAMP(0) DEFAULT current_timestamp ,
                                updated_at TIMESTAMP(0) DEFAULT current_timestamp ,
                                CONSTRAINT pk_customer_id PRIMARY KEY ( id ) );



CREATE TRIGGER set_timestamp
BEFORE UPDATE ON customer
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

CREATE SEQUENCE "public".customer_id_seq START WITH 10000 INCREMENT BY 1;
ALTER SEQUENCE customer_id_seq RESTART WITH 10000 INCREMENT BY 1;

INSERT INTO "public".customer ( id, first_name, last_name, mobile, mail) VALUES ( nextval('customer_id_seq'), 'Linges', 'M', 6382860148, 'nerus.q8@gmail.com' );
INSERT INTO "public".customer ( id, first_name, last_name, mobile, mail) VALUES ( nextval('customer_id_seq'),'Raja', 'YOGI', 9884411611, 'acumeraja@yahoo.co.in' );

select * from customer;
--delete from customer;

UPDATE public.customer SET address='Chennai' WHERE ID = '10000';
UPDATE public.customer SET address='Cbe' WHERE ID = '10001';


----------------
BROKER
----------------

CREATE  TABLE "public".broker (
    id                   integer  NOT NULL ,
    name                 varchar(100)  NOT NULL ,
    --customer_id          smallserial DEFAULT nextval('broker_customer_id_seq'::regclass) NOT NULL ,
    CONSTRAINT pk_broker_id PRIMARY KEY ( id )
 );

ALTER TABLE "public".broker ADD CONSTRAINT fk_broker_customer FOREIGN KEY ( customer_id ) REFERENCES "public".customer( id );

INSERT INTO "public".broker ( id, name, customer_id) VALUES (nextval('broker_id_seq'), 'IIFL', 10000);
INSERT INTO "public".broker ( id, name, customer_id) VALUES (nextval('broker_id_seq'), 'Alice Blue', 10001);

----------------
STRATEGY
----------------
DROP TABLE "public".strategy;
CREATE TABLE "public".strategy ( id integer NOT NULL ,
                                name varchar(100) NOT NULL ,
                                min_multiplier integer DEFAULT 1 NOT NULL ,
                                capital_required decimal(12,2) ,
                                price_per_month decimal(10,2) DEFAULT 0 NOT NULL ,
                                description text DEFAULT 'FirstChoice Strategy' ,
                                --strategy_params_id SERIAL,
                                created_at TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP ,
                                updated_at TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP ,
                                CONSTRAINT pk_strategy_id PRIMARY KEY ( id ) )


CREATE TRIGGER set_timestamp
BEFORE UPDATE ON strategy
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

INSERT INTO "public".strategy
    ( id, name, min_multiplier, capital_required, price_per_month, description) VALUES
    ( nextval('strategy_id_seq'), 'NFO Panther', 1, 700000, 1000, 'BUY 2 lots and SELL 1 lot at SL, Same cont for every 1 hour');


UPDATE public.strategy SET capital_required=500 WHERE ID = 500;


----------------
SUBSCRIBERS
----------------

CREATE  TABLE "public".SUBSCRIBERS (
    id                   serial  NOT NULL ,
    customer_id          smallserial  NOT NULL ,
    strategy_id          integer  NOT NULL ,
    broker_id            integer,
    run_counter          serial  NOT NULL ,
    is_active            char(1)  NOT NULL ,
    start_date           DATE ,
    end_date             DATE ,
    created_at           TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP  ,
    updated_at           TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP  ,
    CONSTRAINT pk_subscribers_id PRIMARY KEY ( id )
 );

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON subscribers
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

INSERT INTO "public".subscribers
    ( id, customer_id, strategy_id, is_active, start_date, end_date) VALUES
 (nextval('subscriber_id_seq'), 10000, 504, 'Y',  CURRENT_DATE ,CURRENT_DATE + INTERVAL '30 day' );


 -------------------
 --STRATEGY_PARAMS
 -------------------

 DROP TABLE strategy_params;
 CREATE TABLE "public".strategy_params (
    id serial NOT NULL ,
    name varchar(100) NOT NULL ,
    strategy_id integer,
    script_name varchar(100) ,
    start_time text[] ,
    repair_time time ,
    end_time time DEFAULT '15:05:00' ,
    target decimal(7,2) ,
    stop_loss decimal(7,2) ,
    created_at TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP ,
    updated_at TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP ,
    CONSTRAINT pk_strategy_params_id PRIMARY KEY ( id ) )

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON strategy_params
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();


INSERT INTO "public".strategy_params(  name, strategy_id, script_name, start_time, repair_time, target, stop_loss) VALUES
                                    ( 'nfo_params', 500, 'NFO_Panther_Live', '{"09:30:00","10:00:00"}', '14:40:00', 24000, -12000 );

select start_time[1] from strategy_params;
delete from strategy_params;
select * from strategy_params;


INSERT INTO "public".strategy_params
    (  name, strategy_id, script_name, start_time, repair_time, target, stop_loss) VALUES
    ( 'os_params', 501, 'NFO_Panther_Live', '{"09:45:00"}', '14:40:00', 3000, -1500 );
select start_time[1] from strategy_params;
delete from strategy_params;
select * from strategy_params;



SELECT distinct name, substring(string(datetime),1,10) FROM `algo-trading-311005.fcdb.nifty_options` LIMIT 100


------------
pd.read_sql_query("SELECT * from ADANIPORTS  where date(Timestamp) = '2021-05-24'", db)
cur.execute("delete from ACC where date(Timestamp) = '2021-05-24'")


https://github.com/ktandon91/straddle-trading/blob/master/stockmock_clone/helpers.py


dbfile='D:\\Python\\First_Choice_Git\\xts\\strategy\\ohlc\\Archive\\NIFTY_MARCH_OHLC.db'
sql_db = sqlite3.connect(dbfile)
sql_cur = sql_db.cursor()
sql_cur.execute("SELECT * FROM NIFTY_MARCH;")
rows=sql_cur.fetchall()
# pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';",sql_db)
df = pd.DataFrame(rows, columns=(['name','datetime', 'open', 'high', 'low', 'close', 'volume', 'oi']))df['Date'].astype('datetime64[ns]')



-----------------------------------

import re

idx = ['NIFTY2171715000CE', 
       'BANKNIFTY2160334300PE',
       'BANKNIFTY21JUL36000CE','BANKNIFTY21123134300PE','NIFTY21MAR14000PE','NIFTY21111719000CE','BANKNIFTY21120334300PE','NIFTY21MAR5900PE' ,]

# pattern1 = r'(NIFTY|BANKNIFTY)(\d{2})(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)(\d{5})(CE|PE)$'
# pattern2 = r'(NIFTY|BANKNIFTY)(\d{2})([0-9])([0-9]{2})(\d{5})(CE|PE)$'


# pattern1 = r'(?P<index>NIFaTY|BANKNaIFTY)(?P<year>\d{2})(?P<month>JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)(?P<strike>\d{5})(?P<otype>CE|PE)$'                            
# pattern2 = r'(?P<index>NaIFTY|BANaKNIFTY)(?P<year>\d{2})(?P<month>[0-9])(?P<date>[0-9]{2})(?P<strike>\d{5})(?P<otype>CE|PE)$'
pattern3= r'(?P<index>NIFTY|BANKNIFTY)(?P<year>\d{2})(?P<month>(0?[1-9]|1[0-2]))(?P<date>(0?[1-9]|[12]\d|30|31))(?P<strike>\d{5})(?P<otype>CE|PE)$'
pattern4 = r'(?P<index>NIFTY|BANKNIFTY)(?P<year>\d{2})(?P<month>JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)(?P<strike>\d{4,5})(?P<otype>CE|PE)$'

for i in range(len(idx)):
    if re.search(pattern3, idx[i]):
        mm = re.search(pattern3, idx[i])
        # print('3 ',idx[i], 'strike', mm.group('strike'))
        print('Weekly Expiry - ', 'date', mm.group('date'),'month', mm.group('month') , 'year', mm.group('year'), 'strike', mm.group('strike'))
    elif re.search(pattern4, idx[i]):
        mm = re.search(pattern4, idx[i])
        # print('4 ',idx[i], 'strike', re.search(pattern4, idx[i]).group('strike'))
        print('Monthly Expiry - ', 'month', mm.group('month') , 'year', mm.group('year'), 'strike', mm.group('strike'))
        
========================
fc db


# ---------------
# from helpers import OptionsDataFrameFromQuery, DBConnection

# DBConnection()
import re

idx = ['NIFTY2171715000CE', 
       'BANKNIFTY2160334300PE',
       'BANKNIFTY21JUL36000CE','BANKNIFTY21123134300PE','NIFTY21MAR14000PE','NIFTY21111719000CE','BANKNIFTY21120334300PE','NIFTY21MAR5900PE' ,]

# pattern1 = r'(NIFTY|BANKNIFTY)(\d{2})(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)(\d{5})(CE|PE)$'
# pattern2 = r'(NIFTY|BANKNIFTY)(\d{2})([0-9])([0-9]{2})(\d{5})(CE|PE)$'


# pattern1 = r'(?P<index>NIFTY|BANKNIFTY)(?P<year>\d{2})(?P<month>JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)(?P<strike>\d{5})(?P<otype>CE|PE)$'                            
# pattern2 = r'(?P<index>NIFTY|BANKNIFTY)(?P<year>\d{2})(?P<month>[0-9])(?P<date>[0-9]{2})(?P<strike>\d{5})(?P<otype>CE|PE)$'
pattern3= r'(?P<index>NIFTY|BANKNIFTY)(?P<year>\d{2})(?P<month>(0?[1-9]|1[0-2]))(?P<date>(0?[1-9]|[12]\d|30|31))(?P<strike>\d{5})(?P<otype>CE|PE)$'
pattern4 = r'(?P<index>NIFTY|BANKNIFTY)(?P<year>\d{2})(?P<month>JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)(?P<strike>\d{4,5})(?P<otype>CE|PE)$'

for i in range(len(idx)):
    if re.search(pattern3, idx[i]):
        mm = re.search(pattern3, idx[i])
        # print('3 ',idx[i], 'strike', mm.group('strike'))
        print('Weekly Expiry - ', 'date', mm.group('date'),'month', mm.group('month') , 'year', mm.group('year'), 'strike', mm.group('strike'))
    elif re.search(pattern4, idx[i]):
        mm = re.search(pattern4, idx[i])
        # print('4 ',idx[i], 'strike', re.search(pattern4, idx[i]).group('strike'))
        print('Monthly Expiry - ', 'month', mm.group('month') , 'year', mm.group('year'), 'strike', mm.group('strike'))
    # ee = re.search(pattern3, idx[i])
    # if ee: 
    #     print('1 ',idx[i], 'month', ee.group('month'))
    # elif re.search(pattern4, idx[i]):
    #     print('2 ',idx[i], 'month', (re.search(pattern4, idx[i])).group('month')) 
    # # elif re.search(pattern3, idx[i]):
    # #     print('3 ',idx[i], 'month', (re.search(pattern3, idx[i])).group('month'))
    # # elif re.search(pattern4, idx[i]):
    # #     print('4 ',idx[i], 'month', (re.search(pattern4, idx[i])).group('month'))
    else:
        print('Not Matched with any')


# ((\b\d{1,2}\D{0,3})?\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|
#                           Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)
#                           ?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\D?)
# (\d{1,2}(st|nd|rd|th)?)?((\s*[,.\-\/]\s*)\D?)?\s*((19[0-9]\d|20\d{2})|\d{2})*




====================================

#to load nifty, bankNifty and futures:
dbfile='D:\\Python\\First_Choice_Git\\xts\\strategy\\ohlc\\FUT_JUL_OHLC.db'
sql_db = sqlite3.connect(dbfile)
sql_cur = sql_db.cursor()
sql_cur.execute("SELECT * FROM FUT_JUL_2021;")
rows=sql_cur.fetchall()
# pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';",sql_db)
df = pd.DataFrame(rows, columns=(['name','datetime', 'open', 'high', 'low', 'close', 'volume', 'oi']))
df_columns = list(df)
table = 'nifty_futures'
columns = ",".join(df_columns)
values = "VALUES({})".format(",".join(["%s" for _ in df_columns]))
insert_stmt = "INSERT INTO {} ({}) {}".format(table,columns,values)

# NIFTY_MARCH
pg_conn = psycopg2.connect(database="fcdb", user="postgres", password="postgres", host="127.0.0.1", port="5432")
pg_cur = pg_conn.cursor()
psycopg2.extras.execute_batch(pg_cur, insert_stmt, df.values)
pg_conn.commit()
pg_cur.close()
pg_conn.close()
sql_cur.close()
sql_db.close()

#to  load equity
# dbfile='D:\\Python\\First_Choice_Git\\xts\\strategy\\ohlc\\EQ_JULY_OHLC.db'
# sql_db = sqlite3.connect(dbfile)
# sql_cur = sql_db.cursor()

# sql_cur.execute('SELECT name FROM sqlite_master  WHERE type IN ("table","view") AND name NOT LIKE "sqlite_%" ORDER BY 1')
# table_names = sql_cur.fetchall()
# tables = []
# ticker_dict = {}
# for i in range(len(table_names)):
#     tables.append(table_names[i][0])
# symbols = [ xt.eq_lookup(ticker) for ticker in tables ]
# for ticker,symbol in zip(tables,symbols):
#     ticker_dict[ticker] = symbol
# # ticker_dict['NIFTY_50']="NIFTY 50"
# # ticker_dict['NIFTY_BANK']="NIFTY BANK"
# pg_conn = psycopg2.connect(database="fcdb", user="postgres", password="postgres", host="127.0.0.1", port="5432")
# pg_cur = pg_conn.cursor()

# for ticker,symbol in ticker_dict.items():
#     sql_cur.execute(f"SELECT '{ticker}' as name,'{symbol}' as symbol,* FROM '{ticker}';")
#     rows=sql_cur.fetchall()
#     df = pd.DataFrame(rows, columns=(['name', 'symbol', 'datetime', 'open', 'high', 'low', 'close', 'volume']))
#     df_columns = list(df)
#     table = 'nifty_equity'
#     columns = ",".join(df_columns)
#     values = "VALUES({})".format(",".join(["%s" for _ in df_columns]))
#     insert_stmt = "INSERT INTO {} ({}) {}".format(table,columns,values)
#     psycopg2.extras.execute_batch(pg_cur, insert_stmt, df.values)

# # # NIFTY_MARCH
# pg_conn.commit()
# pg_cur.close()
# pg_conn.close()
# sql_cur.close()
# sql_db.close()

delete dups in sql db
---------------------
delete from banknifty_september
where rowid not in (select min(rowid)
                    from banknifty_september
                    group by timestamp,Name)

select count(1) from banknifty_september; 939851
select count(1) from (select distinct timestamp, name from banknifty_september) a;	706055

