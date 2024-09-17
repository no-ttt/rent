from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import schedule
import os
from datetime import datetime


def spider(driver, driver2, url, region, rentType, data):
  driver.get(url)
  time.sleep(3)

  items =  driver.find_elements(By.CLASS_NAME, 'item-info')  

  for item in items:
    title = item.find_element(By.CLASS_NAME, 'item-info-title')
    print(title.text)
    
    itemUrl = item.find_element(By.CLASS_NAME, 'v-middle').get_attribute('href')
    itemAll = item.find_elements(By.CLASS_NAME, 'item-info-txt')
    layout = itemAll[0].find_element(By.CLASS_NAME, 'line')
    price =  item.find_element(By.CLASS_NAME, 'item-info-price')

    driver2.get(itemUrl)
    contact = driver2.find_element(By.CLASS_NAME, 'base-info-pc').find_element(By.CLASS_NAME, 'name')
    tel = driver2.find_element(By.CSS_SELECTOR, '#__nuxt > section:nth-child(3) > section.main-wrapper > section.aside > section.contact-card > div > div > button > span:nth-child(2) > span')
    address = driver2.find_element(By.CLASS_NAME, 'address').find_element(By.CLASS_NAME, 'load-map')
    
    data.append ({
      '居住地': region,
      '連結': itemUrl,
      '區域': itemAll[1].text.split('-')[0],
      '物件': itemAll[2].text,
      '格局': layout.text,
      '型態': rentType,
      '金額': price.text,
      '聯絡人': contact.text,
      '電話': tel.text,
      '地址': address.text,
    })

  return data

def crawler():
  regions = [
    {'region': '台北市', 'rentType': '整層住家', 'url': 'https://rent.591.com.tw/list?kind=1&region=1&price=5000$_35000$&other=newPost&shType=host'},
    {'region': '台北市', 'rentType': '獨立套房', 'url': 'https://rent.591.com.tw/list?kind=2&region=1&price=5000$_35000$&other=newPost&shType=host'},
    {'region': '新北市', 'rentType': '整層住家', 'url': 'https://rent.591.com.tw/list?kind=1&region=3&price=5000$_35000$&other=newPost&shType=host'},
    {'region': '新北市', 'rentType': '獨立套房', 'url': 'https://rent.591.com.tw/list?kind=2&region=3&price=5000$_35000$&other=newPost&shType=host'}
  ]

  driver = webdriver.Chrome()
  driver2 = webdriver.Chrome()
  data = []

  for item in regions:
    url = item['url']
    region = item['region']
    rentType = item['rentType']

    driver.get(url)
    page = driver.find_element(By.CLASS_NAME, 'paging').find_elements(By.TAG_NAME, 'li')

    i = 1
    while(i <= len(page)):
      data = spider(driver, driver2, url, region, rentType, data)
      # Next page
      i += 1
      url = 'https://rent.591.com.tw/list?kind=1&region=1&price=5000$_35000$&other=newPost&shType=host' + '&page=' + str(i)


  now = datetime.now()
  current_date = now.strftime("%Y-%m-%d")
  current_time = now.strftime("%H:%M:%S")

  file_name = current_date + '_' + current_time + '.csv'
  file_exists = os.path.isfile(file_name)

  df = pd.DataFrame(data)
  df.to_csv(file_name, mode='a', header=not file_exists, index=True, encoding='utf-8')
  driver.close()
  driver2.close()


if __name__ == "__main__":
  schedule.every(1).hours.do(crawler)
  crawler()

  # 每隔 1 小時就執行一次
  while True:
    schedule.run_pending()
    time.sleep(1)