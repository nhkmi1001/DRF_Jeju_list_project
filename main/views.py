from django.shortcuts import render
# Create your views here.
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from pprint import pprint
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from tqdm import tqdm
from django.conf import settings
import time
from main.models import Store, Tags
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.metrics.pairwise import cosine_similarity
# 포문 하나로 뭉친거
def GetStoreId():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument("--disable-dev-shm-usage")
        # df = pd.read_csv('main/jejulist.csv', encoding='cp949')
    df1 = pd.read_csv('main/jejulist.csv', encoding='utf-8')
    df = df1.head(10)
    jeju_store = df[['업소명','소재지','메뉴']]
    print(jeju_store.head())
    jeju_store.columns = [ 'name','address','menu']
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    jeju_store['kakao_keyword'] = jeju_store['address'] # "%20"는 띄어쓰기를 의미합니다.

    # 상세페이지 주서 따기
    # store_info = []
    store_name_list = []
    store_review_list = []

    for i, keyword in enumerate(jeju_store['kakao_keyword'].tolist()):
        print("이번에 찾을 키워드 :", i, f"/ {df.shape[0] -1} 행", keyword)
        kakao_map_search_url = f"https://map.kakao.com/?q={keyword}"
        driver.get(kakao_map_search_url)
        time.sleep(2)
        df.iloc[i,-1] = driver.find_element(By.CSS_SELECTOR,"#info\.search\.place\.list > li > div.info_item > div.contact.clickArea > a.moreview").get_attribute('href')
        url = df.iloc[i,-1]
        store_id = url.split('/')[-1]
        store = Store(store_id=store_id)
        driver.get(url)
        time.sleep(2)
        # review = Reviews(content=review_info['contents'])
        review_info = {
            'store_name': [],
            'star': '',
            'content': [],
        }
        tags_list = {
            'name':[],
        }
        tag_model = Tags()
        review_info['store_name'] = driver.find_element(By.CLASS_NAME, "inner_place").find_element(By.CLASS_NAME, "tit_location").text
        try:
            review_info['star'] = driver.find_element(By.CLASS_NAME,"ahead_info").find_element(By.CLASS_NAME,"grade_star").find_element(By.CLASS_NAME, "num_rate").text
        except NoSuchElementException:
            review_info['star'] = None

        try:
            reviews = driver.find_element(By.CLASS_NAME,"list_evaluation").find_elements(By.TAG_NAME, "li")
        except NoSuchElementException:
            continue
        try:
            while True:
                more_button = driver.find_element(By.CLASS_NAME,"link_more")
                # print(type(more_button.text), "접기" in more_button.text)
                if "접기" in more_button.text:
                    break
                # print("clicked!!!!")
                # print(more_button.text)
                more_button.click()
        except BaseException:
            pass

        for review in reviews:
            review_content_str = {}
            review_tags = set()
            if not review.text : #or driver.find_element(By.CLASS_NAME,"group_likepoint").find_elements(By.TAG_NAME, "span"):
                continue
            try:
                tags = review.find_element(By.CLASS_NAME, "group_likepoint").find_elements(By.TAG_NAME, "span")
                review_tags = [x.text for x in tags]
            except NoSuchElementException:
                review_tags = None
            # try:
            #     review_more = review.find_element(By.CLASS_NAME, "txt_comment").find_element(By.TAG_NAME, "button")
            #     review_more.click()
            # except:
            #     continue
            try:
                review_content = review.find_element(By.CLASS_NAME, "txt_comment").text
                result = ''.join(s for s in review_content)
                review_content_str = result.replace("\n", "")
                print(review_content_str)
            except NoSuchElementException:
                # 식별값(있지만 없어도 되는 값)
                review_content_str = None
            review_info['content'].append(review_content_str)
            tags_list['name'].append(review_tags)
        review_info['content'] = ''.join(map(str,review_info['content']))
        print(review_info)
            # tag_model.name = tags_list
        store.store_name = review_info['store_name']
        store.content = review_info['content']
        store.star = review_info['star']
        store.save()

        #코사인유사도검사 부분
        store_name_list.append(review_info['store_name'])
        store_review_list.append(review_info['content'])
        Storedata = pd.DataFrame(data={'상호명':store_name_list, '리뷰내용': store_review_list})
        print(Storedata)

        #상호명 + 리뷰내용 해서 상호명리뷰내용 < 이런식으로 한줄로 표현
        Storedata['합침'] = (Storedata['상호명']) + Storedata['리뷰내용']
        tfidf = TfidfVectorizer(stop_words='english')
        Storedata['합침'] = Storedata['합침'].fillna('')
        tfidf_matrix = tfidf.fit_transform(Storedata['리뷰내용']) # 여기 잘 모르겠다.
        print(tfidf_matrix.shape) # (1,25) -> 25개의 단어가 모여서 1개의 문장
        cosine_martrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
        indices = pd.Series(Storedata.index, index=Storedata['상호명']).drop_duplicates()
        print(indices.head())
        def get_recomm(title, cosine_martrix=cosine_martrix):
            choice = []
            idx = indices[title]
            sim_scores = list(enumerate(cosine_martrix[idx]))
            sim_scores = sorted(sim_scores, key=lambda x:x[1], reverse=True)
            sim_scores = sim_scores[1:5]
            store_indices = [i[0] for i in sim_scores]
            for i in range(5):
                choice.append(Storedata['상호명'][store_indices[i]])
            print('***가게추천***')
            for i in range(5):
                print(str(i+1) + '순위: ' + choice[i])
        get_recomm('사형제횟집')
GetStoreId()