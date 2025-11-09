import base64
import time
import traceback
from selenium.webdriver.common.keys import Keys
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
LOGIN_URL = "https://uattuth.dolphin.com.np/canteen/login"
EMPLOYEE_URL = "https://uattuth.dolphin.com.np/canteen/employee"
EMPLOYEE_MEAL_SCHEDULE_URL = "https://uattuth.dolphin.com.np/canteen/user-meal-schedule"
LOG_FILE = "test_result.log"


# ----------------------------------------------------------------------
#  Base Class for shared Selenium logic
# ----------------------------------------------------------------------
class BaseCanteenAutomation:
    def __init__(self, username, password, log_callback=None):
        self.username = username
        self.password = password
        self.driver = None
        self.logs = []
        self.log_callback = log_callback

    def log(self, msg):
        timestamp = time.strftime("[%Y-%m-%d %H:%M:%S] ")
        line = timestamp + msg
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

    def login(self):
        self.log("Logging in...")
        self.driver.get(LOGIN_URL)
        wait = WebDriverWait(self.driver, 10)
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_field = self.driver.find_element(By.NAME, "password")
        username_field.send_keys(self.username)
        password_field.send_keys(self.password)
        login_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Login') or contains(., 'Sign In')]")
        login_button.click()
        self.log("Login submitted.")
        time.sleep(2)

    def wait_click(self, by, value, timeout=10):
        el = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((by, value)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
        self.driver.execute_script("arguments[0].click();", el)
        return el

    def fill_field(self, field_id, value):
        el = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, field_id)))
        self.driver.execute_script("arguments[0].focus(); arguments[0].value='';", el)
        el.send_keys(value)
        self.log(f"Filled {field_id} = '{value}'")

    def quit(self):
        if self.driver:
            self.driver.quit()
            self.log("Browser closed.")


# ----------------------------------------------------------------------
#  Add Employee Test Class
# ----------------------------------------------------------------------
class AddEmployeeTest(BaseCanteenAutomation):
    def run(self, employee_id, first_name, last_name, middle_name="", department_list=None, is_active=True):
        department_list = department_list or []
        self.log("Starting Add Employee Test...")

        try:
            self.init_driver()
            self.login()
            self.driver.get(EMPLOYEE_URL)
            self.log("Employee page loaded.")
            time.sleep(2)

            # Click create button
            self.wait_click(By.XPATH, "//button[contains(text(), 'Create')]")
            self.log("Clicked 'Create'.")

            # Fill Employee ID
            emp_field = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "employee_id")))
            emp_field.send_keys(employee_id)
            self.log(f"Employee ID: {employee_id}")

            # Check duplicate error
            time.sleep(1)
            try:
                error_el = self.driver.find_element(By.XPATH, "//span[@class='text-red-500 text-[12px] error-message']")
                if "Employee id already assigned" in error_el.text:
                    self.log("Duplicate Employee ID detected. Aborting.")
                    return False
            except:
                pass

            # Fill other names
            for fid, val in {"First name": first_name, "Middle name": middle_name, "Last name": last_name}.items():
                if val:
                    self.fill_field(fid, val)

            # Department multiselect
            try:
                dropdown = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.multiselect__placeholder")))
                dropdown.click()
                for dept in department_list:
                    option = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{dept}')]")))
                    option.click()
                    self.log(f"Selected department: {dept}")
            except Exception as e:
                self.log(f"Department selection skipped or failed: {e}")

            # Active checkbox
            try:
                checkbox = self.driver.find_element(By.ID, "is_active")
                if checkbox.is_selected() != is_active:
                    self.driver.execute_script("arguments[0].click();", checkbox)
                self.log(f"Set Active: {is_active}")
            except Exception as e:
                self.log(f"Checkbox issue: {e}")

            # Save
            self.wait_click(By.XPATH, "//button[normalize-space()='Save']")
            self.log("Clicked Save.")
            time.sleep(2)

            # Verify creation
            search_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search']")))
            search_input.send_keys(employee_id)
            time.sleep(1)
            if "No Employee Found" in self.driver.page_source:
                self.log(f"Add Employee Failed for {employee_id}")
                return False
            self.log(f"Employee '{employee_id}' created successfully!")
            return True

        except Exception as e:
            self.log(f"Error: {e}")
            self.log(traceback.format_exc())
            return False
        finally:
            self.quit()


