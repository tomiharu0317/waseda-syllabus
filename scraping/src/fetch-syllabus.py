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

def clear_td(val: str):
    val = val.replace('<td>', '')
    val = val[::-1]
    # </td>の逆
    val = val.replace('>dt/<', '')
    val = val[::-1]

    return val

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

def fetch_class_info(link_set: set):

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

def class_info_to_csv(class_info_key: list, all_class_info_val: list):
    with open('../data/class.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(class_info_key)
        writer.writerows(all_class_info_val)

def class_link_to_csv(link_set: set):
    link_list = list(link_set)

    header = ['link']
    n = len(link_list)
    for i in range(n):
        link_list[i] = [link_list[i]]

    with open('../data/all_class_link.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)
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
    
    class_info_to_csv(class_info_key, all_class_info_val)
    print('Successfully fetched class info and save to csv!')

    driver.quit()

if __name__ == '__main__':
    main()