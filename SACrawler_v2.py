# ==============================================

# 科學雜誌爬蟲(function)
# 使用selenium模擬瀏覽器點擊
# BeautifulSoup4 解析文件內容
# 以類別為資料夾分開儲存
# by Lelingyi

# ==============================================

import requests
import urllib.parse
import time
import os.path
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup as btfs

BASIC_URL = 'http://sa.ylib.com/'
SA_URL = urllib.parse.urljoin(BASIC_URL, 'CategoryList.aspx')
MAXPAGE = 100  # max get page
# 雜誌類別網站
# SITE = ['physics', 'astronomy', 'medicine', 'ecology',
#         'lifescien', 'earthscien', 'InfoTech', 'other']

SITE = ['InfoTech']


def _addparag(match):
    return '|||'+match.group()


# --取得所有雜誌鏈結
def get_article_url(driver):
    url = []  # 雜誌內容鏈結
    for _ in range(MAXPAGE):
        soup = btfs(driver.page_source, 'html.parser')  # 網站原始碼

        # 解析出雜誌內容連結
        for a in soup.select('.content_mixbox_txt > h4 > a'):
            url.append(urllib.parse.urljoin(BASIC_URL, a['href']))

        try:
            next_page_btn = driver.find_element_by_id('ctl00_ContentPlaceHolder2_lnkbtnNext')  # 取得下一頁按紐

            if next_page_btn.get_attribute('disabled'):  # 不可按代表最後一頁
                break
            else:
                time.sleep(0.5)  # 間格時間,防止對網站query過快
                next_page_btn.click()

        except NoSuchElementException:
            print('NoSuchElementException')

    return url


# --iterate雜誌鏈結，解析文章內容
def parser_article(url):
    req = requests.get(url)
    if req.status_code == 200:
        soup = btfs(req.content, 'html.parser')
        try:
            title = soup.find('h1', class_='art-title').get_text().strip()
            sub_title = soup.find('p', class_='art-sub').get_text()
            sub_title = re.sub(r'\s', '', sub_title)
            title = title + ' : ' + sub_title

            content = str(soup.find('div', class_='art-main'))
            content = re.sub(r'(<br/></p>)|(</p><br/>)|(<br/><br/>)', _addparag, content)
            content = btfs(content, 'html.parser').get_text()
            content = re.sub(r'\s', '', content).split('|||')
            content = '\n'.join(content)

        except Exception as e:
            print('something wrong in', url)
            print('Error:', e)
            return {'stat': 0}
    else:
        return {'stat': 0}

    return {'title': title, 'content': content, 'stat': 1}


# --開始爬蟲
chrome_options = Options()  # set chrome option
chrome_options.add_argument('--headless')  # 不開啟瀏覽器方式
driver = webdriver.Chrome(chrome_options=chrome_options)

for site in SITE:
    try:
        driver.get(SA_URL+'?Unit=featurearticles&Cate='+site)  # 取得網址控制
        magazine_url = get_article_url(driver)

        # 解析文章內容(title,subtitle,content)
        start_time = time.time()
        print('start', site)

        save_folder = './sa_magazines/%s/' % site
        try:  # check directory
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)
        except OSError:
            print('Error:creating directory:', save_folder)

        for name, url in enumerate(magazine_url, start=1):
            magazine = parser_article(url)

            if magazine['stat']:
                # save file
                save_path = save_folder + '%s.txt' % name
                with open(save_path, mode='w', encoding='utf-8') as f:
                    f.write(magazine['title'])
                    f.write('\n')
                    f.write(magazine['content'])

            time.sleep(1)

        print('cost', time.time()-start_time)

    except TimeoutException:
        print(site+' Timeout')

driver.close()  # 關閉瀏覽器視窗,釋放資源