# ----------------------------------------------------------------------
#  Employee Meal Schedule Test Class (Updated & Dynamic)
# ----------------------------------------------------------------------
class EmployeeMealTest(BaseCanteenAutomation):
    def run(self, meal_date, meal_schedule_list=None, department_list=None, employee_list=None):
        meal_schedule_list = meal_schedule_list or []
        department_list = department_list or []
        employee_list = employee_list or []
        self.log("Starting Employee Meal Schedule Test...")

        try:
            self.init_driver()
            self.login()
            self.driver.get(EMPLOYEE_MEAL_SCHEDULE_URL)
            self.log("Employee Meal Schedule page loaded.")
            time.sleep(2)

            # Click the Create button
            self.wait_click(By.XPATH, "//button[contains(text(), 'Create')]")
            self.log("Clicked 'Create'.")
            time.sleep(1)

            # Wait for modal
            MODAL_XPATH = "//div[contains(@class, 'fixed') and contains(@class, 'top-0') and contains(@class, 'z-10')]"
            modal = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, MODAL_XPATH))
            )
            self.log("Modal detected.")

            # --- Date Entry ---
            clear_button = modal.find_element(By.CSS_SELECTOR, ".calendar-clear-input")
            self.driver.execute_script("arguments[0].click();", clear_button)
            date_input = modal.find_element(By.CSS_SELECTOR, ".calendar-input")
            self.driver.execute_script("arguments[0].click();", date_input)
            date_input.send_keys(meal_date)
            date_input.send_keys(Keys.ENTER)
            self.log(f"Entered meal date: {meal_date}")

            # --- Meal Schedule Multiselect ---
            self._multiselect_input("Select Meal Schedule", meal_schedule_list)

            # --- Department Multiselect ---
            self._multiselect_input("Select Department", department_list)

            # --- Employee Multiselect ---
            self._multiselect_input("Search by employee id or name", employee_list)

            # Click Add/Save button
            add_button = WebDriverWait(modal, 10).until(
                EC.element_to_be_clickable((By.XPATH, ".//button[text()='Add']"))
            )
            self.driver.execute_script("arguments[0].click();", add_button)
            self.log("Meal schedule submitted successfully!")
            time.sleep(2)

            return True

        except Exception as e:
            self.log(f"Error in Employee Meal Test: {e}")
            self.log(traceback.format_exc())
            return False
        finally:
            self.quit()

    # -----------------------
    # Helper: Robust Multiselect Input
    # -----------------------
    def _multiselect_input(self, placeholder_text, items):
        if not items:
            return
        try:
            input_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//input[@class='multiselect__input' and @placeholder='{placeholder_text}']"))
            )
            self.driver.execute_script("arguments[0].focus();", input_field)
            for item in items:
                input_field.send_keys(item)
                time.sleep(0.5)
                input_field.send_keys(Keys.ENTER)
                self.log(f"Selected '{item}' in '{placeholder_text}'")
            time.sleep(0.5)
        except Exception as e:
            self.log(f"Multiselect '{placeholder_text}' failed: {e}")
            self.log(traceback.format_exc())


# ----------------------------------------------------------------------
#  Wrapper Functions (for Tkinter UI)
# ----------------------------------------------------------------------
def employee_meal(username, password, meal_date, meal_schedule_list=None, department_list=None, employee_list=None, log_callback=None):
    test = EmployeeMealTest(username, password, log_callback)
    result = test.run(meal_date, meal_schedule_list, department_list, employee_list)
    return result, "\n".join(test.logs)

def add_employee(username, password, employee_id, first_name, last_name, middle_name="", department_list=None, is_active=True, log_callback=None):
    test = AddEmployeeTest(username, password, log_callback)
    result = test.run(employee_id, first_name, last_name, middle_name, department_list, is_active)
    return result, "\n".join(test.logs)
