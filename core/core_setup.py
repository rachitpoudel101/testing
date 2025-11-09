import base64
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- Constants ---
AUTH_USER = "mav"
AUTH_PASS = "mavsecret"
LOGIN_URL = "https://uattuth.dolphin.com.np/login"
# DASHBOARD_URL = "https://uattuth.dolphin.com.np/phar/pharmacy/mdashboard"
LOG_FILE = "core_test_result.log"


# ----------------------------------------------------------------------
#  Base Class: Handles driver setup, login, and cleanup
# ----------------------------------------------------------------------
class BaseCanteenAutomation:
    def __init__(self, username, password, log_callback=None):
        self.username = username
        self.password = password
        self.driver = None
        self.logs = []
        self.log_callback = log_callback

    def log(self, msg):
        # timestamp = time.strftime("[%Y-%m-%d %H:%M:%S] ")
        line =  msg
        self.logs.append(line)
        if self.log_callback:
            self.log_callback(line)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def init_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.password_manager_leak_detection": False
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        auth_header = base64.b64encode(f"{AUTH_USER}:{AUTH_PASS}".encode()).decode()
        self.driver.execute_cdp_cmd("Network.enable", {})
        self.driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"Authorization": f"Basic {auth_header}"}})
        self.log("Chrome driver initialized with Basic Auth")
        time.sleep(2)  #  Wait to visually confirm browser opened

    def login(self):
        self.log("Logging in...")
        self.driver.get(LOGIN_URL)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
        time.sleep(1)  #  Wait for login page to fully load

        self.driver.find_element(By.ID, "email").send_keys(self.username)
        time.sleep(0.5)
        self.driver.find_element(By.ID, "password").send_keys(self.password)
        time.sleep(0.5)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        self.log("Login submitted.")
        time.sleep(4)  #  Pause to see post-login transition

    def quit(self):
        if self.driver:
            time.sleep(2)  #  Pause before closing
            self.driver.quit()
            self.log("Browser closed.")