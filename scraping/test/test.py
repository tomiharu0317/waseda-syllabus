from cgi import test
import os
import csv
import pytest
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.select import Select


options = webdriver.FirefoxOptions()
options.add_argument('--headless')

driver = webdriver.Remote(
    command_executor=os.environ["SELENIUM_URL"],
    options=options
)

def start():
    print('Start fetching...')
    
    week = '月'
    TOP_URL: str = 'https://www.wsl.waseda.jp/syllabus/JAA101.php?pLng=jp'

    driver.get(TOP_URL)

    youbi = driver.find_element_by_name('p_youbi')
    select_youbi = Select(youbi)
    select_youbi.select_by_visible_text(week)
    driver.find_element_by_xpath("//input[@value=' 検  索 ']").click()

def fetch_a_tags():
    a_tag_set: set = set()
    driver.implicitly_wait(1)

    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find('table', class_ = 'ct-vh')

    # aタグを含まないタイトルtrを含み、len = 11となる
    # そのため最初の要素を消してからやる
    tr = table.find_all('tr')[1:]

    # aタグからkeyを取得
    for elem in tr:
        a = elem.find('a')
        a_tag_set.add(a)
        # a_tag_set.append(a)

    # print('a_tag_set:\n', a_tag_set)

    return a_tag_set

def extract_key_to_link(a_tag):

    # ex of a tag
    # <a href="#" onclick="post_submit('JAA104DtlSubCon', '1200000110182022120000011012')">導入演習（選択）　１８</a>
    # if a tag were the one above, the key is 1200000110182022120000011012
    split_str = '<a href="#" onclick="post_submit(' + "'JAA104DtlSubCon', '"
    # print('before:\n',  a_tag)
    # print('before type:\n', type(a_tag))
    # print('------------------------------------')

    key = str(a_tag)
    # print('after:\n',  key)
    # print('after:\n', type(key))

    li = key.split(split_str)[1].split("')" + '">')
    # print('\n\n')
    # print(li)
    key = li[0]

    return key

def test_extract_key_to_link():
    start()

    a_tag_set = list(fetch_a_tags())
    print(len(a_tag_set))

    for a_tag in a_tag_set:
        # print(a_tag, '\n')
        key =  extract_key_to_link(a_tag)

        print(key)

    driver.quit()

def fetch_pagesource(link: str):

    driver.get(link)
    driver.implicitly_wait(1)
    html = driver.page_source.encode('utf-8')

    return html

def fetch_class_info(link_set: set):

    all_class_info_key: list = []
    all_class_info_val: list = []

    for link in link_set:

        html = fetch_pagesource(link)
        soup = BeautifulSoup(html, 'html.parser')
        
        # pandasで以下のtidyな形で取得
        # key, key, key
        # value, value, value
        key_list: list = []
        val_list: list = []
        tables = soup.find_all('table', class_= 'ct-common ct-sirabasu')

        for table in tables:
            tr_list: list = table.find_all('tr')
            # print(tr_list)
            for tr in tr_list:
                # keyはcol_nameにする以外いらないかも
                keys = [th.get_text() for th in tr.find_all('th')]

                # print(keys)

                # 成績評価のところだけ違うのでそこで詰まるかも
                # 分岐する必要あると思う
                vals = [td.get_text() for td in tr.find_all('td')]

                # print(vals)

                key_list += keys
                val_list += vals

        print(val_list)

        all_class_info_key.append(key_list)
        all_class_info_val.append(val_list)

    return all_class_info_val

# FIXME: add some links
def test_fetch_class_info():
    link_set: set = set()
    link_set.add('https://www.wsl.waseda.jp/syllabus/JAA104.php?pKey=3332000502012022333200050233&pLng=jp')
    # link_set.add()
    
    all_class_info = fetch_class_info(link_set)

    return

def test():
    # test_extract_key_to_link()
    test_fetch_class_info()

if __name__ == '__main__':
    test()