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
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.select import Select


# リンク一覧の取得に関する関数 -------------------------------

# aタグから詳細ページへのリンクkeyを取得
def extract_key_to_link(a_tag_set: set):
    return "key"

# keyとmergeして詳細ページへのリンクを作成
def join_key_with_baselink(key: str):
    base_link = 'https://www.wsl.waseda.jp/syllabus/JAA104.php?pLng=jp&'
    link = base_link + key

    return link

# 10件の一覧ページからリンクを取得
def fetch_a_tags():
    a_tag_set: set = set()
    driver.implicitly_wait(1)

    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find('table', class_ = 'ct-vh')
    tr = table.find_all('tr')

    # aタグからkeyを取得
    for elem in tr:
        a = elem.find('a')
        a_tag_set.add(a)

    return a_tag_set

# 表示されているページにおける詳細ページへのリンクを一覧に追加
def add_to_link_set(link_set: set):
    a_tag_set: set = fetch_a_tags()

    for a_tag in a_tag_set:
        key: str = extract_key_to_link(a_tag)
        link: str = join_key_with_baselink(key)
        link_set.add(link)

    return link_set
# --------------------------------------------------------
# リンクに飛んで詳細ページの情報を取得する関数 ------------------
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
            for tr in tr_list:
                # keyはcol_nameにする以外いらないかも
                keys = [th.get_text() for th in tr.find_all('th')]

                # 成績評価のところだけ違うのでそこで詰まるかも
                # 分岐する必要あると思う
                vals = [td.get_text() for td in tr.find_all('td').get_text()]

                key_list += keys
                val_list += vals

        all_class_info_key.append(key_list)
        all_class_info_val.append(val_list)

    return all_class_info_val

def class_info_to_csv(class_info: list):
    with open('data/class.csv', 'w') as f:
        writer = csv.writer()
        writer.writerows(class_info)
    return

def main():
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')

    driver = webdriver.Remote(
        command_executor=os.environ["SELENIUM_URL"],
        options=options
    )

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

        link_set = add_to_link_set()

        # 表示されているページの詳細リンクを作成したらページ遷移
        # 次へがなかったら最後のページまで行っているので、
        # continueして次の曜日へ
        try: 
            driver.find_element_by_xpath("//table[@class='t-btn']").find_element_by_xpath("//*[text()=\"次へ>\"]").click()
            print('Successfully gone to next page...')
        except Exception as e:
            print(e)
            print('Finish fetching class info of week: ' + week)
            continue

    # --------------------------------------------------------
    # リンク一覧に飛んで詳細情報を取得 ----------------------------
    print('Finish fetching all class info and start fetching details...')

    class_info = fetch_class_info(link_set)
    class_info_to_csv(class_info)

    print('Successfully fetched class info and save to csv!')

    driver.quit()

if __name__ == '__main__':
    main()