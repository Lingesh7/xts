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


headers = {'Connection': 'keep-alive',
           'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-GPC': '1',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Referer': 'https://tradetron.tech//deployed-strategies',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cookie': 'country_code=eyJpdiI6IlZqUHJ0Y3RoU044UHJTRThaSVI2ZEE9PSIsInZhbHVlIjoielhXYjZPRUxjZVBnVHBNQnhCXC80SFE9PSIsIm1hYyI6IjVkZDJlMjkxYzE0M2E5MjZjNjVkYzZjODVkNDc3ODQ5NjQ0NDUwNzE1OWQ0ZWZkZmU1ODYxOWNiMTBjZTFhM2MifQ%3D%3D; _fbp=fb.1.1606220024534.1297436447; __stripe_mid=fc840f40-6a31-4a39-b449-ff470a617df03e164a; http-refer=eyJpdiI6IlE4Y3dKZ2hIVW1nTk9cL2dXd2N1K29RPT0iLCJ2YWx1ZSI6IjJOT211RHRDdXpDMHpya3pYbXJCSTlmME9JajZvUDdHb1N0b1ZpMzRSWmkxOW41bUp5cnk0SWRmUVNoUm5LdkkiLCJtYWMiOiIxMTc4ZjVkYjAwMTYwMDAxM2QwMWQyYmZhMTM4ZWEzNWIwM2EzZTBkNmE1NWFlNzkwNDc5MzYwMTA5MDlhZGEwIn0%3D; __cfduid=da5d9dbdc12397a3739d0df84fa970d291614102540; chatlio_uuid--00593f8f-3a67-4245-7d6f-997306ba3cdf=445a18bf-bd52-4273-b470-feb6adade974; chatlio_uuid--258d00e0-9e54-4c22-7ac9-86ebbc7f2bac=dbdd1848-bfd3-451a-b582-e5d13d43c8e1; chatlio_rt--00593f8f-3a67-4245-7d6f-997306ba3cdf=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjZVVVSUQiOiIwMDU5M2Y4Zi0zYTY3LTQyNDUtN2Q2Zi05OTczMDZiYTNjZGYiLCJleHAiOjE2NzkxNDg3MTMsImlhdCI6MTYxNjA3NjcxMywidnNVVUlEIjoiNDQ1YTE4YmYtYmQ1Mi00MjczLWI0NzAtZmViNmFkYWRlOTc0In0.tERGtyjG1SUCbqeb0DrfX8n6KHdkOvop7MQqCcltuq4; chatlio_at--00593f8f-3a67-4245-7d6f-997306ba3cdf=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjZVVVSUQiOiIwMDU5M2Y4Zi0zYTY3LTQyNDUtN2Q2Zi05OTczMDZiYTNjZGYiLCJleHAiOjE2MTYwODM5MTMsImlhdCI6MTYxNjA3NjcxMywidnNVVUlEIjoiNDQ1YTE4YmYtYmQ1Mi00MjczLWI0NzAtZmViNmFkYWRlOTc0In0.0QsSTm1nrHL_xjzBcH2NGQ2-NfuX2lUskl_29lXPARk; XSRF-TOKEN=eyJpdiI6ImJQNlY2dVdGUkpMemY4T1h4dHdFUkE9PSIsInZhbHVlIjoiT2d0UnpEdlU1SUNEZVJ1c1VvUjUxTXViY2g5cVkrbXdlMmVHbGlValZScmxGS3Z1UFYyK0Nqc3pFc1wvVlwvcENLIiwibWFjIjoiNjY0NjhiMjJlNjkyYzYyYzZmNzc4YWUxMmU4ZjY3YTE3MGM3ZTE2MTIzMDJiMDJlYTBiNDBlN2NjNGM4NzNlNCJ9; tradetron_session=eyJpdiI6IkF6XC8wMDBjcFFzQnpCWTY5cEl1Rm1BPT0iLCJ2YWx1ZSI6InZWYm1hVFpKN0l5MjgyUmw5RGR6MnAraDN4d2ZmVytLampQakp4Rmg1Y0NxNm9iaTM0c1B5WFQrRkZ0M2FuajgiLCJtYWMiOiJkOGUwYzRkOTA1ODdhY2RiODQ5ZWZmYmI4ZDkwYjQ1OTkzNWNiYTJkOTk5N2RiMDQ0ZDZiMTRjYWJkN2I3ZjVhIn0%3D; chatlio_rt--258d00e0-9e54-4c22-7ac9-86ebbc7f2bac=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjZVVVSUQiOiIyNThkMDBlMC05ZTU0LTRjMjItN2FjOS04NmViYmM3ZjJiYWMiLCJleHAiOjE2NzkxNDg3MjEsImlhdCI6MTYxNjA3NjcyMSwidnNVVUlEIjoiZGJkZDE4NDgtYmZkMy00NTFhLWI1ODItZTVkMTNkNDNjOGUxIn0.9LXmbGDWTofXjinKlLAn7riOwl40D_L7RVRsWAIW0xs; chatlio_at--258d00e0-9e54-4c22-7ac9-86ebbc7f2bac=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjZVVVSUQiOiIyNThkMDBlMC05ZTU0LTRjMjItN2FjOS04NmViYmM3ZjJiYWMiLCJleHAiOjE2MTYwODM5MjEsImlhdCI6MTYxNjA3NjcyMSwidnNVVUlEIjoiZGJkZDE4NDgtYmZkMy00NTFhLWI1ODItZTVkMTNkNDNjOGUxIn0.4D_9zYkkWSLzfjSmLrwh8Se6T-Ps06qWJ5fQ0T8yhXc'
           }
