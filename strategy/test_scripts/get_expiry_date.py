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



driver.



































