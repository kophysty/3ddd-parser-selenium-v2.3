# from selenium import webdriver

from selenium import webdriver
from bs4 import BeautifulSoup
import time

options = webdriver.ChromeOptions()
options.add_argument('--ignore-ssl-errors')
prefs = {"profile.managed_default_content_settings.images":2}

options.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(executable_path='driver\\chromedriver.exe', chrome_options=options)

driver.get('https://3ddd.ru/login')

login_3ddd = False

while (login_3ddd == False):
    time.sleep(0.5)
    if(driver.current_url != 'https://3ddd.ru/login'):
        login_3ddd = True

