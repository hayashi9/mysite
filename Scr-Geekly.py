# browser = webdriver.Chrome(executable_path='●')について
# ●にchromedriverまでのパスを入れる必要あり。

######################## インポート ########################

# jsonデータを取得するため
from bs4 import BeautifulSoup
import requests
from pandas.io.json import dumps
from pandas.io.json import loads

# csvの読み取りと収集したデータの保存のため
from pandas import *

# webクローリングのため
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# 待ち時間
import time

######################## プログラム ########################

# 最初のページまで行く
# executable_path='●'　の●にchromedriverまでのパスを入れる必要あり。
browser = webdriver.Chrome(executable_path='')
url = 'https://www.geekly.co.jp/search/job_list/'
browser.get(url)
browser.maximize_window()
columns = ['INDEX', '会社名', '職種', '必要言語', '実務経験', '掲載日'\
    , '資本金', '売上', '自社サービス開発', '未経験可', 'URL']
PL = ['Ruby', 'PHP', 'Python', 'C++', 'Java', 'JavaScript', 'Go', 'Kotlin']
try:
    df = pandas.read_csv('Geekly.csv', index_col=0)
except pandas.errors.EmptyDataError:
    df = pandas.DataFrame(columns=columns)

# 最初からある程度絞る為検索する
search = browser.find_element_by_name('free_word')
search.clear()
search.send_keys('web系SE・PG（自社製品）')
search.send_keys(Keys.RETURN)

page = 1
index = 0

# 最後のページまで遷移する。
while True:
    print('######################## page : {} ########################'.format(page))
    print('Starting to get posts......')
    time.sleep(3)
    detail_urls = []
    browser.implicitly_wait(30)
    posts = browser.find_elements_by_class_name('search__list-item')
    for post in posts:
        detail_url = post.find_element_by_css_selector('a').get_attribute('href')
        detail_urls.append(detail_url)
    browser.implicitly_wait(30)


    for i in range(len(detail_urls)):
        pl = []
        index += 1
        browser.implicitly_wait(30)
        browser.get(detail_urls[i])
        browser.implicitly_wait(30)

        #一覧のクラス取得
        table_elm = browser.find_elements_by_class_name('resume')[1]

        # 会社名
        company_name  = table_elm.find_elements(By.TAG_NAME, 'td')[1].text.strip('"')

        # 職種
        job_code = browser.find_element_by_class_name('code').text.strip('職種コード：')

        #必要言語　
        required_skills = browser.find_element_by_id('movable002').text.strip('br')
        for j in PL:
            if required_skills.find(j) > 0:
                pl.append(j)
        if len(pl) > 0:
            pl = ','.join(pl)
        else:
            pl = '該当なし'

        #実務経験
        if required_skills.find('実務') > 0 :
            pra = '✓'
        else :
            pra = ''

        #掲載開始日
        r = requests.get(detail_urls[i])
        soup = BeautifulSoup(r.content, "lxml")
        sd = soup.find_all("script", {"type": "application/ld+json"})
        for n in sd:
            json_data = loads(dumps(n.get_text(), ensure_ascii=False))
            fd = json_data.find('datePosted')
            date = json_data[fd+14:fd+26].strip('"')

        #資本金
        capital = table_elm.find_elements(By.TAG_NAME, 'td')[3].text.strip('"')

        #売上
        sales = table_elm.find_elements(By.TAG_NAME, 'td')[4].text.strip('"')

        #自社サービスというワードが入っているか
        all = browser.find_element_by_css_selector('body').text.strip()
        if all.find('自社サービス') > 0:
            in_house = '〇'
        else:
            in_house = '×'

        #未経験というワードが入っているか
        if all.find('未経験') > 0:
            experience = '〇'
        else:
            experience = '×'

        data = pandas.Series([index, company_name, job_code, pl, pra, date,\
                                capital, sales, in_house, experience, detail_urls[i]], columns)
        df = df.append(data, ignore_index=True)
        print("{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}".\
              format(index, company_name, job_code, pl, pra, date,\
                     capital, sales, in_house, experience,detail_urls[i]))

        time.sleep(3)
        browser.implicitly_wait(20)
        browser.back()
        browser.implicitly_wait(20)

    try:
        page += 1
        browser.implicitly_wait(30)
        next_link = browser.find_element_by_link_text(str(page))
        browser.implicitly_wait(30)
        print('Calling nextpage...')
        time.sleep(5)
        browser.implicitly_wait(30)
        next_link.click()
        browser.implicitly_wait(30)
    except NoSuchElementException:
        break

df.to_csv('Geekly.csv', encoding='utf-8-sig')
print('Done!')
browser.close()
