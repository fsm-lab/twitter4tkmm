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
ACOUNT_ID , ACOUNT_PASS = "RnPuseF77mJZpVO","twitternopas1"
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




def get_tweet(twitter_id,search_type,follow_count,follower_count):
     
    url = 'https://twitter.com/' + twitter_id +"/"+ search_type

    id_list = []
    
    time.sleep(5)
    driver.get(url)


    for i in range(SCROLL_COUNT):
        
        id_list = get_user_id(id_list)
        print(len(id_list))
        scroll_to_elem()

        # ○秒間待つ（サイトに負荷を与えないと同時にコンテンツの読み込み待ち）
        time.sleep(SCROLL_WAIT_TIME) 

        #id_listが垢のfollower数と一緒なら終了判定
        if follower_count-15 < len(id_list) < follower_count+15:
            break


    return id_list


def count_follow_id(twitter_id):

    url = 'https://twitter.com/' + twitter_id
    
    driver.get(url)

    #読み込むまでを試したがダメだったのでtime.sleep推奨
    time.sleep(3)

    #鍵垢判定　もし鍵垢ならフォロワーを読めないのでここで判定。鍵垢なら空を返す
    try:

        follower_count = driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[5]/div[2]/a/span[1]').text
        follow_count = driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/div/div[5]/div[1]/a/span[1]').text
        # print(follower_count,follow_count)
        # print(type(follower_count),type(follow_count))

        return translator(follow_count) ,translator(follower_count)
    
    except NoSuchElementException:
        return "",""


#万や億などの表記を日本語に直す　1,000などを1000に直す
def translator(target):
    target = target.replace(',', '')
    replaceTable = str.maketrans({'億':'*100000000','万':'*10000'})
    text = str(target)

    result = eval(text.translate(replaceTable))
    
    return result


def login_twitter(account, password, driver):
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
     

def get_user_id(id_list):
    # ここでスリープを入れないと読み込む前に検索してエラー出る
    time.sleep(3) #読み込むまでを試したがダメだったのでtime.sleep推奨

    elems_article = driver.find_elements(By.XPATH,"//div[@data-testid='cellInnerDiv']")


    for elem_article in elems_article:
        html_text = elem_article.get_attribute('innerHTML')

        user_id = split_userID(html_text) #userIDはlist
    
        if not user_id: #空判定 なぜか空のlistが出来たため応急的
            break
        
        else:
            if user_id[-1] not in id_list:
                # twitter_id情報取得                   
                id_list.append(user_id[-1])
                # print(user_id)
    

    return id_list #,tweet_list


def split_userID(html_text):
    # 特定の文字列を切り出したい。(ユーザーID)　@0000では複数あるので「>@　~userID~　<」までを指定して切り出したい   ex) r-qvutc0">@shunno0529</span></div></div></a></div>    
    p = r'>@(\w+)</span>'
    m = re.findall(p, html_text)
    usreID = m

    return usreID











def GET_FOLLOWS(target_csv_name,search_type):

    # ファイルを開く
    # file_name = "data\\" + target_csv_name + ".csv"
    file_name = "data\\"+ target_csv_name + ".csv"
    f = open(file_name, 'r')
    id_list = csv.reader(f)
    # print(id_list)
    # print(type(id_list))

    #　ヘッドレスモードでブラウザを起動
    options = Options()
    options.add_argument('--headless')
    login_twitter(ACOUNT_ID , ACOUNT_PASS , driver)

    # global変数へ代入できるように
    global TWITTER_ID
    for id in id_list:
        # print(id[0])
        TWITTER_ID = id[0]
        follow_count,follower_count = count_follow_id(TWITTER_ID)

        if follow_count and follower_count:
            # tweet情報をlist型で取得
            id_list = get_tweet(TWITTER_ID,search_type,follow_count,follower_count)

            # ファイル名を決定
            file_path = "data\\" + TWITTER_ID + ".csv"
            # データフレームに変換
            df = pd.DataFrame(id_list)
            # csvとして保存
            df.to_csv(file_path,mode='w',header=False, index=False)
        
        else:
            continue

    # ブラウザ停止
    driver.quit()






if __name__ == "__main__":

    csv_name = "test"
    search_type = "followers"
    GET_FOLLOWS(csv_name,search_type)





import pickle