from django.shortcuts import render


# Create your views here.
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from pprint import pprint
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
import time
import json
import csv
from .models import Store


def GetStoreID():
# df = pd.read_csv('main/jejulist.csv', encoding='cp949')
    df1 = pd.read_csv('jejulist.csv', encoding='UTF-8')
    df = df1.head(3)

    jeju_store = df[['업소명','소재지','메뉴']]
    print(jeju_store.head())
    jeju_store.columns = [ 'name','address','menu']

    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    jeju_store['kakao_keyword'] = jeju_store['address'] # "%20"는 띄어쓰기를 의미합니다.
    store_detail_list = []


    # 상세페이지 주서 따기
    for i, keyword in enumerate(jeju_store['kakao_keyword'].tolist()):
        print("이번에 찾을 키워드 :", i, f"/ {df.shape[0] -1} 행", keyword)
        kakao_map_search_url = f"https://map.kakao.com/?q={keyword}"

        driver.get(kakao_map_search_url)
        time.sleep(1)
        df.iloc[i,-1] = driver.find_element(By.CSS_SELECTOR,"#info\.search\.place\.list > li > div.info_item > div.contact.clickArea > a.moreview").get_attribute('href')

        store_detail_list.append(df.iloc[i,-1])
        # df.iloc[i,-1] = driver.find_element '//*[@id="info.search.place.list"]/li/div[5]/div[4]/a[1]').click()
    print(store_detail_list)

    for url in store_detail_list:
        url = url.split('/')
        print(url[-1])
        Store(store_id=url[-1]).save()

    store_info = []
    for store in store_detail_list:
        # driver.get(https://place.map.kakao.com/+f{'store_id'}) 주석풀고 이용하세요!
        driver.get(store)
        time.sleep(1)
        review_info = {
            'store_name': '',
            'tags': [],
            'contents': [],
        }
        review_info['star'] = driver.find_element(By.CLASS_NAME,"ahead_info").find_element(By.CLASS_NAME,"grade_star").find_element(By.CLASS_NAME, "num_rate").text
        reviews = driver.find_element(By.CLASS_NAME,"list_evaluation").find_elements(By.TAG_NAME, "li")
        for review in reviews:
            review_content = {}
            review_tag ={}
            if not review.text : #or driver.find_element(By.CLASS_NAME,"group_likepoint").find_elements(By.TAG_NAME, "span"):
                continue
            try:
                tags = review.find_element(By.CLASS_NAME, "group_likepoint").find_elements(By.TAG_NAME, "span")
                review_tag['tag'] = [x.text for x in tags]
            except NoSuchElementException:
                review_tag['tag'] = None

            try:
                review_content['content'] = review.find_element(By.CLASS_NAME, "txt_comment").text
            except NoSuchElementException:
                # 식별값(있지만 없어도 되는 값)
                review_content['content'] = None

            review_info['tags'].append(review_tag)
            review_info['contents'].append(review_content)
            
        store_info.append(review_info)
        Store(tags=review_tag, contents=review_content).save()
        
    pprint(store_info)
GetStoreID()


# def toJson(store_info):
#     with open('store_info.json', 'w', encoding='utf-8') as file :
#         json.dump(store_info, file, ensure_ascii=False, indent='\t')
        
# toJson(store_info)

