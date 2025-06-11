import requests
import schedule
import time
from flask import Flask, request, redirect
from threading import Thread
import logging
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from datetime import datetime, timedelta
import pymysql
from collections import deque
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

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

# 默认的广告位列表
ad_slots = [
    "mm_1902210064_2348000105_111662900182",
    "mm_1902210064_2348000105_111663100185",
    "mm_1902210064_2348000105_113763000348",
    "mm_1902210064_2348000105_113765750160",
    "mm_3447365382_2749500311_114553400117",
    "mm_3447365382_2749500311_114552150188",
    "mm_1861850082_2364600045_112144700173",
    "mm_1873810155_2320450209_111384500336",
    "mm_1873810155_2320450209_111953150429",
    "mm_1873810155_2320450209_111953700467",
    "mm_1861850082_2364600045_115796950045",
    "mm_1861850082_2364600045_111952850176",
    "mm_1861850082_2364600045_111952350174",
    "mm_1562690005_2184850029_111650700372",
    "mm_1562690005_2184850029_111651000378",
    "mm_1562690005_2184850029_112164850011",
    "mm_1562690005_2184850029_112159050469",
    "mm_6899417631_3131950139_115762350460",
    "mm_6899417631_3131950139_115765600056",
    "mm_6899417631_3131950139_115768000140",
    "mm_6899417631_3131950139_115764850334",
    "mm_6899417631_3131950139_115840550019",
    "mm_6899417631_3131950139_115834100467",
    "mm_2279650033_2540650473_111838750084",
    "mm_2279650033_2540650473_111836000276",
    "mm_2279650033_2540650473_111835400327",
    "mm_2279650033_2540650473_111835250296",
    "mm_2279650033_2540650473_111835500278",
    "mm_2279650033_2540650473_111835750274",
    "mm_2279650033_2540650473_114534000022",
    "mm_2279650033_2540650473_114532100161"
]

ad_slots_up = []

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