url='https://tradetron.tech/deployed/all/389444'
r = requests.get(url, headers=headers)


PATH = r"D:\Users\lmahendran\Downloads\chromedriver.exe"
option =  Options()
option.add_argument('--disable-notifications')
option.add_argument("Connection=keep-alive")
option.add_argument("Upgrade-Insecure-Requests=1")
option.add_argument("User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36")
option.add_argument("Accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9")
option.add_argument("Sec-GPC=1")
option.add_argument("Sec-Fetch-Site=same-origin")
option.add_argument("Sec-Fetch-Mode=navigate")
option.add_argument("Sec-Fetch-User=?1")
option.add_argument("Sec-Fetch-Dest=document")
option.add_argument("Referer=https://tradetron.tech//deployed-strategies")
option.add_argument("Accept-Encoding=gzip, deflate, br")
option.add_argument("Accept-Language=en-US,en;q=0.9")
option.add_argument("Cookie=country_code=eyJpdiI6IlZqUHJ0Y3RoU044UHJTRThaSVI2ZEE9PSIsInZhbHVlIjoielhXYjZPRUxjZVBnVHBNQnhCXC80SFE9PSIsIm1hYyI6IjVkZDJlMjkxYzE0M2E5MjZjNjVkYzZjODVkNDc3ODQ5NjQ0NDUwNzE1OWQ0ZWZkZmU1ODYxOWNiMTBjZTFhM2MifQ%3D%3D; _fbp=fb.1.1606220024534.1297436447; __stripe_mid=fc840f40-6a31-4a39-b449-ff470a617df03e164a; http-refer=eyJpdiI6IlE4Y3dKZ2hIVW1nTk9cL2dXd2N1K29RPT0iLCJ2YWx1ZSI6IjJOT211RHRDdXpDMHpya3pYbXJCSTlmME9JajZvUDdHb1N0b1ZpMzRSWmkxOW41bUp5cnk0SWRmUVNoUm5LdkkiLCJtYWMiOiIxMTc4ZjVkYjAwMTYwMDAxM2QwMWQyYmZhMTM4ZWEzNWIwM2EzZTBkNmE1NWFlNzkwNDc5MzYwMTA5MDlhZGEwIn0%3D; __cfduid=da5d9dbdc12397a3739d0df84fa970d291614102540; chatlio_uuid--00593f8f-3a67-4245-7d6f-997306ba3cdf=445a18bf-bd52-4273-b470-feb6adade974; chatlio_uuid--258d00e0-9e54-4c22-7ac9-86ebbc7f2bac=dbdd1848-bfd3-451a-b582-e5d13d43c8e1; chatlio_rt--00593f8f-3a67-4245-7d6f-997306ba3cdf=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjZVVVSUQiOiIwMDU5M2Y4Zi0zYTY3LTQyNDUtN2Q2Zi05OTczMDZiYTNjZGYiLCJleHAiOjE2NzkxNDg3MTMsImlhdCI6MTYxNjA3NjcxMywidnNVVUlEIjoiNDQ1YTE4YmYtYmQ1Mi00MjczLWI0NzAtZmViNmFkYWRlOTc0In0.tERGtyjG1SUCbqeb0DrfX8n6KHdkOvop7MQqCcltuq4; chatlio_at--00593f8f-3a67-4245-7d6f-997306ba3cdf=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjZVVVSUQiOiIwMDU5M2Y4Zi0zYTY3LTQyNDUtN2Q2Zi05OTczMDZiYTNjZGYiLCJleHAiOjE2MTYwODM5MTMsImlhdCI6MTYxNjA3NjcxMywidnNVVUlEIjoiNDQ1YTE4YmYtYmQ1Mi00MjczLWI0NzAtZmViNmFkYWRlOTc0In0.0QsSTm1nrHL_xjzBcH2NGQ2-NfuX2lUskl_29lXPARk; XSRF-TOKEN=eyJpdiI6ImJQNlY2dVdGUkpMemY4T1h4dHdFUkE9PSIsInZhbHVlIjoiT2d0UnpEdlU1SUNEZVJ1c1VvUjUxTXViY2g5cVkrbXdlMmVHbGlValZScmxGS3Z1UFYyK0Nqc3pFc1wvVlwvcENLIiwibWFjIjoiNjY0NjhiMjJlNjkyYzYyYzZmNzc4YWUxMmU4ZjY3YTE3MGM3ZTE2MTIzMDJiMDJlYTBiNDBlN2NjNGM4NzNlNCJ9; tradetron_session=eyJpdiI6IkF6XC8wMDBjcFFzQnpCWTY5cEl1Rm1BPT0iLCJ2YWx1ZSI6InZWYm1hVFpKN0l5MjgyUmw5RGR6MnAraDN4d2ZmVytLampQakp4Rmg1Y0NxNm9iaTM0c1B5WFQrRkZ0M2FuajgiLCJtYWMiOiJkOGUwYzRkOTA1ODdhY2RiODQ5ZWZmYmI4ZDkwYjQ1OTkzNWNiYTJkOTk5N2RiMDQ0ZDZiMTRjYWJkN2I3ZjVhIn0%3D; chatlio_rt--258d00e0-9e54-4c22-7ac9-86ebbc7f2bac=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjZVVVSUQiOiIyNThkMDBlMC05ZTU0LTRjMjItN2FjOS04NmViYmM3ZjJiYWMiLCJleHAiOjE2NzkxNDg3MjEsImlhdCI6MTYxNjA3NjcyMSwidnNVVUlEIjoiZGJkZDE4NDgtYmZkMy00NTFhLWI1ODItZTVkMTNkNDNjOGUxIn0.9LXmbGDWTofXjinKlLAn7riOwl40D_L7RVRsWAIW0xs; chatlio_at--258d00e0-9e54-4c22-7ac9-86ebbc7f2bac=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjZVVVSUQiOiIyNThkMDBlMC05ZTU0LTRjMjItN2FjOS04NmViYmM3ZjJiYWMiLCJleHAiOjE2MTYwODM5MjEsImlhdCI6MTYxNjA3NjcyMSwidnNVVUlEIjoiZGJkZDE4NDgtYmZkMy00NTFhLWI1ODItZTVkMTNkNDNjOGUxIn0.4D_9zYkkWSLzfjSmLrwh8Se6T-Ps06qWJ5fQ0T8yhXc")

driver = webdriver.Chrome(PATH, options=option)
driver.maximize_window()
driver.get(url)











audioToTextDelay = 10
delayTime = 2
audioFile = "\\payload.mp3"
SpeechToTextURL = "https://speech-to-text-demo.ng.bluemix.net/"
PATH = r"D:\Users\lmahendran\Downloads"
#PATH = "C:\\Users\\Welcome\\Downloads\\chromedriver.exe"
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
    # option.add_argument('--headless')
    # option.add_argument('--mute-audio')
    option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4389.82 Safari/537.36")
    #option.add_argument("user_agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36")
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


