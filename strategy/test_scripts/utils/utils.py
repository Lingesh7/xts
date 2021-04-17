# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 14:21:49 2021
General UTILITIES USED FOR ALGO
@author: WELCOME
"""
import time
from functools import partial, wraps
import logging
from sys import exit
import json
import configparser
from XTConnect.Connect import XTSConnect
from datetime import datetime,date
from pathlib import Path
import pandas as pd
from random import randint
import os
from openpyxl import load_workbook




# this is referring the main script logger
logger = logging.getLogger('__main__')


############## XTS Initialisation ##############
def xts_init(interactive=None, market=None):
    '''
    This will initialize the XTCONNECT class 
    only if the access token available in path
    Returns
    -------
    xt

    '''
    if interactive == True:
        key_int = 'interactive_appkey'
        key_sec = 'interactive_secretkey'
    elif market == True:
        key_int = 'marketdata_appkey'
        key_sec = 'marketdata_secretkey'
    try:    
        cfg = configparser.ConfigParser()
        cfg.read('../../XTConnect/config.ini')
        source = cfg['user']['source']
        appKey = cfg.get('user', key_int)
        secretKey = cfg.get('user', key_sec)
        xt = XTSConnect(appKey, secretKey, source)
        
        # global cdate
        cdate = datetime.strftime(datetime.now(), "%d-%m-%Y")
        token_file=f'../scripts/access_token_{cdate}.txt'
        file = Path(token_file)
        if file.exists() and (date.today() == date.fromtimestamp(file.stat().st_mtime)):
            logger.info('Token file exists and created today')
            in_file = open(token_file,'r').read().split()
            access_token = in_file[0]
            userID = in_file[1]
            #isInvestorClient=in_file[2]
            logger.info('UTILS: Initializing session with token..')
            xt._set_common_variables(access_token, userID)
        else:
            logger.error('UTILS: Wrong with token file. Generate separately..!..')
            # exit()
    except Exception:
        logger.info('UTILS:  Error in creating XT initialization')


def retry(func=None, exception=Exception, n_tries=5, delay=5, backoff=1, tolog=True, kill=False):
    # logger.info('Retry function from another file')
    """Retry decorator with exponential backoff.

    Parameters
    ----------
    func : typing.Callable, optional
        Callable on which the decorator is applied, by default None
    exception : Exception or tuple of Exceptions, optional
        Exception(s) that invoke retry, by default Exception
    n_tries : int, optional
        Number of tries before giving up, by default 5
    delay : int, optional
        Initial delay between retries in seconds, by default 5
    backoff : int, optional
        Backoff multiplier e.g. value of 2 will double the delay, by default 1
    tolog : bool, optional
        Option to log or print, by default True
    kill : bool, optional
        Option to kill the execution of the sript, by default False

    Returns
    -------
    typing.Callable
        Decorated callable that calls itself when exception(s) occur.

    Examples
    --------
    >>> import random
    >>> @retry(exception=Exception, n_tries=4)
    ... def test_random(text):
    ...    x = random.random()
    ...    if x < 0.5:
    ...        raise Exception("Fail")
    ...    else:
    ...        print("Success: ", text)
    >>> test_random("It works!")
    """

    if func is None:
        return partial(retry, exception=exception,
                       n_tries=n_tries, delay=delay,
                       backoff=backoff, tolog=logger, kill=kill,)

    @wraps(func)
    def wrapper(*args, **kwargs):
        ntries, ndelay, nkill = n_tries, delay, kill

        while ntries >= 1:
            try:
                return func(*args, **kwargs)
            except exception as e:
                msg = f"UTILS: Exception in {func.__name__} ==> {str(e)}, Retrying in {ndelay} seconds..."
                if tolog:
                    logger.warning(msg)
                else:
                    print(msg)
                time.sleep(ndelay)
                ntries -= 1
                ndelay *= backoff
                if nkill and ntries == 0:
                    logger.info(f'UTILS: {func.__name__} ==> failed all the retires.. Exiting.')
                    exit()

        return func(*args, **kwargs)

    return wrapper


@retry(n_tries=10, delay=15, kill=True)
def masterEqDump():
    # global instrument_df
    cdate = datetime.strftime(datetime.now(), "%d-%m-%Y")
    filename=f'../ohlc/NSE_EQ_Instruments_{cdate}.csv'
    file = Path(filename)
    if file.exists() and (date.today() == date.fromtimestamp(file.stat().st_mtime)):
        logger.info('UTILS: MasterDump already exists.. reading directly')
        instrument_df = pd.read_csv(filename,header='infer')
    else:
        logger.info('UTILS: Creating MasterDump..')
        xt = xts_init(market=True)
        exchangesegments = [xt.EXCHANGE_NSECM]
        mastr_resp = xt.get_master(exchangeSegmentList=exchangesegments)
        # print("Master: " + str(mastr_resp))
        master = mastr_resp['result']
        spl=master.split('\n')
        mstr_df = pd.DataFrame([sub.split("|") for sub in spl],columns=(['ExchangeSegment','ExchangeInstrumentID','InstrumentType','Name','Description','Series','NameWithSeries','InstrumentID','PriceBand.High','PriceBand.Low','FreezeQty','TickSize',' LotSize']))
        instrument_df = mstr_df[mstr_df.Series == 'EQ']
        instrument_df.to_csv(f"../ohlc/NSE_EQ_Instruments_{cdate}.csv",index=False)
    return instrument_df


def instrumentLookup(ticker,instrument_df=None):
    """Looks up instrument token for a given script from instrument dump"""
    instrument_df = masterEqDump()
    try:
        return int(instrument_df[instrument_df.Name==ticker].ExchangeInstrumentID.values[0])     
    except:
        return -1

    
def ltp(symbol=None,ltp=None):
    if symbol != None:
        id1 = symbol if str(symbol).isdigit() else instrumentLookup(symbol)
        if id1 != -1:
            instruments=[]
            instruments.append({'exchangeSegment': 1, 'exchangeInstrumentID': id1})
            xt = xts_init(market=True)
            quote_resp = xt.get_quote(Instruments=instruments,xtsMessageCode=1501,
                publishFormat='JSON')
            ltp = json.loads(quote_resp['result']['listQuotes'][0])['LastTradedPrice']
    else:
        logger.info('UTILS: pass valid symbol or id')
    return ltp


def dataToExcel(pnl_dump,startTime,df,gdf):
    time.sleep(randint(3,9))
    filename = os.path.basename(__file__).split('.')[0]
    cdate = datetime.strftime(datetime.now(), "%d-%m-%Y")
    sheetname = cdate+'_'+startTime.replace(':','_')
    pnl_df = pd.DataFrame(pnl_dump,columns=['date','pl'])
    pnl_df = pnl_df.set_index(['date'])
    pnl_df.index = pd.to_datetime(pnl_df.index, format='%d-%m-%Y %H:%M:%S')
    resampled_df = pnl_df['pl'].resample('1min').ohlc()
    #writing the output to excel sheet
    writer = pd.ExcelWriter(f'..\\pnl\\{filename}.xlsx',engine='openpyxl')
    writer.book = load_workbook(f'..\\pnl\\{filename}.xlsx')
    resampled_df.to_excel(writer, sheet_name=(sheetname), index=True)
    df.to_excel(writer, sheet_name=(sheetname),startrow=11, startcol=6, index=False)
    gdf.to_excel(writer, sheet_name=(sheetname),startrow=4, startcol=6, index=False)
    writer.sheets=dict((ws.title, ws) for ws in writer.book.worksheets)
    worksheet = writer.sheets[cdate]
    worksheet['G1'] = f"{filename} - {sheetname}"
    worksheet['G2'] = "MaxPnL"
    worksheet["G3"] = "=MAX(E:E)"
    worksheet['H2'] = "MinPnL"
    worksheet["H3"] = "=MIN(E:E)"
    worksheet['I2'] = "FinalPnL"
    worksheet['I3'] = gl_pnl
    writer.save()
    writer.close()