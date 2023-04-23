import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import pandas as pd
import re
 
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import csv
from selenium.common.exceptions import NoSuchElementException

# -----global_variable-----
SCROLL_COUNT = 100000000000000000

SCROLL_WAIT_TIME = 1
ACOUNT_ID , ACOUNT_PASS = "FsmlabT", "barabara0811"
TWITTER_ID = ""
# -------------------------



# -----headers-------------
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
    } # ヘッダーとは何なのかわからん？？？
# -------------------------



# ---------システムに接続されたデバイスが機能していません。を消すためにある----------------
ChromeOptions = webdriver.ChromeOptions()
ChromeOptions.add_experimental_option('excludeSwitches', ['enable-logging'])
# -------------------------



# -------chromeドライバーのダウンロード------------------
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
# -------------------------


def get_follows(target_name, search_type):
    user_count = count_follow_id(target_name)[search_type]
    print(f"{search_type}数：{user_count}")
    url = f"https://twitter.com/{target_name}/{search_type}"
    print(url)
    time.sleep(5)
    driver.get(url)
    id_set = set()
    id_counts = 0
    for i in range(SCROLL_COUNT):     
        print(len(id_set))
        ids = get_user_id()
        id_set |= ids
        print(len(id_set), id_set)
        scroll_to_elem()
        # x秒間待つ（サイトに負荷を与えないと同時にコンテンツの読み込み待ち）
        time.sleep(SCROLL_WAIT_TIME) 
        #id_listが垢のfollower数と一緒なら終了判定
        if user_count-5 < len(id_set) < user_count+5:
            break
        if len(id_set) == id_counts:
            btn = get_reload_button()
            print(btn)
            print("読み込み制限のため，15+1分スリープします")
            time.sleep(960)
            print("読み込み再開")
            btn.click()

        id_counts = len(id_set)

    file_path = f"{search_type}/{target_name}.txt"
    wfo = open(file_path, "w")
    for follow_name in id_set: wfo.write(f"{follow_name}\n")
    wfo.close()


def count_follow_id(twitter_id):
    url = 'https://twitter.com/' + twitter_id
    driver.get(url)
    #読み込むまでを試したがダメだったのでtime.sleep推奨
    time.sleep(3)
    #鍵垢判定　もし鍵垢ならフォロワーを読めないのでここで判定。鍵垢なら空を返す
    try:
        follower_count = driver.find_element(By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[5]/div[2]/a/span[1]').text
        followee_count = driver.find_element(By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[5]/div[1]/a/span[1]').text        # print(follower_count,follow_count)
        # print(type(follower_count),type(follow_count))
        return {"following": translator(followee_count), "followers": translator(follower_count)}    
    except NoSuchElementException:
        return {"following": -1, "followers": -1}


#万や億などの表記を日本語に直す　1,000などを1000に直す
def translator(target):
    target = target.replace(',', '')
    replaceTable = str.maketrans({'億':'*100000000','万':'*10000'})
    text = str(target)
    result = eval(text.translate(replaceTable))   
    return result


def login_twitter(account, password):
    # ログインページを開く
    driver.get("https://twitter.com/i/flow/login")
    time.sleep(2)
    # account入力
    element_account = driver.find_element(By.NAME,"text")
    element_account.send_keys(account)
    time.sleep(1.5) 
    # 次へボタンのXPathがこれでしか取れなかった・・・
    # 次へボタンクリック
    element_login = driver.find_element(By.XPATH,'//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div')
    element_login.click()
    time.sleep(1.5) 
    # パスワード入力
    element_pass = driver.find_element(By.NAME,"password")
    element_pass.send_keys(password)
    time.sleep(1.5) 
    # ログインボタンクリック
    element_login = driver.find_element(By.XPATH,'//*[@data-testid="LoginForm_Login_Button"]')
    element_login.click()
    time.sleep(1.5) 


def scroll_to_elem():
    time.sleep(3) #読み込むまでを試したがダメだったのでtime.sleep推奨
    # 最後の要素の一つ前までスクロール
    elems_article = driver.find_elements(By.XPATH,"//div[@data-testid='cellInnerDiv']")
    last_elem = elems_article[-1]
    actions = ActionChains(driver)
    actions.move_to_element(last_elem)
    actions.perform()
     

def get_user_id():
    # ここでスリープを入れないと読み込む前に検索してエラー出る
    time.sleep(3) #読み込むまでを試したがダメだったのでtime.sleep推奨
    elems_article = driver.find_elements(By.XPATH,"//div[@data-testid='cellInnerDiv']")
    ids = set()
    for elem_article in elems_article:
        html_text = elem_article.get_attribute('innerHTML')
        user_id = split_userID(html_text) #userIDはlist
        if not user_id: #空判定 なぜか空のlistが出来たため応急的
            break
        else:
            ids.add(user_id[-1])
                # print(user_id)
    return ids #,tweet_list


def get_reload_button():
    button = driver.find_element(By.CSS_SELECTOR, "#react-root > div > div > div.css-1dbjc4n.r-18u37iz.r-13qz1uu.r-417010 > main > div > div > div > div.css-1dbjc4n.r-14lw9ot.r-jxzhtn.r-1ljd8xs.r-13l2t4g.r-1phboty.r-16y2uox.r-1jgb5lz.r-11wrixw.r-61z16t.r-1ye8kvj.r-13qz1uu.r-184en5c > div > section > div > div > div:nth-child(25) > div > div > div.css-18t94o4.css-1dbjc4n.r-l5o3uw.r-42olwf.r-sdzlij.r-1phboty.r-rs99b7.r-2yi16.r-1qi8awa.r-1ny4l3l.r-ymttw5.r-o7ynqc.r-6416eg.r-lrvibr")
    return button


def split_userID(html_text):
    # 特定の文字列を切り出したい。(ユーザーID)　@0000では複数あるので「>@　~userID~　<」までを指定して切り出したい   ex) r-qvutc0">@shunno0529</span></div></div></a></div>    
    p = r'>@(\w+)</span>'
    m = re.findall(p, html_text)
    usreID = m
    return usreID


def get_already_got_names():
    """
    フォロワー／フォロウィーリストを収集済みのユーザ集合を返す
    ToDo：未実装
    """
    user_names = set()
    return user_names


def main(file_path, search_type):
    #　ヘッドレスモードでブラウザを起動
    options = Options()
    options.add_argument('--headless')
    login_twitter(ACOUNT_ID , ACOUNT_PASS)

    user_names = get_already_got_names()
    rfo = open(file_path, "r")
    for target_name in rfo:
        target_name = target_name.replace("\n", "")
        if target_name in user_names: continue
        get_follows(target_name, search_type)
    rfo.close()
    # ブラウザ停止
    driver.quit()


if __name__ == "__main__":
    # file_path = sys.argv[1] # 対象ユーザ名が書かれたファイルのパス
    file_path = "./origin.txt" # ファイル内の改行コードはLFのみ対応
    search_type = "followers"
    main(file_path, search_type)

