# ===============================================

# 蘋果即時新聞爬蟲
# 以使用eautifulSoup4解析文件內容
# by Lelingyi

# ===============================================

import requests
import time
import json
from collections import namedtuple
from bs4 import BeautifulSoup as btfs

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

                # 該頁所有鏈結
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
        req = requests.get(url)
        if req.status_code == 200:
            # 開始解析
            try:
                soup = btfs(req.content, 'html.parser')  # 網頁原始碼
                meta = soup.find('script', {'type': 'application/ld+json'}).get_text().strip()
                meta = json.loads(meta)

                category = meta['articleSection'][3:]
                hgroup = soup.find('hgroup')
                datetime = hgroup.find('div', class_='ndArticle_creat').get_text().strip()[5:]
                title = hgroup.find('h1').get_text().strip()

                content = soup.select('.ndArticle_margin > p')[0]
                # 去除span、a(不必要的內容)
                for span in content.select('span'):
                    span.decompose()
                for a in content.select('a'):
                    a.decompose()
                content = content.get_text().strip()

                view = hgroup.find('div', class_='ndArticle_view')
                view = view.get_text().strip() if view else 0

                time.sleep(0.5)  # 間格時間,防止對網站query過快

                return self.DATATUPLE(category, datetime, title, content, url, view)

            except Exception as e:
                print(e)
                print(url)
                return False
        else:
            return False


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





