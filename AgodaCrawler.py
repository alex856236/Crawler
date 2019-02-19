import time
import urllib
from bs4 import BeautifulSoup as btfs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASIC_URL = 'https://www.agoda.com/'
URL = 'https://www.agoda.com/zh-tw/pages/agoda/default/DestinationSearchResult.aspx'

driver = webdriver.Chrome()

parameter = {'city': 4951,  # 台北4951
             # 'area':80303, #板橋
             'checkIn': '2019-02-20',  # 入住時間
             'checkOut': '2019-02-22',  # 離開時間
             'rooms' : 1,  # 客房數
             'adults': 2,  # 大人人數
             'children': 0,  # 小孩人數
            }


def get_tag(parent, tag):
    try:
        element = parent.find_element_by_tag_name(tag)
    except:
        return None
    return element


def get_class(parent, class_name):
    try:
        element = parent.find_element_by_class_name(class_name)
    except:
        return None
    return element


def get_css(parent, css_selector):
    try:
        element = parent.find_element_by_css_selector(css_selector)
    except:
        return None
    return element


correct_URL = URL + '?' + '&'.join(['%s=%s' % (key, value) for (key, value) in parameter.items()])
driver.get(correct_URL)
hotel_blocks = driver.find_elements_by_class_name('PropertyCardItem')

for block in hotel_blocks:
    driver.execute_script('arguments[0].scrollIntoView();', block)

    hotel_url = get_tag(block, 'a')
    hotel_url = hotel_url.get_attribute('href') if hotel_url else hotel_url

    hotel_name = get_class(block, 'hotel-name')
    hotel_name = hotel_name.text if hotel_name else hotel_name

    hotel_star = get_css(block, 'i[data-selenium="hotel-star-rating"]')
    hotel_star = hotel_star.get_attribute('title') if hotel_star else hotel_star

    hotel_location = get_class(block, 'areacity-name-text')
    hotel_location = hotel_location.text if hotel_location else hotel_location

    hotel_score = get_class(block, 'ReviewScore-Number')
    hotel_score = hotel_score.text if hotel_score else hotel_score

    print((hotel_name, hotel_star, hotel_location, hotel_score, hotel_url))
    time.sleep(1)