@app.route('/')
def cookie_input_page():
    try:
        # 使用绝对路径加载 HTML 文件
        html_path = './cookie_input.html'
        with open(html_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        # 将广告位列表插入到 <textarea> 中
        ad_slots_text = "\n".join(ad_slots)
        html_content = html_content.replace('<textarea id="ad_slots" name="ad_slots" rows="5" required></textarea>', f'<textarea id="ad_slots" name="ad_slots" rows="5" required>{ad_slots_text}</textarea>')
        return html_content, 200, {'Content-Type': 'text/html'}
    except FileNotFoundError:
        logging.error("cookie_input.html not found")
        return "Error: cookie_input.html not found", 404
    

@app.route('/update_cookie', methods=['POST'])
def update_cookie():
    global cookie_value
    cookie_value = request.form['cookie']
    return "Cookie 已更新成功！"


@app.route('/update_ad_slots', methods=['POST'])
def update_ad_slots():
    global ad_slots
    global ad_slots_up
    # 去掉传递进来的数据中的 \r
    ad_slots = [slot.replace('\r', '') for slot in request.form['ad_slots'].split('\n')]
    if len(ad_slots_up) == 0:
        ad_slots_up = ad_slots.copy()
    logging.info(f"广告位列表已更新: {ad_slots}")
    return "广告位列表已更新成功！"

# Execute fetch_data once at startup
def fetch_data():
    status_record = {"execution_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "status": "执行中"}
    #print(f"Fetching data at {status_record['execution_time']} with cookie: {cookie_value}")
    try:
        url = 'https://tanx.alimama.com/api/media/debug/report/getReport.htm'
        headers = {
            'Cookie': cookie_value,
            'Content-Type': 'application/json'
        }
        # Use yesterday's date as default
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        print(f"Fetching yesterday at {yesterday}")
    
        for pid in ad_slots:
            data = {
                "ds": yesterday,
                "mediaClick": "1",
                "mediaCost": "1",
                "mediaPV": "1",
                "pid": pid,
                "type": "rtb"
            }
            response = requests.post(url, headers=headers, json=data)
            #print(f"Fetching data for url:{url} pid: {pid} with data: {data} response data: {response}")
            try:
                response_data = response.json()
                #print(f"Fetching response_data: {response_data}")
                tanx_monitor_param_list = response_data.get("data", {}).get("clickMonitorParamList", [])
                # 修改条件判断，检查列表是否为空
                if len(tanx_monitor_param_list) == 0:
                    logging.error(f"No data found for pid {pid} on {yesterday}")
                    print(f"No data found for pid {pid} on {yesterday}")
                    continue
                # 将 activeRatioDf 转换为百分数格式
                for item in tanx_monitor_param_list:
                    active_ratio_df = item.get("activeRatioDf") if item.get("activeRatioDf") not in (None, "") else "0"
                    ratio = float(active_ratio_df) * 100
                    active_ratio_df_percent = str(f"{ratio:.2f}%")
                    insert_data(
                        item.get("ds"),
                        item.get("pid"),
                        item.get("adzoneName"),
                        item.get("qingqiupv"),
                        active_ratio_df_percent,
                        item.get("tanxEffectPv"),
                        item.get("tanxClk"),
                        item.get("dongfengEf")
                    )
                    logging.info(f"Stored Data for pid {pid}: {item}")
                    print(f"Stored Data for pid: {pid}")
            except Exception as e:
                logging.error(f"Error processing response for pid {pid}: {e}")
                print(f"Error processing response for pid {pid}: {e}")
        status_record["status"] = "成功"
    except Exception as e:
        status_record["status"] = f"失败: {e}"
    finally:
        # 修复 scheduler_status 的错误操作
        # 删除错误的字典键操作
        # scheduler_status["last_execution"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 确保 fetch_data 函数正确追加 status_record
        scheduler_status.append(status_record)

@app.route('/fetch_data', methods=['POST'])
def fetch_data_button():
    fetch_data()
    query_and_export_data()
    return "抓包调用成功！"

def run_flask():
    app.run(port=5000)


# 全局变量存储定时任务状态
scheduler_status = deque(maxlen=10)  # 存储最近十次的执行记录

@app.route('/scheduler_status', methods=['GET'])
def get_scheduler_status():
    return list(scheduler_status)

def query_and_export_data():
    try:
        # Query the database for the last 30 days of data
        query = '''
        SELECT ds, pid, adzone_name, qingqiupv, active_ratio_df, tanx_effect_pv, tanx_clk, dongfeng_ef
        FROM tanx_monitor
        WHERE ds >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        '''
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        # Convert the result to a pandas DataFrame
        columns = ['日期', '广告位', '广告位名称', 'tanx有效请求', '东风手淘换端率-同步点击', 'TANX曝光数', 'TANX点击数', 'TANX预估收益']
        df = pd.DataFrame(result, columns=columns)

        # Export the DataFrame to an Excel file
        file_path = '/tmp/tanx_data.xlsx'
        df.to_excel(file_path, index=False)
        logging.info(f"Data exported to {file_path}")

        # Send the Excel file via email
        send_email(file_path)

    except Exception as e:
        logging.error(f"Error querying or exporting data: {e}")

# Global variable to store email recipients
email_recipients = ['chemanyu@admate.cn','zhangwenjing@admate.cn']

def send_email(file_path):
    try:
        # Email configuration
        sender_email = "monitor@admate.cn"
        sender_password = "Wut49622"
        subject = "Tanx Data Export"

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ", ".join(email_recipients)
        msg['Subject'] = subject

        # Email body
        print(f"Sending email to: {email_recipients}")
        body = "Please find the attached Excel file containing the Tanx data for the last 30 days."
        msg.attach(MIMEText(body, 'plain'))

        # Attach the Excel file
        with open(file_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={file_path.split("/")[-1]}')
        msg.attach(part)

        # Send the email
        with smtplib.SMTP('smtp.partner.outlook.cn', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email_recipients, msg.as_string())

        logging.info(f"Email sent to {email_recipients}")

    except Exception as e:
        logging.error(f"Error sending email: {e}")

# 定时更新Cookie的函数
def fetch_and_update_cookie():
    global cookie_value
    driver = None  # Initialize driver to None
    try:
        # Set up Selenium WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--disable-gpu')
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # Navigate to the target page
        driver.get('https://tanx.alimama.com/cooperation/pages/utils/traffic_verification')

        # Wait for the page to load and extract cookies
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))  # Wait for the body tag to load
        )
        time.sleep(5)
        cookies = driver.get_cookies()
        print(f"Fetched cookies: {cookies}")
        # Format cookies into a string
        cookie_value = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
        print(f"Updated cookie_value: {cookie_value}")
        logging.info(f"Updated cookie_value: {cookie_value}")

    except Exception as e:
        logging.error(f"Error fetching and updating cookie: {e}")
        print(f"Error fetching and updating cookie: {e}")

    finally:
        if driver:
            driver.quit()


