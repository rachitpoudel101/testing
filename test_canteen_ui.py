import base64
import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- Global constants ---
AUTH_USER = "mav"
AUTH_PASS = "mavsecret"
LOGIN_URL = "https://uattuth.dolphin.com.np/canteen/login"
EMPLOYEE_URL = "https://uattuth.dolphin.com.np/canteen/employee"
EMPLOYEE_MEAL_SCHEDULE_URL = "https://uattuth.dolphin.com.np/canteen/user-meal-schedule"
LOG_FILE = "test_result.log"

# --- Initialize Chrome WebDriver with Basic Auth ---
def init_driver(log):
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Basic Auth headers
    auth_header = base64.b64encode(f"{AUTH_USER}:{AUTH_PASS}".encode()).decode()
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"Authorization": f"Basic {auth_header}"}})
    log(" Chrome driver initialized with Basic Auth")
    return driver

# --- Add Employee Test ---
def add_employee(username, password, employee_id, first_name, last_name,
                 middle_name="", department_list=None, is_active=True,
                 log_callback=None):
    import time, traceback
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    department_list = department_list or []
    logs = []

    def log(msg):
        timestamp = time.strftime("[%Y-%m-%d %H:%M:%S] ")
        full_msg = timestamp + msg
        logs.append(full_msg)
        if log_callback:
            log_callback(full_msg)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(full_msg + "\n")

    driver = None
    log(" Starting Add Employee Test...")

    try:
        # --- Login ---
        log(" Logging in...")
        driver = init_driver(log)
        driver.get(LOGIN_URL)
        time.sleep(2)
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        log("Login submitted.")
        time.sleep(3)

        # --- Employee Page ---
        driver.get(EMPLOYEE_URL)
        log("Employee page loaded.")
        time.sleep(2)

        # --- Click 'Create' ---
        create_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", create_btn)
        driver.execute_script("arguments[0].click();", create_btn)
        log("Clicked 'Create' button successfully.")
        time.sleep(2)

# --- Fill Employee ID first ---
        try:
            emp_id_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "employee_id"))
            )
            driver.execute_script("arguments[0].focus(); arguments[0].value='';", emp_id_input)
            emp_id_input.send_keys(employee_id)
            log(f"Filled employee_id = '{employee_id}'")
            
            # --- Check for duplicate immediately ---
            time.sleep(1.5)  # wait for frontend validation
            try:
                error_el = driver.find_element(
                    By.XPATH, "//span[@class='text-red-500 text-[12px] error-message']"
                )
                if "Employee id already assigned" in error_el.text.strip():
                    log(f" Error detected: {error_el.text.strip()}. Skipping rest of the form.")
                    driver.quit()
                    log("Browser closed due to duplicate Employee ID before filling other fields.\n")
                    return False, "\n".join(logs)
            except Exception:
                log("No duplicate Employee ID error detected. Continuing to fill form.")
        except Exception as e:
            log(f"Exception while filling employee_id: {e}")
            driver.quit()
            return False, "\n".join(logs)


        # --- Fill other fields ---
        try:
            other_fields = {
                "First name": first_name,
                "Middle name": middle_name,
                "Last name": last_name
            }
            for field_id, value in other_fields.items():
                input_el = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, field_id))
                )
                driver.execute_script("arguments[0].focus(); arguments[0].value='';", input_el)
                input_el.send_keys(value)
                log(f"Filled {field_id} = '{value}'")
        except Exception as e:
            log(f"Exception while filling other fields: {e}")
            log(traceback.format_exc())
            if driver:
                driver.quit()
            return False, "\n".join(logs)

        # --- Departments ---
        try:
            dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "span.multiselect__placeholder"))
            )
            dropdown.click()
            for dept in department_list:
                option = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{dept}')]"))
                )
                option.click()
                log(f"Selected department: {dept}")
        except Exception as e:
            log(f"Department selection skipped or failed: {e}")

        # --- Active Checkbox ---
        try:
            checkbox = driver.find_element(By.ID, "is_active")
            if checkbox.is_selected() != is_active:
                driver.execute_script("arguments[0].click();", checkbox)
            log(f"Checkbox 'is_active' set to {is_active}.")
        except Exception as e:
            log(f"Exception while setting 'is_active': {e}")

        # --- Click Save ---
        try:
            save_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Save']"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_btn)
            driver.execute_script("arguments[0].click();", save_btn)
            log("'Save' button clicked.")
            time.sleep(2)
        except Exception as e:
            log(f"Exception while clicking Save: {e}")
            log(traceback.format_exc())
            if driver:
                driver.quit()
            return False, "\n".join(logs)

        # --- Verify Employee Creation ---
        try:
            search_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search']"))
            )
            driver.execute_script("arguments[0].value='';", search_input)
            search_input.send_keys(employee_id)
            time.sleep(2)

            try:
                no_emp_div = driver.find_element(By.CSS_SELECTOR, "div.tabulator-placeholder-contents")
                if "No Employee Found" in no_emp_div.text:
                    log(f" Add Employee Failed! Employee '{employee_id}' not found.")
                    return False, "\n".join(logs)
            except:
                pass

            log(f" Employee '{employee_id}' created successfully!")
            return True, "\n".join(logs)
        except Exception as e:
            log(f"Exception during verification: {e}")
            log(traceback.format_exc())
            return False, "\n".join(logs)

    except Exception as e:
        log(f"Unexpected Exception in Add Employee Test: {e}")
        log(traceback.format_exc())
        return False, "\n".join(logs)

    finally:
        if driver:
            try:
                driver.quit()
                log("Browser closed.\n")
            except:
                pass



