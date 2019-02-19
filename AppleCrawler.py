# ===============================================

# 蘋果即時新聞爬蟲
# 以使用eautifulSoup4解析文件內容
# 使用selenium模擬瀏覽器行為
# by Lelingyi

# ===============================================

import requests
import time
import re
from collections import namedtuple
from bs4 import BeautifulSoup as btfs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class AppleCrawler():
    BASIC_URL = 'https://tw.appledaily.com/new/realtime/'
    DATATUPLE = namedtuple('Article', ['category', 'datetime', 'title', 'content', 'url', 'view'])

    def __init__(self):
        pass

    # --取得新聞鏈結
    def get_url(self, maxpage):
        url = []
        for page in range(1, maxpage + 1):
            req = requests.get(self.BASIC_URL + str(page))
            if req.status_code == 200:  # 確認網站正確連接
                soup = btfs(req.content, 'html.parser')  # 網站原始碼

                # 該頁所有新聞鏈結
                a_link = soup.select('.rtddt > a')
                if a_link:  # 沒有任何鏈結便結束
                    for a in a_link:
                        url.append(a['href'])
                else:
                    break

            time.sleep(1)  # 間格時間,防止對網站query過快
        return url

    # --解析頁面
    def parser(self, url):
        chrome_options = Options()  # set chrome option
        chrome_options.add_argument('--headless')  # 不開啟瀏覽器方式
        with webdriver.Chrome(options=chrome_options) as driver:
            # 開始解析
            try:
                driver.get(url)  # 取得網站控制
                soup = btfs(driver.page_source, 'html.parser')  # 網站原始碼

                category = soup.find('h2', text=re.compile('《.*》')).get_text().strip()
                hgroup = soup.find('hgroup')
                datetime = hgroup.find('div', class_='ndArticle_creat').get_text().strip()
                title = hgroup.find('h1').get_text().strip()
                content = soup.select('.ndArticle_margin > p')
                content = [p.get_text().strip() for p in content]
                content = '\r\n'.join(content)
                view = hgroup.find('div', class_='ndArticle_view')
                view = view.get_text().strip() if view else 0

                time.sleep(0.5)  # 間格時間,防止對網站query過快

            except Exception as e:
                print(e)
                print(url)
                return False

        return self.DATATUPLE(category, datetime, title, content, url, view)


if __name__ == '__main__':
    crawler = AppleCrawler()

    start_time = time.time()
    article_url = crawler.get_url(maxpage=1)
    print('"get_url" cost time:', time.time()-start_time)

    # 解析文章內容(category,title,subtitle,content)
    start_time = time.time()
    articles = []
    for url in article_url:
        art = crawler.parser(url)
        if art:
            print(art)
            articles.append(art)
    print('"parser" cost time:', time.time() - start_time)





