from cgi import test
import os
import csv
from pickle import FALSE, TRUE
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

# FIXME
# 1. シラバス情報は取らないので find_all -> find('table', class_= 'ct-common ct-sirabasu')
# 2. key の取得は初回だけにするので first_time = FALSE で 最初に TRUE に変換し以降は if で 処理
# 3. key_list において 授業方法区分 と コースコードの間に 空白の要素があるので取り除く 順番は決まっているのでindexで指定できる
def extract_key_from_table(tr_list: list):
    class_info_key: list = []
    
    for tr in tr_list:
        keys = [th.get_text() for th in tr.find_all('th')]
        class_info_key += keys
        
    # 授業方法区分 と コースコードの間に 空白の要素があるので取り除く
    class_info_key.pop(14)

    return class_info_key

def extract_val_from_table(tr_list: list):
    val_list: list = []

    for tr in tr_list:
        vals = [td.get_text() for td in tr.find_all('td')]
        val_list += vals

    return val_list

def fetch_class_info(link_set: set):

    class_info_key: list = []
    all_class_info_val: list = []
    first_time: bool = False

    for link in link_set:

        html = fetch_pagesource(link)
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', class_= 'ct-common ct-sirabasu')
        tr_list: list = table.find_all('tr')

        if first_time == False: 
            first_time = True
            class_info_key = extract_key_from_table(tr_list)
            class_info_key.append('元シラバスリンク')
            print('class_info_key:\n', class_info_key)
            print('len(class_info_key):', len(class_info_key))
        
        val_list = extract_val_from_table(tr_list)
        val_list.append(link)
        print('val_list:\n', val_list)
        print('len(val_list):', len(val_list))
    
        all_class_info_val.append(val_list)

    return class_info_key, all_class_info_val

def make_link_set():
    link_set: set = set()
    link_set.add('https://www.wsl.waseda.jp/syllabus/JAA104.php?pKey=3332000502012022333200050233&pLng=jp')
    link_set.add('https://www.wsl.waseda.jp/syllabus/JAA104.php?pKey=1200007D810120221200007D8112&pLng=jp')
    
    return link_set

def test_fetch_class_info():
    link_set = make_link_set()
    
    class_info_key, all_class_info_val = fetch_class_info(link_set)

def test_class_info_to_csv():
    link_set = make_link_set()
    class_info_key, all_class_info_val = fetch_class_info(link_set)

    with open('csv/class.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(class_info_key)
        writer.writerows(all_class_info_val)

    # print('class_info_key:\n', class_info_key)
    # print('all_class_info_val:\n', all_class_info_val)

    return

def test_class_link_to_csv():
    link_set = make_link_set()
    link_list = list(link_set)

    header = ['link']
    n = len(link_list)
    for i in range(n):
        link_list[i] = [link_list[i]]

    with open('csv/link.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(link_list)

def test():
    # test_extract_key_to_link()
    # test_fetch_class_info()
    # test_class_link_to_csv()
    test_class_info_to_csv()

if __name__ == '__main__':
    test()