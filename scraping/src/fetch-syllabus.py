# README----------------------------------

# Seleniumでやること
# 月-無を選択して検索
# ページ遷移

# BeautifulSoup4でやること
# 詳細ページへのkeyを取得
# 詳細ページの内容取得
# ----------------------------------------

import os
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


def main():
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')

    driver = webdriver.Remote(
        command_executor=os.environ["SELENIUM_URL"],
        options=options
    )

    # 全授業の詳細ページへのリンクを取得 ---------------------------
    # --------------------------------------------------------
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

        link_set = add_to_link_set()

        # 表示されているページの詳細リンクを作成したらページ遷移
        # 次へがなかったら最後のページまで行っているので、
        # continueして次の曜日へ
        try: 
            driver.find_element_by_xpath("//table[@class='t-btn']").find_element_by_xpath("//*[text()=\"次へ>\"]").click()
        except Exception as e:
            print(e)
            continue

    # --------------------------------------------------------
    # リンク一覧に飛んで詳細情報を取得 ----------------------------
    # TODO: どのような形で詳細情報を受け取るか
    # 後で整形しやすい形で（できればtidyに）
    for link in link_set:
        return

    driver.quit()

if __name__ == '__main__':
    main()