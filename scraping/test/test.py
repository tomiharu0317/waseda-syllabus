from cgi import test
import os
import csv
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

    # FIXME
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

def test():
    test_extract_key_to_link()

if __name__ == '__main__':
    test()