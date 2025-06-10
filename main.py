import requests
import schedule
import time
from flask import Flask, request, redirect
from threading import Thread
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from datetime import datetime, timedelta
import pymysql

CHROME_DRIVER_PATH = "/opt/homebrew/bin/chromedriver" #

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Global variable to store the cookie
cookie_value = 'lgc=; wk_cookie2=167f0c4d672ac968e0a93b99b0d0321b; ' \
'cookie2=16cd3b0638e9816bd345a1feea4ead65; cancelledSubSites=empty; ' \
't=aad3d47a3693faf2be2983e66f9366c7; sn=; _tb_token_=ee85e7738e7a7; ' \
'XSRF-TOKEN=40246523-8598-46b3-8cf4-95ab422f784a; ' \
'__itrace_wid=95ae536e-98c9-4b4d-80b3-e28c2a186e6a; ' \
'cna=VWfNIPe5zgoCASvziD7zfIGi; xlly_s=1; ' \
'cookie3_bak=16cd3b0638e9816bd345a1feea4ead65; login=true; ' \
'env_bak=FM%2BgywHD7Unoz8SbIc%2FnUBfFQSvsP66Kkma08fliLj6Y; ' \
'havana_lgc_exp=1780553644693; cookie3_bak_exp=1749708844693; dnk=tb85338658; ' \
'uc1=cookie21=Vq8l%2BKCLjhS4UhJVac7m&cookie16=VFC%2FuZ9az08KUQ56dCrZDlbNdA%3D%3D&pas=0' \
'&cookie15=VFC%2FuZ9ayeYq2g%3D%3D&cookie14=UoYagkR3PZ3UQw%3D%3D&existShop=false; ' \
'tracknick=tb85338658; lid=tb85338658; _l_g_=Ug%3D%3D; unb=3895799029; ' \
'cookie1=B0eh2kgmi29iNjmbWg2JUdr7m2PoH4FQJcna5FWIY2c%3D; cookie17=UNiN%2FYvCapPgTg%3D%3D; ' \
'_nk_=tb85338658; sgcookie=E100DLStFIXeqkyuZKGpXbna2HJxRf4TTqNa9lwcg5Esm%2FaEBoX' \
'P9PgZXe6lS98he2BPRnFvsR4YFw90sB1SrfQzHL7CkYCvmMx7373FvGHZ2vg%3D; sg=897;' \
' csg=0b687ed8; wk_unb=UNiN%2FYvCapPgTg%3D%3D; __wpkreporterwid_=08407be1-a5ed-4adc-' \
'3102-f98773652212; tfstk=gCZmWVtMzbOBiR5-yuif8y_yh5_-Gmi_b5Kt6chNzblWXtw9XzmgNS0Ah-' \
'QbrfVzZjrxDmewjRVMX-nYB72a6WavDmkxQGV7Cj-tWZTMSSF1GFBjWGYgM5Ni5tGt_fVTQrBRvMebhcia' \
'I6Idv_Ne2urm_CnZc0ReczVcvMeb3KHVp8SLXQZtAblZbquZaQlSBh84_j8PEAk9gF-4_TXoBv8w3nuqU' \
'YkjBcla_cWuUbMibxPZbfecwjhq1u582Zcgsza8qx0mT-bBbhqkvqcU3bxNTuDmOXyqZh-Zt8NaCRPNshnU' \
'R7qi85sMVme3z0k0rO8rg244MYNGxnl4q-rqMo5JDjrbUyETaO-ZszzEJjz5NGg4RSUEruCDVXzzER3uPO' \
'Tx6yMa12ZOOnG4QJZQJDjMIY43U0jyIU8FNwKsUOEy5FgqFYcLuGIsmBZ0ejXlEekmuYM22TXk5igqFYDcE' \
'TYFTqkS3Q1..; isg=BK-vcQqHG2EQ3B9cyDvQkHJPPsW5VAN2eHI3zME-7Z_5EMsSySbKx-JWkAAuaNvu'

# Global variable to store ad slots
ad_slots = ["mm_1902210064_2348000105_113763000348"]

# MySQL database configuration
DB_CONFIG = {
    'host': '172.16.3.12',
    'user': 'adx',
    'password': 'CaPn1jxidkkE5',
    'database': 'release_atd',
    'charset': 'utf8mb4'
}

# Establish a global database connection at project startup
connection = pymysql.connect(**DB_CONFIG)

