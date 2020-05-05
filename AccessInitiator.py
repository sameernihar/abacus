import logging
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import urllib.parse as urlparse
from selenium.webdriver.chrome.options import Options
from kiteconnect import KiteConnect

logging.basicConfig(level=logging.DEBUG)


class AccessInitiator:
    def __init__(self):
        f = open("config.json", "r"); jsonconfig = f.read(); f.close()
        brokerconfig = json.loads(jsonconfig)
        self.apikey = brokerconfig['apikey']
        self.apisecret = brokerconfig['apisecret']
        self.accesstoken = ""
        self.requesttoken = ""
        self.username = brokerconfig['username']
        self.password = brokerconfig['password']
        self.pin = brokerconfig['pin']
        self.loginurl = brokerconfig['loginurl']
        self.dataurl = brokerconfig['dataurl']
        self.chromedriverpath = brokerconfig['chromedriverpath']
        self.conn = ""

    def getaccesstoken(self):
        try:
            options = Options()
            ### By enabling below option you can run chrome without UI
            #options.add_argument('--headless')
            ## chrome driver object
            driver = webdriver.Chrome(self.chromedriverpath, chrome_options=options)
            ## load the url into chrome
            driver.get(self.loginurl)
            ## wait to load the site
            wait = WebDriverWait(driver, 20)
            ## Find User Id field and set user id
            wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="text"]'))) \
                .send_keys(self.username)
            ## Find password field and set user password
            wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="password"]'))) \
                .send_keys(self.password)
            ## Find submit button and click
            wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))) \
                .submit()
            ## Find pin field and set  pin value
            #wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="password"]'))).click()
            time.sleep(5)
            driver.find_element_by_xpath('//input[@type="password"]').send_keys(self.pin)
            ## Final Submit
            wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))).submit()
            ## wait for redirection
            wait.until(EC.url_contains('status=success'))
            ## get the token url after success
            tokenurl = driver.current_url
            parsed = urlparse.urlparse(tokenurl)
            driver.close()
            self.requesttoken = urlparse.parse_qs(parsed.query)['request_token'][0]
            self.conn = KiteConnect(api_key=self.apikey)
            data = self.conn.generate_session(self.requesttoken, api_secret=self.apisecret)
            self.accesstoken = data["access_token"]
            #print(data["access_token"])
        except Exception as ex:
            print(ex)

    def refresh_conn(self):
        self.conn = KiteConnect(api_key=self.apikey)
        if self.accesstoken != "":
            self.conn.set_access_token(self.accesstoken)

    def printallbrokervalues(self):
        print('apikey', ':', self.apikey)
        #print('apisecret', ':', self.apisecret)
        print('username', ':', self.username)
        #print('password', ':', self.password)
        #print('requestToken', ':', self.requesttoken)
        print('accessToken', ':', self.accesstoken)
        #print('pin', ':', self.pin)