def login_and_fetch_cookie():
    global cookie_value
    driver = None
    try:
        # Set up Selenium WebDriver
        options = webdriver.ChromeOptions()
        # Temporarily disable headless mode for debugging
        # options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # Navigate to the login page
        driver.get('https://tanx.alimama.com/login')

        # Wait for the login form to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'fm-login-id'))
        )

        # Fill in the login credentials
        username_field = driver.find_element(By.ID, 'fm-login-id')
        password_field = driver.find_element(By.ID, 'fm-login-password')
        login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')

        username_field.send_keys('tb85338658')
        password_field.send_keys('AdMate2025.4.17&')
        login_button.click()

        # Wait for the page to load after login
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )

        # Extract cookies
        cookies = driver.get_cookies()
        cookie_value = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
        logging.info(f"Fetched cookies: {cookie_value}")
        print(f"Fetched cookies: {cookie_value}")

    except Exception as e:
        logging.error(f"Error during login and cookie fetch: {e}")
        print(f"Error during login and cookie fetch: {e}")

    finally:
        if driver:
            driver.quit()

# Call the function to fetch cookies
#login_and_fetch_cookie()

# 新增一个定时任务，每十分钟执行一次 测试
schedule.every().day.at("12:00").do(fetch_data)
schedule.every().day.at("12:30").do(query_and_export_data)
#schedule.every(1).minutes.do(fetch_and_update_cookie)


flask_thread = Thread(target=run_flask)
flask_thread.start()

# 添加调试日志以确认定时任务是否正常运行
try:
    print("Scheduler started. Waiting for tasks...")
    while True:
        schedule.run_pending()
        print("Pending tasks executed.")  # 调试日志
        time.sleep(1)
except KeyboardInterrupt:
    print("Program terminated by user.")
    logging.info("Program terminated by user.")



# 调用浏览器抓包，备选，不一定用
# def selenium_fetch_data():
#     # Set up the Selenium WebDriver
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless')
#     options.add_argument('--disable-gpu')
#     service = Service(CHROME_DRIVER_PATH)
#     driver = webdriver.Chrome(service=service, options=options)
    
#     try:
#         # Navigate to the target page
#         driver.get('https://tanx.alimama.com/cooperation/pages/utils/traffic_verification')

#         # Wait for the page to load and interact with elements
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.ID, 'date'))  # Example element ID
#         )

#         # Select fields and perform query
#         date_field = driver.find_element(By.ID, 'date')
#         date_field.send_keys('2025-06-09')  # Example date

#         query_button = driver.find_element(By.ID, 'query')  # Example button ID
#         query_button.click()

#         # Wait for results to load
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CLASS_NAME, 'result'))  # Example result class
#         )

#         # Extract and log results
#         results = driver.find_element(By.CLASS_NAME, 'result').text
#         logging.info(f"Selenium Results: {results}")
#         print(results)

#     finally:
#         driver.quit()

# @app.route('/selenium_fetch', methods=['POST'])
# def selenium_fetch_button():
#     selenium_fetch_data()
#     return "Selenium 抓包调用成功！"



