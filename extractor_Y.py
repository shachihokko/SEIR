import sys
sys.path.append("lib.bs4")
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import chromedriver_binary
import pandas as pd
import os
from tqdm import tqdm


dir_org = os.path.dirname(os.path.abspath(__file__))
os.chdir(dir_org) #作業フォルダの移動

###############################################################
#---------------------- setting ------------------------------
###############################################################

### ログイン用の情報
URL = "https://coronavirus.smartnews.com/jp/"

### アクセス確認のための最大待機時間
seconds = 20


###############################################################
#---------------------- xpath_setting -------------------------
###############################################################

graph_xpath = "/html/body/div/div/section[2]/section[2]/div/div[1]/div[2]/div[1]/canvas"

button_xpath = "/html/body/div/div/section[2]/section[2]/div/div[2]/button[2]"

info_xpath = "/html/body/div/div/section[2]/section[2]/div/div[1]/div[2]/div[2]"

date_xpath = info_xpath + "/text()[1]"


###############################################################
#---------------------- function ------------------------------
###############################################################

# driver上でxpathが選択できるまで最大sec秒待つ
def wait_loading(driver, sec, xpath):
  WebDriverWait(driver, sec).until(EC.presence_of_element_located((By.XPATH, xpath)))

#ボタンの出現を確認後にクリック
def wait_and_click(driver, sec, xpath):
  wait_loading(driver, sec, xpath)
  driver.find_element_by_xpath(xpath).click()


###############################################################
#---------------------- main routine --------------------------
###############################################################

### ブラウザの立ち上げ
options = Options()
options.set_headless(True) # Headlessモードを有効
driver = webdriver.Chrome(chrome_options=options)
driver.set_window_size('1200', '1000') #ブラウザを適当に大きく
driver.get(URL) #ブラウザでアクセスする

wait_loading(driver, seconds, graph_xpath)
wait_and_click(driver, seconds, button_xpath)
graph_position = driver.find_element_by_xpath(graph_xpath) # チャートの要素を取得
actions = ActionChains(driver) #マウスの動きの記述スタート
actions.move_to_element(graph_position) #チャートの中心にマウスを移動
graph_width = graph_position.rect["width"] #チャートの横幅
actions.move_by_offset(-(graph_width//2),0) #チャートの左端へ移動
actions.perform() # 記述した動きを実行

record = {}
for i in tqdm(range(int(graph_width))):
  wait_loading(driver, seconds, info_xpath)
  info = driver.find_elements_by_xpath(info_xpath)[0].text.split()
  data = [info[2], info[4], info[6]]
  record[info[0]] = data
  actions = ActionChains(driver)
  actions.move_by_offset(1,0) # 5pixelずつ移動
  actions.perform()
df = pd.DataFrame(record).T.sort_index()
df.columns = ["感染者数", "回復者数", "死亡者数"]
df.to_csv("tmp.csv", encoding="cp932")
