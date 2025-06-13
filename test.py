import logging
import time
import random
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ActionChains

def login_and_fetch_cookie():
    """
    Automates login to Alimama (阿里妈妈) platform and returns cookies.
    Returns:
        str: Cookie string if login successful, None otherwise
    """
    cookie_value = None
    driver = None
    try:
        # Set up Chrome options
        options = webdriver.ChromeOptions()
        
        # 禁用自动化标志
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 常规设置
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        
        # 更多反检测设置
        options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        
        # 使用伪装的 navigator.webdriver
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # 添加随机 user-agent
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        ]
        options.add_argument(f'user-agent={random.choice(user_agents)}')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 设置窗口大小和位置
        driver.set_window_size(1200, 800)
        driver.set_window_position(0, 0)
        
        # 设置隐式等待时间
        driver.implicitly_wait(10)
        
        # 访问登录页面
        driver.get('https://tanx.alimama.com/login')
        
        # 确保页面完全加载
        wait = WebDriverWait(driver, 30)
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
        
        # 强制窗口到前台
        driver.execute_script("window.focus();")
        logging.info("Login page loaded successfully.")
        
        # 等待页面稳定并尝试多种方式定位iframe
        time.sleep(5)  # 给页面更多时间完全加载和稳定
        logging.info("Starting iframe detection process...")
        
        # 尝试多种定位器定位iframe
        iframe_found = False
        iframe_locators = [
            (By.CSS_SELECTOR, "iframe[src*='login']"),
            (By.TAG_NAME, "iframe")
        ]
        
        for by, locator in iframe_locators:
            try:
                logging.info(f"Attempting to locate iframe with {by}: {locator}")
                
                # 先检查iframe是否存在
                iframe_present = wait.until(
                    EC.presence_of_element_located((by, locator))
                )
                logging.info(f"Iframe found with {by}: {locator}")
                
                # 确保iframe可见
                wait.until(
                    EC.visibility_of_element_located((by, locator))
                )
                logging.info("Iframe is visible")
                
                # 尝试滚动到iframe
                driver.execute_script("arguments[0].scrollIntoView(true);", iframe_present)
                time.sleep(1)
                
                # 检查iframe是否可切换
                wait.until(
                    EC.frame_to_be_available_and_switch_to_it((by, locator))
                )
                logging.info("Successfully switched to iframe")
                
                # 验证是否成功切换到iframe内
                try:
                    # 尝试在iframe内定位一个常见元素
                    wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text'], input[type='password'], button"))
                    )
                    logging.info("Successfully verified iframe switch - found form elements")
                    iframe_found = True
                    break
                except Exception as e:
                    logging.warning(f"Could not verify iframe contents: {str(e)}")
                    driver.switch_to.default_content()
                    continue
                    
            except Exception as e:
                logging.warning(f"Failed with locator {by}: {locator}. Error: {str(e)}")
                try:
                    driver.switch_to.default_content()
                except:
                    pass
                continue
        
        if not iframe_found:
            logging.error("Failed to switch to iframe after trying all methods")
            raise Exception("Could not locate or switch to login iframe")
            
        # 等待页面元素加载完成并确保 iframe 内容已加载
        time.sleep(3)
        wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
        
        logging.info("Starting username input process")
        username = '天津浩睿信息科技有限公司'
        password = '@QQhr123654'  # 建议从配置文件读取
        success = False
        
        # 尝试多种方式定位和输入用户名
        locators = [
            #(By.ID, "fm-login-id"),
            #(By.NAME, "fm-login-id"),
            #(By.CSS_SELECTOR, "input.fm-text[name='fm-login-id']"),
            (By.CSS_SELECTOR, ".input-plain-wrap input[type='text']")
        ]
        
        # 尝试多种方式定位和输入用户名密码
        def try_input_field(field_locators, value, field_name):
            for by, locator in field_locators:
                try:
                    logging.info(f"Attempting to locate {field_name} field with {by}: {locator}")
                    field = wait.until(
                        EC.presence_of_element_located((by, locator))
                    )
                    wait.until(
                        EC.element_to_be_clickable((by, locator))
                    )
                    
                    # 清除字段
                    field.clear()
                    time.sleep(random.uniform(0.3, 0.7))
                    
                    # 使用多种输入方法
                    try:
                        # 方法1: 直接输入
                        field.send_keys(value)
                        logging.info(f"Direct input for {field_name} successful")
                        return True
                    except Exception as e1:
                        logging.warning(f"Direct input failed for {field_name}: {str(e1)}")
                        
                        try:
                            # 方法2: JavaScript输入
                            driver.execute_script(
                                f"arguments[0].value = arguments[1];", 
                                field, 
                                value
                            )
                            logging.info(f"JavaScript input for {field_name} successful")
                            return True
                        except Exception as e2:
                            logging.warning(f"JavaScript input failed for {field_name}: {str(e2)}")
                            
                            try:
                                # 方法3: ActionChains模拟人工输入
                                actions = ActionChains(driver)
                                actions.move_to_element(field)
                                actions.click()
                                actions.pause(random.uniform(0.3, 0.5))
                                for char in value:
                                    actions.send_keys(char)
                                    actions.pause(random.uniform(0.1, 0.2))
                                actions.perform()
                                logging.info(f"ActionChains input for {field_name} successful")
                                return True
                            except Exception as e3:
                                logging.warning(f"ActionChains input failed for {field_name}: {str(e3)}")
                                continue
                except Exception as e:
                    logging.warning(f"Failed to locate/interact with {field_name} using {by}: {locator}. Error: {str(e)}")
                    continue
            return False
        
        # 用户名输入定位器
        username_locators = [
            #(By.CSS_SELECTOR, "#username"),
            #(By.NAME, "username"),
            (By.CSS_SELECTOR, "input[type='text']"),
            (By.XPATH, "//input[@placeholder='请输入账号']")
        ]
        
        # 密码输入定位器
        password_locators = [
            #(By.CSS_SELECTOR, "#password"),
            #(By.NAME, "password"),
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.XPATH, "//input[@placeholder='请输入密码']")
        ]
        
        # 尝试输入用户名
        if not try_input_field(username_locators, username, "username"):
            logging.error("Failed to input username after trying all methods")
            raise Exception("Could not input username")
        
        time.sleep(random.uniform(0.8, 1.5))
        
        # 尝试输入密码
        if not try_input_field(password_locators, password, "password"):
            logging.error("Failed to input password after trying all methods")
            raise Exception("Could not input password")
        
        # 输入密码
        password_field = wait.until(
            EC.presence_of_element_located((By.ID, "fm-login-password"))
        )
        password_field.clear()
        password = '@QQhr123654'  # 建议从配置文件读取
        for char in password:
            password_field.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))
        logging.info("Password entered")
        
       
        # 登录按钮定位器
        login_button_locators = [
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//button[contains(text(), '登录')]"),
            (By.CSS_SELECTOR, ".submit"),
            (By.CLASS_NAME, "login-button")
        ]
        
        # 尝试点击登录按钮
        button_clicked = False
        for by, locator in login_button_locators:
            try:
                logging.info(f"Attempting to locate login button with {by}: {locator}")
                button = wait.until(
                    EC.presence_of_element_located((by, locator))
                )
                wait.until(
                    EC.element_to_be_clickable((by, locator))
                )
                
                # 尝试多种点击方法
                try:
                    # 方法1: 直接点击
                    button.click()
                    button_clicked = True
                    logging.info("Direct click on login button successful")
                    break
                except Exception as e1:
                    logging.warning(f"Direct click failed: {str(e1)}")
            except Exception as e:
                logging.warning(f"Failed to locate/interact with login button using {by}: {locator}. Error: {str(e)}")
                continue
        
        if not button_clicked:
            logging.error("Failed to click login button after trying all methods")
            raise Exception("Could not click login button")
            
        # 等待登录结果
        time.sleep(10)  # 给登录过程足够时间
        
        # 检查登录结果
        # try:
        #     # 检查是否仍在登录页面
        #     if "login" in driver.current_url.lower():
        #         logging.error("Login failed - still on login page")
        #         raise Exception("Login failed - still on login page")
                
        #     # 尝试定位登录后才会出现的元
            
        # except Exception as e:
        #     logging.error(f"Login verification failed: {str(e)}")
        #     raise Exception("Could not verify successful login")
        
        # 切换回主文档并获取cookies
        # driver.switch_to.default_content()
        
        # # 验证登录是否成功
        # try:
        #     wait.until(EC.url_changes('https://tanx.alimama.com/login'))
        #     logging.info("Login successful - URL changed")
        # except:
        #     logging.error("Login might have failed - URL didn't change")
            
        # 获取cookies
        cookies = driver.get_cookies()
        cookie_value = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
        logging.info("Successfully fetched cookies")
        logging.info(cookie_value)
        
        #return cookie_value
        
    except Exception as e:
        logging.error(f"Error during login process: {str(e)}")
        return None
        
    #finally:
        # if driver:
        #     driver.quit()


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


if __name__ == '__main__':
    # 设置更详细的日志记录
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log', mode='w', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    login_and_fetch_cookie()
