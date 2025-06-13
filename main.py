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
from cookie import login_and_fetch_cookie  # 从cookie.py导入方法

CHROME_DRIVER_PATH = "/opt/homebrew/bin/chromedriver" #

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Global variable to store the cookie
cookie_value = 'wk_cookie2=167f0c4d672ac968e0a93b99b0d0321b; __itrace_wid=95ae536e-98c9-4b4d-80b3-e28c2a186e6a; cna=VWfNIPe5zgoCASvziD7zfIGi; env_bak=FM%2BgywHD7Unoz8SbIc%2FnUBfFQSvsP66Kkma08fliLj6Y; __wpkreporterwid_=08407be1-a5ed-4adc-3102-f98773652212; t_alimama=ee2cffdec21995b8105c3f08a73ab6c9; lgc=; cookie2=1e5d78ccd2b97d0d1da082d51dd217ce; t=aad3d47a3693faf2be2983e66f9366c7; sn=; _tb_token_=7384e3d9e335a; XSRF-TOKEN=cb12569d-1278-439d-adef-7ace59411b33; cookie3_bak=1e5d78ccd2b97d0d1da082d51dd217ce; login=true; cancelledSubSites=empty; xlly_s=1; dnk=%5Cu5929%5Cu6D25%5Cu6D69%5Cu777F%5Cu4FE1%5Cu606F%5Cu79D1%5Cu6280%5Cu6709%5Cu9650%5Cu516C%5Cu53F8; tracknick=%5Cu5929%5Cu6D25%5Cu6D69%5Cu777F%5Cu4FE1%5Cu606F%5Cu79D1%5Cu6280%5Cu6709%5Cu9650%5Cu516C%5Cu53F8; lid=%E5%A4%A9%E6%B4%A5%E6%B5%A9%E7%9D%BF%E4%BF%A1%E6%81%AF%E7%A7%91%E6%8A%80%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8; wk_unb=UUpgTs0%2BqS386PihCA%3D%3D; _l_g_=Ug%3D%3D; cookie1=U7ZvqNzFjt0WHllf4lbxAgQ5Wl4LJjp%2Fl6HVIQ%2FXkiU%3D; sg=%E5%8F%B85e; uc1=cookie14=UoYagke%2BQnvi0A%3D%3D&pas=0&cookie15=V32FPkk%2Fw0dUvg%3D%3D&existShop=false&cookie16=UtASsssmPlP%2Ff1IHDsDaPRu%2BPw%3D%3D&cookie21=VT5L2FSpdiBh; havana_lgc_exp=1780898242562; unb=2218492598755; cookie17=UUpgTs0%2BqS386PihCA%3D%3D; _nk_=%5Cu5929%5Cu6D25%5Cu6D69%5Cu777F%5Cu4FE1%5Cu606F%5Cu79D1%5Cu6280%5Cu6709%5Cu9650%5Cu516C%5Cu53F8; sgcookie=E100Iwg5vQePW%2FuvoH870NOoXXaNTJ0n3ETkubPIWgdgirmz3UJSBvaSCd7DDVlbUy1zB%2BSIN9KnVy%2B5Hh5yVVEzOPAkx3QSfJAoimBHTiaJr4A%3D; csg=5ce22315; cookie3_bak_exp=1750053442563; tfstk=gGIK-W2eFRHplBjpI9ziZYhTGPegiPXFQ6WjqQAnP1CO3_LoZTaUeuCGwe2FFW5R2C1ytBxuLUtR36dHrHtk2bCcUBgHZw2JNC6XEJyzUudR5tbHEw2z2QKFjwmktW-RFsx8iSq0m9Wev3N0iYRfPmteeLMBFbc_fLtJd1faKXWe43NiI0a0D95FfMKVN3w9fLprP3OIVfw9nL-SAUiI5fOw139WdB66Cpv-VDO5NOw9UCOWV31WfRpr_w2p_v9K2ZAxuReKeGiSVGpp5PXB1ETYEpTpG9OTG_SMpQRfdCnSVIBNNTW5N7nkcZ5O2E1z2c-hHNt6pNeS5BTAR6vNwonBOGBCABjQsDACYO_cq1wSVQQ1lEAC75ryRZ5hlFIg9cRf5OBkWNyr-Qb2F_8VqSoeOT6V0ZxY2YpOkOtO4BjcD96siIpoRRetz48BQ0A3ih05JwJWBI2BR4uyrdooJgJjz48tmdd0IOurzF0c.; isg=BMrKpYwglklzYxrv_SRNU794G7Zsu04VvzPZEVQDopw0B2vBPE6OJgn1E3Pb98at'

# 默认的广告位列表
ad_slots = [
    "mm_1902210064_2348000105_111662900182",
    "mm_1902210064_2348000105_111663100185",
    "mm_1902210064_2348000105_113763000348",
    "mm_1902210064_2348000105_113765750160",
    "mm_3447365382_2749500311_114553400117",
    "mm_3447365382_2749500311_114552150188",
    "mm_1873810155_2320450209_111384500336",
    "mm_1873810155_2320450209_111953150429",
    "mm_1873810155_2320450209_111953700467",
    "mm_1873810155_2320450209_115792250490",
    "mm_1873810155_2320450209_115890350442",
    "mm_1873810155_2320450209_115894200243",
    "mm_1873810155_2320450209_115797000138",
    "mm_1873810155_2320450209_111388400121",
    "mm_1861850082_2364600045_115796950045",
    "mm_1861850082_2364600045_111952850176",
    "mm_1861850082_2364600045_111952350174",
    "mm_1861850082_2364600045_111484350168",
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
    "mm_2279650033_2540650473_114532100161",
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

# Ensure the DB connection is alive or reopen if dropped
def get_connection():
    global connection
    try:
        connection.ping(reconnect=True)
    except Exception:
        connection = pymysql.connect(**DB_CONFIG)
    return connection

# Function to insert data into the MySQL table
def insert_data(ds, pid, adzone_name, qingqiupv, active_ratio_df, tanx_effect_pv, tanx_clk, dongfeng_ef):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
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
                if response_data.get("info", {}).get("errorCode") == "user_not_login":
                    logging.info("User not logged in, please update cookie.")
                    update_cookie_task()  # 自动更新cookie
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
        conn = get_connection()
        with conn.cursor() as cursor:
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
email_recipients = ['chemanyu@admate.cn','zhangwenjing@admate.cn','xuzhongwang@admate.cn','fanang@admate.cn']
#email_recipients = ['chemanyu@admate.cn']

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

# 定时更新cookie的函数
def update_cookie_task():
    global cookie_value
    new_cookie = login_and_fetch_cookie()
    if new_cookie:
        cookie_value = new_cookie
        logging.info("自动更新Cookie成功")
    else:
        logging.error("自动更新Cookie失败")


# 设置定时任务
schedule.every().day.at("12:15").do(fetch_data)  # 每天抓取数据
schedule.every().day.at("12:30").do(query_and_export_data)  # 每天导出数据


flask_thread = Thread(target=run_flask)
flask_thread.start()

# 添加调试日志以确认定时任务是否正常运行
try:
    print("Scheduler started. Waiting for tasks...")
    while True:
        schedule.run_pending()
        print("Pending tasks executed.")  # 调试日志
        time.sleep(60)
except KeyboardInterrupt:
    print("Program terminated by user.")
    logging.info("Program terminated by user.")