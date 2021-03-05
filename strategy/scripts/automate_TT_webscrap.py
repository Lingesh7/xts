# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 22:31:38 2021
web scrapping TT
@author: mling
"""
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

options = Options()
options.add_argument("--disable-notifications")
PATH = "C:\\Users\\mling\\Downloads\\chromedriver.exe"
driver = webdriver.Chrome(PATH,chrome_options=options)
driver.maximize_window()
driver.get('https://tradetron.tech/')

# signin = driver.find_element_by_id("Sign in")
# signin = driver.find_element_by_link_text("Sign in")
# signin.click()
# uname.send_keys("prisminvest48@gmail.com")

# wait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Sign in']"))).click()
# for element in driver.find_elements_by_css_selector('span'):
#     element.click()
wait_time = 60 # a very long wait time
element = wait(driver, wait_time).\
    until(EC.element_to_be_clickable((By.LINK_TEXT, 'Sign in')))
element.click()

email = driver.find_element_by_id("modalEmailSignIn")
email.send_keys("prisminvest48@gmail.com")