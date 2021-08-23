# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 16:59:17 2021

@author: WELCOME
"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import pyperclip
# # Replace below path with the absolute path
# # to chromedriver in your computer
# driver = webdriver.Chrome(r'C:\Users\WELCOME\Downloads\chromedriver.exe')

# driver.get("https://web.whatsapp.com/")
# wait = WebDriverWait(driver, 600)

# # Replace 'Friend's Name' with the name of your friend
# # or the name of a group
# target = '"FC aaa"'

# # Replace the below string with your own message
# string = "Message sent using Python!!!"

# x_arg = '//span[contains(@title,' + target + ')]'
# group_title = wait.until(EC.presence_of_element_located((
# 	By.XPATH, x_arg)))
# group_title.click()
# inp_xpath = '//div[@class="input"][@dir="auto"][@data-tab="1"]'
# input_box = wait.until(EC.presence_of_element_located((
# 	By.XPATH, inp_xpath)))
# for i in range(100):
# 	input_box.send_keys(string + Keys.ENTER)
# 	time.sleep(1)

wait = None
browser = None
Link = "https://web.whatsapp.com/"
chrome_path = r'C:\Users\WELCOME\Downloads\chromedriver.exe'
datadir =  r'C:\Users\WELCOME\Downloads\datadir'
headless = True
message = "Message sent using Python"
unsaved_Contacts = ['919677109063']
# with open('groups.txt', 'r', encoding='utf8') as f:
#     unsaved_Contacts = [group.strip() for group in f.readlines()]
with open('msg.txt', 'r', encoding='utf8') as f:
    msg = f.read()
pyperclip.copy(msg)  
def whatsapp_login(chrome_path, headless):
    global wait, browser, Link
    chrome_options = Options()
    chrome_options.add_argument(f'--user-data-dir={datadir}')
    if headless == 'True':
        chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(executable_path=chrome_path, options=chrome_options)
    wait = WebDriverWait(browser, 600)
    browser.get(Link)
    browser.maximize_window()
    print("QR scanned")
  
    
def send_unsaved_contact_message():
    global message
    try:
        time.sleep(5)
        browser.implicitly_wait(10)
        # input_box = browser.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')
        input_xpath = '//div[@contenteditable="true"][@data-tab="6"]'
        input_box = browser.find_element_by_xpath(input_xpath)        
        # for ch in message:
        #     if ch == "\n":
        #         ActionChains(browser).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.ENTER).key_up(
        #             Keys.SHIFT).key_up(Keys.BACKSPACE).perform()
        #     else:
        #         input_box.send_keys(ch)
        #     input_box.send_keys(ch)
        # input_box.send_keys(Keys.ENTER)
        # pyperclip.copy(msg)
        input_box.send_keys(Keys.SHIFT, Keys.INSERT)  # Keys.CONTROL + "v"
        input_box.send_keys(Keys.ENTER)
        print("Message sent successfully")
    except Exception as e:
        print("Failed to send message exception: ", e)
        return

    
def sender():
    global unsaved_Contacts
    print(unsaved_Contacts)
    if len(unsaved_Contacts) > 0:
        for i in unsaved_Contacts:
            link = "https://web.whatsapp.com/send?phone={}&text&source&data&app_absent".format(i)
            # driver  = webdriver.Chrome()
            browser.get(link)
            print("Sending message to", i)
            send_unsaved_contact_message()
            time.sleep(5)
            
            
if __name__ == "__main__":
    print("Web Page Open")
    print("SCAN YOUR QR CODE FOR WHATSAPP WEB")
    whatsapp_login(chrome_path, headless)
    sender()
    