# ==============================================

# 科學雜誌爬蟲(class)
# 使用selenium模擬瀏覽器點擊
# BeautifulSoup4解析文件內容
# by Lelingyi

# ==============================================

import requests
import urllib.parse
import time
import re
from collections import namedtuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup as btfs


class SACrawler():
    BASIC_URL = 'http://sa.ylib.com/'
    SA_URL = urllib.parse.urljoin(BASIC_URL, 'CategoryList.aspx')

    # 雜誌類別網站
    SITE = ['physics', 'astronomy', 'medicine', 'ecology',
            'lifescien', 'earthscien', 'InfoTech', 'other']

    DATATUPLE = namedtuple('Article', ['category', 'title', 'content', 'url'])

    def __init__(self):
        pass

    def _addparag(self,match):
        return '|||' + match.group()

    # --取得所有雜誌鏈結
    def get_url(self, maxpage=100):
        chrome_options = Options()  # set chrome option
        chrome_options.add_argument('--headless')  # 不開啟瀏覽器方式

        with webdriver.Chrome(chrome_options=chrome_options) as driver:
            url = []  # 雜誌內容鏈結

            # --iterate 雜誌類別
            for site in self.SITE:
                driver.get(self.SA_URL + '?Unit=featurearticles&Cate=' + site)  # 取得網址控制

                for _ in range(maxpage):
                    soup = btfs(driver.page_source, 'html.parser')  # 網站原始碼

                    # 解析出雜誌內容連結
                    for a in soup.select('.content_mixbox_txt > h4 > a'):
                        url.append(urllib.parse.urljoin(self.BASIC_URL, a['href']))

                    try:
                        next_page_btn = driver.find_element_by_id('ctl00_ContentPlaceHolder2_lnkbtnNext')  # 取得下一頁按紐

                        if next_page_btn.get_attribute('disabled'):  # 不可按代表最後一頁
                            break
                        else:
                            time.sleep(0.5)  # 間格時間,防止對網站query過快
                            next_page_btn.click()  # 下一頁

                    except NoSuchElementException:
                        print('NoSuchElementException')

        # driver.close()  # 關閉瀏覽器視窗,釋放資源

        return url

    # --iterate雜誌鏈結，解析文章內容
    def parser(self, url):
        req = requests.get(url)
        if req.status_code == 200:
            soup = btfs(req.content, 'html.parser')
            try:
                category = soup.find('h4', class_='catgr').get_text().strip()
                title = soup.find('h1', class_='art-title').get_text().strip()
                sub_title = soup.find('p', class_='art-sub').get_text()
                sub_title = re.sub(r'\s', '', sub_title)
                title = title + ' : ' + sub_title

                content = str(soup.find('div', class_='art-main'))
                content = re.sub(r'(<br/></p>)|(</p><br/>)|(<br/><br/>)', self._addparag, content)
                content = btfs(content, 'html.parser').get_text()
                content = re.sub(r'\s', '', content).split('|||')
                content = '\n'.join(content)

            except Exception as e:
                print('something wrong in', url)
                print('Error:', e)
                return False

            time.sleep(1)  # 間格時間,防止對網站query過快
            return self.DATATUPLE(category, title, content, url)
        else:
            return False


if __name__ == '__main__':
    crawler = SACrawler()

    start_time = time.time()
    article_url = crawler.get_url(maxpage=1)
    print('"get_url" cost time:', time.time()-start_time)

    # 解析文章內容(category,title,subtitle,content,url)
    start_time = time.time()
    articles = []
    for url in article_url:
        art = crawler.parser(url)
        if art:
            print(art)
            articles.append(art)
    print('"parser" cost time:', time.time() - start_time)

