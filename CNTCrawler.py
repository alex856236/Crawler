# ==============================================

# 中國時報爬蟲
# 使用BeautifulSoup4解析文件內容
# by Lelingyi


# ==============================================

import requests
import urllib.parse
import time
from collections import namedtuple
from bs4 import BeautifulSoup as btfs


class CNTCrawler():

    BASIC_URL = 'https://www.chinatimes.com/realtimenews/'
    DATATUPLE = namedtuple('Article', ['category', 'datetime', 'title', 'content', 'author', 'url'])

    def __init__(self):
        pass

    # --取得新聞鏈結
    def get_url(self, maxpage=100):
        url = []  # 新聞鏈結
        for page in range(1, maxpage+1):
            req = requests.get(self.BASIC_URL, params={'page': page})  # 連接網站
            if req.status_code == 200:  # 確認網站正確連接
                soup = btfs(req.content, 'html.parser')  # 網站原始碼

                # 下一頁不能按表示最後一頁
                last_page_btn = soup.find('li', text='下一頁')
                if last_page_btn.has_attr('class') and 'disabled' in last_page_btn['class']:
                    break

                # 該頁所有新聞鏈結
                for a in soup.select('.listRight > ul > li > h2 > a'):
                    url.append(urllib.parse.urljoin(self.BASIC_URL, a['href']))

                time.sleep(1)  # 間格時間,防止對網站query過快
        return url

    # --解析頁面
    def parser(self, url):
        req = requests.get(url)
        if req.status_code == 200:  # 確認網站正確連接
            soup = btfs(req.content, 'html.parser')  # 網站原始碼

            # --開始解析
            try:
                category = soup.find('meta', {'name': 'section'})['content']
                datetime = soup.find('time').get_text().strip()
                title = soup.find('meta', {'property': 'og:title'})['content']
                paragraphs = soup.select('article > p')
                paragraphs = [p.get_text().strip() for p in paragraphs]
                content = '\r\n'.join(paragraphs)
                author = soup.find('a', {'rel': 'author'})
                author = author.get_text().strip() if author else ''
            except Exception as e:
                print('something wrong in', url)
                print('Error:', e)
                return False

            time.sleep(1)  # 間格時間,防止對網站query過快
            return self.DATATUPLE(category, datetime, title, content, author, url)
        else:
            return False


if __name__ == '__main__':
    crawler = CNTCrawler()

    start_time = time.time()
    article_url = crawler.get_url(maxpage=1)
    print('"get_url" cost time:', time.time() - start_time)

    # 解析文章內容(category,title,subtitle,content,url)
    start_time = time.time()
    articles = []
    for url in article_url:
        art = crawler.parser(url)
        if art:
            articles.append(art)
    print('"parser" cost time:', time.time() - start_time)

    # save file
    import pandas as pd
    data = pd.DataFrame(articles)

    # encoding=utf-8-sig: 包含BOM檔首
    data.to_csv('./CNT.csv', encoding='utf-8-sig')