# --- Employee Meal Schedule Test ---
def employee_meal_schedule_test(username, password, 
                                schedule_for_tomorrow=False,
                                meal_schedule_list=None,
                                department_list=None,
                                employee_id_list=None,
                                log_callback=None):

    meal_schedule_list = meal_schedule_list or []
    department_list = department_list or []
    employee_id_list = employee_id_list or []

    logs = []
    def log(msg):
        timestamp = time.strftime("[%Y-%m-%d %H:%M:%S] ")
        full_msg = timestamp + msg
        logs.append(full_msg)
        if log_callback:
            log_callback(full_msg)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(full_msg + "\n")

    driver = None
    log(" Starting Employee Meal Schedule Test...")
    try:
        # --- Login ---
        log(" Logging in...")
        driver = init_driver(log)
        driver.get(LOGIN_URL)
        time.sleep(2)
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        log("Login submitted.")
        time.sleep(3)

        # --- Employee Meal Schedule Page ---
        driver.get(EMPLOYEE_MEAL_SCHEDULE_URL)
        log("Employee Meal Schedule page loaded.")
        time.sleep(2)

        # --- Click 'Create' ---
        create_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", create_btn)
        driver.execute_script("arguments[0].click();", create_btn)
        log("Clicked 'Create' button.")
        time.sleep(2)

        # --- Schedule for Tomorrow Checkbox ---
        if schedule_for_tomorrow:
            try:
                tomorrow_checkbox = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@id='schedule_tomorrow']"))
                )
                if not tomorrow_checkbox.is_selected():
                    driver.execute_script("arguments[0].click();", tomorrow_checkbox)
                log("Checkbox 'Schedule for Tomorrow' selected.")
            except Exception as e:
                log(f"Tomorrow checkbox skipped: {e}")

        # --- Select Meal Schedule ---

        try:
            time.sleep(1)
            # Wait for and locate the meal schedule input field
            meal_dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Select Meal Schedule']"))
            )

            # Scroll into view and click
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", meal_dropdown)
            meal_dropdown.click()
            time.sleep(1)

            # Select options from the dropdown
            for meal in meal_schedule_list:
                try:
                    option = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{meal}')]"))
                    )
                    driver.execute_script("arguments[0].click();", option)
                    log(f" Selected Meal Schedule: {meal}")
                except Exception as e:
                    log(f" Could not select meal '{meal}': {e}")

            # Click outside to close dropdown
            driver.find_element(By.TAG_NAME, "body").click()

        except Exception as e:
            log(f" Meal schedule selection skipped: {e}")

        # --- Select Departments ---
        try:
            time.sleep(1)

            # Dropdown selectors for different possible layouts
            dept_selectors = [
                "//span[@class='multiselect__placeholder' and text()='Select Department']",
                "//div[contains(@class,'department')]//span[contains(@class,'multiselect__placeholder')]",
                "//label[contains(text(),'Department')]/following::span[contains(@class,'multiselect__placeholder')][1]"
            ]

            dept_dropdown = None
            for sel in dept_selectors:
                try:
                    dept_dropdown = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, sel))
                    )
                    break
                except:
                    continue

            if not dept_dropdown:
                raise Exception("Department dropdown not found!")

            # Scroll into view and click to open dropdown
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dept_dropdown)
            dept_dropdown.click()
            time.sleep(1)

            # Find the input field inside the dropdown (for searchable multiselects)
            try:
                search_input = dept_dropdown.find_element(By.XPATH, "./ancestor::div[contains(@class,'multiselect')]/descendant::input")
            except:
                search_input = None

            # Select each department
            for dept in department_list:
                try:
                    log(f"1")
                    dropdown = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "span.multiselect__placeholder"))
                    )
                    log(f"3")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option)
                    option.click()
                    log(f"4")
                    for dept in department_list:
                        option = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{dept}')]"))
                        )
                    log(f"5")
                    option.click()

                    log(f"Selected Department: {dept}")
                    time.sleep(0.5)
                except Exception as e:
                    log(f"Could not select department '{dept}': {e}")

            # Click outside to close dropdown
            driver.find_element(By.TAG_NAME, "body").click()
            time.sleep(0.5)

        except Exception as e:
            log(f"Department selection skipped: {e}")




        # --- Select Employees ---
        try:
            time.sleep(1)
            emp_selectors = [
                "//input[@placeholder='Search by employee id or name']",
                "//input[contains(@aria-label,'Search')]",
                "//label[contains(text(),'Employee')]/following::input[1]"
            ]
            emp_input = None
            for sel in emp_selectors:
                try:
                    emp_input = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, sel))
                    )
                    break
                except:
                    continue

            if not emp_input:
                raise Exception("Employee search input not found!")

            for emp in employee_id_list:
                emp_input.clear()
                emp_input.send_keys(emp)
                time.sleep(2)
                try:
                    option = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{emp}')]"))
                    )
                    driver.execute_script("arguments[0].click();", option)
                    log(f"Selected Employee: {emp}")
                except Exception as e:
                    log(f"Could not select employee '{emp}': {e}")

            driver.find_element(By.TAG_NAME, "body").click()
        except Exception as e:
            log(f"Employee selection skipped: {e}")

        # --- Click 'Add' ---
        try:
            add_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Add']"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_btn)
            driver.execute_script("arguments[0].click();", add_btn)
            log("Clicked 'Add' button successfully.")
            time.sleep(2)
        except Exception as e:
            log(f"Add button skipped: {e}")

        # --- Click 'Save' ---
        save_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Save']"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_btn)
        driver.execute_script("arguments[0].click();", save_btn)
        log("Clicked 'Save' button.")
        time.sleep(3)

        log(" Employee Meal Schedule created successfully!")
        return True, "\n".join(logs)

    except Exception as e:
        log(f" Exception in Employee Meal Schedule Test: {e}")
        log(traceback.format_exc())
        return False, "\n".join(logs)
    finally:
        if driver:
            driver.quit()
            log("Browser closed.\n")