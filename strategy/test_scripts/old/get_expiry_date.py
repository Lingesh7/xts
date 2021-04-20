# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 22:05:03 2020

@author: mling
"""

import requests
from bs4 import BeautifulSoup


symbol="NIFTY"
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
    # locate_expiry_point = soup.select('option[value]')
    # expiry_rows = locate_expiry_point.find_all('option')
    # items = soup.select('[id=expirySelect] option[value]')
    
    subject_options = [i.findAll('option') for i in soup.findAll('select')]

    
    its = soup.select('select > option')
    options = its.find_all('option')
    values = [item.get('value') for item in options]
    print(values)


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





import time
import sys
from datetime import datetime as dt

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select


options = Options()
options.add_argument("--disable-notifications")
options.add_argument("user-agent={'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, ''like Gecko) ''Chrome/80.0.3987.149 Safari/537.36'}")
PATH = "C:\\Users\\mling\\Downloads\\chromedriver.exe"
driver = webdriver.Chrome(PATH,chrome_options=options)
driver.maximize_window()
url='https://www1.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?symbol="NIFTY"&date=-'
driver.get(url)
wait_time = 60 # a very long wait time
wait(driver, wait_time).until(EC.element_to_be_clickable(By.XPATH("//*[@id='expirySelect']"))).click()




import requests
import time
import os
import pandas as pd
from datetime import datetime
import shutil
import json

url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
headers={'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
     'accept-language':'en-US,en;q=0.9,bn;q=0.8','accept-encoding':'gzip, deflate, br'}
r=requests.get(url,headers=headers).json()
expiry_dates = r["records"]["expiryDates"]
cmon_expiry_dates = [date for date in expiry_dates if "Apr" in date]
cmon_expiry_dates = [date for date in expiry_dates if f'datetime.now().strftime('%B')' in date]

def nextThu_and_lastThu_expiry_date ():
    global weekly_exp, monthly_exp
    print('Calculating weekly and monthly expiry dates..')
    
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
    monthly_exp=str((month_last_thu_expiry.strftime("%d")))+month_last_thu_expiry.strftime("%b").capitalize()+month_last_thu_expiry.strftime("%Y")
    weekly_exp=str((next_thursday_expiry.strftime("%d")))+next_thursday_expiry.strftime("%b").capitalize()+next_thursday_expiry.strftime("%Y")
    print(f'weekly expiry is : {weekly_exp}, monthly expiry is: {monthly_exp}')

def get_expiry():
    global weekly_exp, monthly_exp
    now = datetime.today()
    cmon = now.month
    thu = (now + relativedelta(weekday=TH(1))).strftime('%d%b%Y')
    wed = (now + relativedelta(weekday=WE(1))).strftime('%d%b%Y')
    nxtmon = (now + relativedelta(weekday=TH(1))).month
    if (nxtmon != cmon):
        month_last_thu_expiry = now + relativedelta(weekday=TH(5))
        if (month_last_thu_expiry.month!= nxtmon):
            mon_thu = now + relativedelta(weekday=TH(4))
            mon_wed = now + relativedelta(weekday=WE(4))
    else:
        for i in range(1, 7):
            t = now + relativedelta(weekday=TH(i))
            if t.month != cmon:
                # since t is exceeded we need last one  which we can get by subtracting -2 since it is already a Thursday.
                mon_thu = (t + relativedelta(weekday=TH(-2))).strftime('%d%b%Y')
                mon_wed = (t + relativedelta(weekday=WE(-2))).strftime('%d%b%Y')
                break
    xpry_resp = xt.get_expiry_date(exchangeSegment=2, series='OPTIDX', symbol='NIFTY')
    if 'result' in xpry_resp:
        expiry_dates = xpry_resp['result']
    else:
        print('Error getting Expiry dates..')
        raise ex.XTSDataException('Issue in getting expiry dates')
    if thu in expiry_dates:
        weekly_exp = thu
        print(f'Thursday - {weekly_exp} is the week expiry')
    elif wed in expiry_dates:
        weekly_exp = wed
        print(f'Wednesday - {weekly_exp} is the week expiry')
    if mon_thu in expiry_dates:
        monthly_exp = mon_thu
        print(f'Thursday - {monthly_exp} is the month expiry')
    elif mon_wed in expiry_dates:
        monthly_exp = mon_wed
        print(f'Wednesday - {monthly_exp} is the month expiry')


