# README----------------------------------

# Seleniumでやること
# 月-無を選択して検索
# ページ遷移

# BeautifulSoup4でやること
# 詳細ページへのkeyを取得
# 詳細ページの内容取得
# ----------------------------------------

from curses import keyname
from lib2to3.pgen2 import driver
import os
import csv
import time
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

# リンク一覧の取得に関する関数 -------------------------------
# aタグから詳細ページへのリンクkeyを取得
def extract_key_to_link(a_tag):

    # ex of a tag
    # <a href="#" onclick="post_submit('JAA104DtlSubCon', '1200000110182022120000011012')">導入演習（選択）　１８</a>
    # if a tag were the one above, the key is 1200000110182022120000011012
    split_str = '<a href="#" onclick="post_submit(' + "'JAA104DtlSubCon', '"
    key = str(a_tag).split(split_str)[1].split("')" + '">')[0]

    # print('key: ', key)
    return key

# keyとmergeして詳細ページへのリンクを作成
def join_key_with_baselink(key: str):
    base_link = 'https://www.wsl.waseda.jp/syllabus/JAA104.php?pKey='
    link = base_link + key + '&pLng=jp'

    # print('link: ', link)
    # print('\n')

    return link

# 10件の一覧ページからリンクを取得
def fetch_a_tags():
    a_tag_set: set = set()
    driver.implicitly_wait(3)

    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find('table', class_ = 'ct-vh')
    # index0にaタグを含まない列名のtrが含まれるので取り除く
    tr = table.find_all('tr')[1:]

    # aタグからkeyを取得
    for elem in tr:
        a = elem.find('a')
        a_tag_set.add(a)

    print('a_tag_set:\n', a_tag_set)

    return a_tag_set

# 表示されているページにおける詳細ページへのリンク10件を一覧に追加
def add_to_link_set(link_set: set):
    a_tag_set: set = fetch_a_tags()

    for a_tag in a_tag_set:
        key: str = extract_key_to_link(a_tag)
        link: str = join_key_with_baselink(key)
        link_set.add(link)

    # print('link_set:\n', link_set)

    return link_set
# --------------------------------------------------------
# リンクに飛んで詳細ページの情報を取得する関数 ------------------
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
        # シラバス情報の取得は断念
        table = soup.find('table', class_= 'ct-common ct-sirabasu')
        tr_list: list = table.find_all('tr')

        # 初回のみkeyを取得
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

def class_info_to_csv(class_info: list):
    with open('data/class.csv', 'w') as f:
        writer = csv.writer()
        writer.writerows(class_info)

def class_link_to_csv(link_set: set):
    link_list = list(link_set)

    with open('data/link.csv', 'w') as f:
        writer = csv.writer()
        writer.writerows(link_list)

def main():
    # 全授業の詳細ページへのリンクを取得 ---------------------------
    # --------------------------------------------------------
    print('Start fetching...')

    link_set: set = set()
    week_list: list = ['月', '火', '水', '木', '金', '土', '日', '無']
    TOP_URL: str = 'https://www.wsl.waseda.jp/syllabus/JAA101.php?pLng=jp'

    for week in week_list:
        driver.get(TOP_URL)

        # 曜日を条件として選択して授業を検索
        youbi = driver.find_element_by_name('p_youbi')
        select_youbi = Select(youbi)
        select_youbi.select_by_visible_text(week)
        driver.find_element_by_xpath("//input[@value=' 検  索 ']").click()

        print('week:' + week + ' now fetching...')
        pagecount = 0

        # ページに表示されている10件のリンクを追加
        while True: 
            pagecount += 1
            print('\n')
            print('現在のページ数: ', pagecount)

            link_set = add_to_link_set(link_set)

            # 表示されているページの詳細リンクを作成したらページ遷移
            # 次へがなかったら最後のページまで行っているので、
            # continueして次の曜日へ
            try: 
                driver.find_element_by_xpath("//table[@class='t-btn']").find_element_by_xpath("//*[text()=\"次へ>\"]").click()
                time.sleep(1)
                print('Successfully went to next page...')
            except Exception as e:
                print(e)
                print('Finish fetching class info of week: ' + week)
                break

    # --------------------------------------------------------
    # リンク一覧に飛んで詳細情報を取得 ----------------------------
    print('Finish fetching all links and start fetching details...')
    class_link_to_csv(link_set)

    class_info_key, all_class_info_val = fetch_class_info(link_set)
    
    # FIXME: csvへの保存の仕方
    # class_info_to_csv(class_info)

    print('Successfully fetched class info and save to csv!')

    driver.quit()

if __name__ == '__main__':
    main()