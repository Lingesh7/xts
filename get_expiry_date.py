# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 22:05:03 2020

@author: mling
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta, TH


#symbol="NIFTY"
def get_expiry_from_option_chain (symbol):

    #url = "https://www1.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?symbolCode=-10003&symbol=NIFTY&symbol=NIFTY&instrument=OPTIDX&date=-&segmentLink=17&segmentLink=17"
    url="https://www1.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?symbol="+symbol+"&date=-"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                             'like Gecko) '
                             'Chrome/80.0.3987.149 Safari/537.36',
               'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}
    session = requests.Session()
    request = session.get(url, headers=headers, timeout=5)
    cookies = dict(request.cookies)
    page = session.get(url, headers=headers, timeout=5, cookies=cookies)

    soup = BeautifulSoup(page.content, 'html.parser')
    locate_expiry_point = soup.find(id="date")
    expiry_rows = locate_expiry_point.find_all('option')

    index = 0
    expiry_list = []
    for each_row in expiry_rows:
        # skip first row as it does not have value
        if index <= 0:
            index = index + 1
            continue
        index = index + 1
        # Remove HTML tag and save to list
        expiry_list.append(BeautifulSoup(str(each_row), 'html.parser').get_text())

    return expiry_list

#expdate="24DEC2020"
def get_strike_price_from_option_chain(symbol, expdate):
    url="https://www1.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?symbol="+symbol+"&date=-"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                             'like Gecko) '
                             'Chrome/80.0.3987.149 Safari/537.36',
               'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}
    session = requests.Session()
    request = session.get(url, headers=headers, timeout=5)
    cookies = dict(request.cookies)
    page = session.get(url, headers=headers, timeout=5, cookies=cookies)

    soup = BeautifulSoup(page.content, 'html.parser')

    table_cls_2 = soup.find(id="octable")
    req_row = table_cls_2.find_all('tr')
    strike_price_list = []

    for row_number, tr_nos in enumerate(req_row):
        # This ensures that we use only the rows with values
        if row_number <= 1 or row_number == len(req_row) - 1:
            continue
        td_columns = tr_nos.find_all('td')
        strike_price = int(float(BeautifulSoup(str(td_columns[11]), 'html.parser').get_text()))
        strike_price_list.append(strike_price)
        # print (strike_price_list)
    return strike_price_list



def nextThu_and_lastThu_expiry_date ():

    todayte = datetime.today()
    
    cmon = todayte.month
    if_month_next=(todayte + relativedelta(weekday=TH(1))).month
    next_thursday_expiry=todayte + relativedelta(weekday=TH(1))
   
    if (if_month_next!=cmon):
        month_last_thu_expiry= todayte + relativedelta(weekday=TH(5))
        if (month_last_thu_expiry.month!=if_month_next):
            month_last_thu_expiry= todayte + relativedelta(weekday=TH(4))
    else:
        for i in range(1, 7):
            t = todayte + relativedelta(weekday=TH(i))
            if t.month != cmon:
                # since t is exceeded we need last one  which we can get by subtracting -2 since it is already a Thursday.
                t = t + relativedelta(weekday=TH(-2))
                month_last_thu_expiry=t
                break
    str_month_last_thu_expiry=str(int(month_last_thu_expiry.strftime("%d")))+month_last_thu_expiry.strftime("%b").upper()+month_last_thu_expiry.strftime("%Y")
    str_next_thursday_expiry=str(int(next_thursday_expiry.strftime("%d")))+next_thursday_expiry.strftime("%b").upper()+next_thursday_expiry.strftime("%Y")
    return (str_next_thursday_expiry,str_month_last_thu_expiry)


get_expiry_from_option_chain("NIFTY")
get_strike_price_from_option_chain("NIFTY","24DEC2020")

str_next_thursday_expiry,str_month_last_thu_expiry=nextThu_and_lastThu_expiry_date()
print("Next Expiry Date = " + str_next_thursday_expiry)
print("Month End Expiry Date = " + str_month_last_thu_expiry)


