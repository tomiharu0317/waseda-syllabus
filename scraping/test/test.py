from cgi import test
import os
import csv
import pandas as pd
from pickle import FALSE, TRUE
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

def extract_key_from_table(tr_list: list):
    class_info_key: list = []
    
    for tr in tr_list:
        keys = [th.get_text() for th in tr.find_all('th')]
        class_info_key += keys
        
    # 授業方法区分 と コースコードの間に 空白の要素があるので取り除く
    class_info_key.pop(14)

    # オープン科目の情報を追加 len() = 21なら
    # オープン科目のスペースの空白文字があるので変換
    if len(class_info_key) == 21:
        class_info_key[-1] = 'オープン科目'
    else:
        class_info_key.append('オープン科目')

    print(class_info_key)
    print('len(class_info_key)', len(class_info_key))

    return class_info_key

def extract_val_from_table(tr_list: list):
    val_list: list = []

    for tr in tr_list:
        vals = [td.get_text() for td in tr.find_all('td')]
        val_list += vals

    # オープン科目の情報があればTrueになければFalseとして追加
    if val_list[-1] == 'オープン科目':
        val_list[-1] = True
    else:
        val_list.append(False)

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

        # key の取得は初回だけにするので first_time = FALSE で
        # 最初に TRUE に変換し以降は if で 処理
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

def clear_td(val: str):
    val = val.replace('<td>', '')
    val = val[::-1]
    # </td>の逆
    val = val.replace('>dt/<', '')
    val = val[::-1]

    return val

def extract_html_from_table(tr_list: list):
    syllabus_info_dict: dict = {
        '副題': None,
        '授業概要': None,
        '授業の到達目標': None,
        '事前・事後学習の内容': None,
        '授業計画': None,
        '教科書': None,
        '参考文献': None,
        '成績評価方法': None,
        '備考・関連URL': None
    }

    for tr in tr_list:
        key_val_list = tr.contents
        key_val_list = [elem for elem in key_val_list if elem != '\n']

        # syllabus_info_dictのkeyを取得
        try:
            key = key_val_list[0].get_text()

            if key in syllabus_info_dict:
                val = str(key_val_list[1])
                #  先頭の<td></td>を削除
                val = clear_td(val)                
                syllabus_info_dict[key] = val
        except Exception as e:
            print(e)
            continue

    return list(syllabus_info_dict.values())

def syllabus_info_key():
    syllabus_info_key_list: list = [
        '副題', '授業概要', '授業の到達目標', '事前・事後学習の内容',
        '授業計画', '教科書', '参考文献', '成績評価方法', '備考・関連URL', '元シラバスリンク']
    return syllabus_info_key_list

def fetch_class(link_set: set):

    class_info_key: list = []
    all_class_info_val: list = []
    first_time: bool = False

    for link in link_set:
        html = fetch_pagesource(link)
        soup = BeautifulSoup(html, 'html.parser')
        # 改行コードを削除
        [tag.extract() for tag in soup(string='n')]
        
        table_list: list = soup.find_all('table', class_= 'ct-common ct-sirabasu')
        val_list: list = []

        # table1:授業情報 table2:シラバス情報
        for id in range(2):
            table = table_list[id]
            if id == 0:
                tr_list: list = table.find_all('tr')
                if first_time == False: 
                    first_time = True
                    class_info_key = extract_key_from_table(tr_list) + syllabus_info_key()

                val_list = extract_val_from_table(tr_list)
            # シラバス情報のtableは自由度が高く、単純に文章を取得できないので
            # 子要素のtdタグを取得し、html -> markdownにすることで対処する
            else:
                tbody = table_list[id].contents
                # 改行コードが入っているので削除
                tbody = [tbody for tbody in tbody if tbody != '\n'][0]

                # 1つ階層が下の'tr'タグを取得
                tr_list: list = tbody.contents
                tr_list = [tr for tr in tr_list if tr != '\n']
                # table1の情報と結合
                val_list += extract_html_from_table(tr_list)
                val_list.append(link)

        all_class_info_val.append(val_list)

    return class_info_key, all_class_info_val

def make_link_set():
    link_set: set = set()
    link_set.add('https://www.wsl.waseda.jp/syllabus/JAA104.php?pKey=3332000502012022333200050233&pLng=jp')
    link_set.add('https://www.wsl.waseda.jp/syllabus/JAA104.php?pKey=1200007D810120221200007D8112&pLng=jp')
    link_set.add('https://www.wsl.waseda.jp/syllabus/JAA104.php?pKey=1200000050012022120000005012&pLng=jp')
    
    return link_set

def test_fetch_class_info():
    link_set = make_link_set()
    
    class_info_key, all_class_info_val = fetch_class_info(link_set)

def test_class_info_to_csv():
    link_set = make_link_set()
    class_info_key, all_class_info_val = fetch_class(link_set)

    with open('../data/class.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(class_info_key)
        writer.writerows(all_class_info_val)

    # print('class_info_key:\n', class_info_key)
    # print('all_class_info_val:\n', all_class_info_val)

def test_class_link_to_csv():
    link_set = make_link_set()
    link_list = list(link_set)

    header = ['link']
    n = len(link_list)
    for i in range(n):
        link_list[i] = [link_list[i]]

    with open('../data/link.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(link_list)

def test_fetch_class():
    link_set = make_link_set()
    fetch_class(link_set)

def test_clear_td():
    string = '<td>aaa</td>'
    print(clear_td(string))

def test_link_set_from_csv():
    link_df = pd.read_csv('../data/all_class_link.csv')
    link_list: list = link_df.values.tolist()
    # 1次元に変換
    link_list = [link[0] for link in link_list]
    link_set = set(link_list)

    return link_set

def test_fetch_last_page_num():

    start()
    driver.implicitly_wait(3)

    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    btn_table = soup.find('div', class_ = 'l-btn-c')
    a_list = btn_table.find_all('a')
    last_page_num: int = 1

    for a in a_list:
        text = a.get_text()
        try:
            last_page_num = int(text)
        except ValueError as e:
            print(e)
            print(text)
            pass

    print('last_page_num', last_page_num)
    driver.quit()

    return last_page_num

def test():
    # test_extract_key_to_link()
    # test_fetch_class_info()
    # test_class_link_to_csv()
    # test_class_info_to_csv()
    # test_fetch_class()
    # test_clear_td()
    test_link_set_from_csv()
    # test_fetch_last_page_num()

if __name__ == '__main__':
    test()

# テストすること
# 1. その曜日の最後のページ番号の取得
# 2. 次のページボタンをクリック
# 3. csvからlinkを取得しsetにする