# Function to insert data into the MySQL table
def insert_data(ds, pid, adzone_name, qingqiupv, active_ratio_df, tanx_effect_pv, tanx_clk, dongfeng_ef):
    try:
        with connection.cursor() as cursor:
            sql = '''
            INSERT INTO tanx_monitor (ds, pid, adzone_name, qingqiupv, active_ratio_df, tanx_effect_pv, tanx_clk, dongfeng_ef, create_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, UNIX_TIMESTAMP())
            ON DUPLICATE KEY UPDATE
                adzone_name = VALUES(adzone_name),
                qingqiupv = VALUES(qingqiupv),
                active_ratio_df = VALUES(active_ratio_df),
                tanx_effect_pv = VALUES(tanx_effect_pv),
                tanx_clk = VALUES(tanx_clk),
                dongfeng_ef = VALUES(dongfeng_ef)
            '''
            cursor.execute(sql, (ds, pid, adzone_name, qingqiupv, active_ratio_df, tanx_effect_pv, tanx_clk, dongfeng_ef))
        connection.commit()
    except Exception as e:
        logging.error(f"Failed to insert data for pid {pid}: {e}")
        print(f"Failed to insert data for pid {pid}: {e}")

@app.route('/update_cookie', methods=['POST'])
def update_cookie():
    global cookie_value
    cookie_value = request.form['cookie']
    return "Cookie 已更新成功！"

@app.route('/cookie_input')
def cookie_input_page():
    try:
        return open('cookie_input.html').read(), 200, {'Content-Type': 'text/html'}
    except FileNotFoundError:
        logging.error("cookie_input.html not found")
        return "Error: cookie_input.html not found", 404

@app.route('/')
def index():
    return redirect('/cookie_input')

@app.route('/update_ad_slots', methods=['POST'])
def update_ad_slots():
    global ad_slots
    ad_slots = request.form['ad_slots'].split('\n')
    return "广告位列表已更新成功！"

# Execute fetch_data once at startup
def fetch_data():
    url = 'https://tanx.alimama.com/api/media/debug/report/getReport.htm'
    headers = {
        'Cookie': cookie_value,
        'Content-Type': 'application/json'
    }
    # Use yesterday's date as default
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    for pid in ad_slots:
        data = {
            "ds": yesterday,
            "mediaClick": "1",
            "mediaCost": "1",
            "mediaPV": "1",
            "pid": pid,
            "type": "rtb"
        }
        #print(f"Fetching data for url:{url} pid: {pid} headers {headers} with data: {data}")
        response = requests.post(url, headers=headers, json=data)
        try:
            response_data = response.json()
            tanx_monitor_param_list = response_data.get("data", {}).get("clickMonitorParamList", [])
            for item in tanx_monitor_param_list:
                insert_data(
                    item.get("ds"),
                    item.get("pid"),
                    item.get("adzoneName"),
                    item.get("qingqiupv"),
                    item.get("activeRatioDf"),
                    item.get("tanxEffectPv"),
                    item.get("tanxClk"),
                    item.get("dongfengEf")
                )
                logging.info(f"Stored Data for pid {pid}: {item}")
                print(item)
        except Exception as e:
            logging.error(f"Error processing response for pid {pid}: {e}")
            print(f"Error processing response for pid {pid}: {e}")

# Schedule the task to run every day at 12:00
schedule.every().day.at("12:09").do(fetch_data)

@app.route('/fetch_data', methods=['POST'])
def fetch_data_button():
    fetch_data()
    return "抓包调用成功！"

def run_flask():
    app.run(port=5000)

flask_thread = Thread(target=run_flask)
flask_thread.start()

try:
    print("Scheduler started. Waiting for tasks...")
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("Program terminated by user.")
    logging.info("Program terminated by user.")



# 调用浏览器抓包，备选，不一定用
def selenium_fetch_data():
    # Set up the Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Navigate to the target page
        driver.get('https://tanx.alimama.com/cooperation/pages/utils/traffic_verification')

        # Wait for the page to load and interact with elements
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'date'))  # Example element ID
        )

        # Select fields and perform query
        date_field = driver.find_element(By.ID, 'date')
        date_field.send_keys('2025-06-09')  # Example date

        query_button = driver.find_element(By.ID, 'query')  # Example button ID
        query_button.click()

        # Wait for results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'result'))  # Example result class
        )

        # Extract and log results
        results = driver.find_element(By.CLASS_NAME, 'result').text
        logging.info(f"Selenium Results: {results}")
        print(results)

    finally:
        driver.quit()

@app.route('/selenium_fetch', methods=['POST'])
def selenium_fetch_button():
    selenium_fetch_data()
    return "Selenium 抓包调用成功！"
