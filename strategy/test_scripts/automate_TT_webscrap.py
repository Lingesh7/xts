# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 22:31:38 2021
web scrapping TT
@author: mling
"""
import time
import sys
from datetime import datetime as dt
import os
import requests
import urllib
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


audioToTextDelay = 10
delayTime = 2
audioFile = "\\payload.mp3"
SpeechToTextURL = "https://speech-to-text-demo.ng.bluemix.net/"
# PATH = "C:\\Users\\mling\\Downloads\\chromedriver.exe"
PATH = "C:\\Users\\Welcome\\Downloads\\chromedriver.exe"
URL = 'https://tradetron.tech/'

# options = Options()
# options.add_argument("--disable-notifications")
# PATH = "C:\\Users\\mling\\Downloads\\chromedriver.exe"
# driver = webdriver.Chrome(PATH,chrome_options=options)
# driver.maximize_window()
# driver.get('https://tradetron.tech/')

def delay():
    time.sleep(random.randint(2, 3))

def audioToText(audioFile):
    driver.execute_script('''window.open("","_blank")''')
    driver.switch_to.window(driver.window_handles[1])
    driver.get(SpeechToTextURL)

    delay()
    audioInput = driver.find_element(By.XPATH, '//*[@id="root"]/div/input')
    audioInput.send_keys(audioFile)

    time.sleep(audioToTextDelay)

    text = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[7]/div/div/div/span')
    while text is None:
        text = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[7]/div/div/div/span')

    result = text.text

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    return result

try:
    # create chrome driver
    option =  Options()
    option.add_argument('--disable-notifications')
    # option.add_argument('headless')
    # option.add_argument('--mute-audio')
    # option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4389.82 Safari/537.36")
    option.add_argument("user_agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36")
    driver = webdriver.Chrome(PATH, options=option)
    driver.maximize_window()
    # delay()
    # go to website which have recaptcha protection
    driver.get('https://tradetron.tech/')
except Exception:
    sys.exit(
        "[-] Please update the chromedriver.exe in the webdriver folder according to your chrome version:https://chromedriver.chromium.org/downloads")


wait_time = 60 # a very long wait time
element = wait(driver, wait_time).\
    until(EC.element_to_be_clickable((By.LINK_TEXT, 'Sign in')))
element.click()
time.sleep(5)
email = driver.find_element_by_id("modalEmailSignIn")
email.send_keys("prisminvest48@gmail.com")
pswd = driver.find_element_by_id("modalPasswordSignIn")
pswd.send_keys("Algo@123")

# driver.find_element_by_xpath("//input[@type='submit']").submit()

# signin = driver.find_element_by_xpath('//button[text()="Sign in"]')
# signin.submit()




g_recaptcha = driver.find_elements_by_class_name('g-recaptcha')[0]
outerIframe = g_recaptcha.find_element_by_tag_name('iframe')
outerIframe.click()

iframes = driver.find_elements_by_tag_name('iframe')
audioBtnFound = False
audioBtnIndex = -1

for index in range(len(iframes)):
    driver.switch_to.default_content()
    iframe = driver.find_elements_by_tag_name('iframe')[index]
    driver.switch_to.frame(iframe)
    driver.implicitly_wait(delayTime)
    try:
        audioBtn = driver.find_element_by_id("recaptcha-audio-button")
        audioBtn.click()
        audioBtnFound = True
        audioBtnIndex = index
        break
    except Exception as e:
        pass

if audioBtnFound:
    try:
        while True:
            # get the mp3 audio file
            src = driver.find_element_by_id("audio-source").get_attribute("src")
            print("[INFO] Audio src: %s" % src)

            # download the mp3 audio file from the source
            urllib.request.urlretrieve(src, os.getcwd() + audioFile)

            # Speech To Text Conversion
            key = audioToText(os.getcwd() + audioFile)
            print("[INFO] Recaptcha Key: %s" % key)

            driver.switch_to.default_content()
            iframe = driver.find_elements_by_tag_name('iframe')[audioBtnIndex]
            driver.switch_to.frame(iframe)

            # key in results and submit
            inputField = driver.find_element_by_id("audio-response")
            inputField.send_keys(key)
            delay()
            inputField.send_keys(Keys.ENTER)
            delay()
            
            err = driver.find_elements_by_class_name('rc-audiochallenge-error-message')[0]
            print(err.text)
            print(err.value_of_css_property('display'))
            if err.text == "" or err.value_of_css_property('display') == 'none':
                print("[INFO] Success!")
                break

    except Exception as e:
        print(e)
        driver.switch_to.default_content()
        signin = driver.find_element_by_xpath('//button[text()="Sign in"]')
        signin.submit()
        # sys.exit("[INFO] Possibly blocked by google. Change IP,Use Proxy method for requests")
        
else:
    sys.exit("[INFO] Audio Play Button not found! In Very rare cases!")

# driver.switch_to.default_content()

# driver.get('https://tradetron.tech/deployed/all/60053')
delay()
stgBtn = driver.find_element_by_id('dropdownMenuStrategy')
stgBtn.click()
delay()
driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't') 
driver.get("https://tradetron.tech/my-strategies?strategyType=created")
delay()
driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't') 
driver.get("https://tradetron.tech/deployed/all/389444")


