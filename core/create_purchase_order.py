import time
import traceback
from core_setup import BaseCanteenAutomation
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait,Select
from selenium.webdriver.support import expected_conditions as EC

class PurchaseOrder(BaseCanteenAutomation):
    def load_dashboard(self): 
        try:
            print("[DEBUG] Initializing driver...")
            self.init_driver()
            print("[DEBUG] Logging in...")
            self.login()
            self.log("Dashboard loaded.")
            time.sleep(2)

            print("[DEBUG] Navigating to Purchase Order page...")
            self.go_to_purchase_order()
            print("[DEBUG] Opening Add Purchase Order modal...")
            self.open_add_purchase_order_page()
            self.log("Purchase Order modal opened successfully.")
            time.sleep(3)

            print("[DEBUG] Selecting supplier...")
            self.select_supplier("ABC")
            print("[DEBUG] Selecting store...")
            self.select_store("DISPENSARY")
            time.sleep(1)

            print("[DEBUG] Setting delivery date...")
            self.delivery_date_fun("2025-11-11")
            print("[DEBUG] Delivery date function completed.")

            print("[DEBUG] Setting Prepared By...")
            self.prepared_by_fun("rachit")
            print("[DEBUG] Prepared By field completed.")
            
            print("[DEBUG] Setting credit days...")
            self.Credit_days_fun("120")
            print("[DEBUG] Credit days function completed.")

            print("[DEBUG] Setting Payment Term...")
            self.Payment_term_fun("CASH") 
            print("[DEBUG] Payment Term field completed.")
            
            print("[DEBUG] Setting CC-charge...")
            self.select_cc_charge("Exclusive") 
            print("[DEBUG] CC Charge field completed.")

            print("[DEBUG] Setting Discount On...")
            self.select_discount_on("After CC")
            print("[DEBUG] Discount On field completed.")

            self.tick_checkbox("tax_on_free_active")

            self.select_catalogue("PAR10")

        except Exception as e:
            self.log(f"Error loading dashboard: {e}")
            traceback.print_exc()
        finally:
            print("[DEBUG] Closing browser...")
            time.sleep(2)
            self.quit()


    def go_to_purchase_order(self):
        """Navigate to Purchase Order from sidebar."""
        try:
            print("[DEBUG] Checking sidebar toggle...")
            try:
                toggle_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.sidebar-toggle"))
                )
                if toggle_button.get_attribute("aria-expanded") == "false":
                    toggle_button.click()
                    self.log("Sidebar expanded.")
                    print("[DEBUG] Sidebar expanded.")
                    time.sleep(1)
            except Exception:
                self.log("Sidebar toggle not found or already expanded.")
                print("[DEBUG] Sidebar toggle skipped.")

            print("[DEBUG] Clicking Purchase Order link...")
            purchase_order_link = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Purchase Order']"))
            )
            purchase_order_link.click()
            self.log("Navigated to Purchase Order page.")
            print("[DEBUG] Navigated to Purchase Order page.")
            time.sleep(3)

        except Exception as e:
            self.log(f"Error navigating to Purchase Order: {e}")
            traceback.print_exc()

    def open_add_purchase_order_page(self):
        """Click 'Add New' button and wait for the Purchase Order creation page."""
        try:
            self.log("Attempting to open 'Add New Purchase Order' page...")
            print("[DEBUG] Waiting for 'Add New' button...")
            add_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "addPurchaseOrder"))
            )
            add_button.click()
            self.log("Clicked 'Add New Purchase Order' button.")
            print("[DEBUG] 'Add New' button clicked.")

            # Wait until the URL changes or a page element of the new page is visible
            WebDriverWait(self.driver, 10).until(
                EC.url_contains("/phar/pharmacy/purchase_order/create")
            )
            self.log("Purchase Order page loaded successfully.")
            print("[DEBUG] Purchase Order page loaded.")
            time.sleep(1)

        except Exception as e:
            self.log(f"Error opening Add Purchase Order page: {e}")
            traceback.print_exc()

    
    def select_supplier(self, supplier_name):
        """Select a supplier by typing and pressing ENTER."""
        try:
            self.log(f"Selecting supplier: {supplier_name}")
            print("[DEBUG] Locating multiselect span...")
            multiselect_span = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@class='multiselect custom-widthed-multiselect']//div[@class='multiselect__tags']")
                )
            )
            multiselect_span.click()
            print("[DEBUG] Multiselect span clicked.")
            self.log("Clicked multiselect span to activate input.")
            time.sleep(0.5)

            print("[DEBUG] Locating hidden supplier input...")
            input_field = self.driver.find_element(
                By.XPATH,
                "//div[@class='multiselect custom-widthed-multiselect']//input[@name='supplier']"
            )

            print("[DEBUG] Focusing hidden input via JS...")
            self.driver.execute_script("arguments[0].focus();", input_field)
            time.sleep(0.2)

            print(f"[DEBUG] Typing supplier: {supplier_name}")
            input_field.send_keys(supplier_name)
            time.sleep(0.5)

            input_field.send_keys(Keys.ENTER)
            self.log(f"Supplier '{supplier_name}' selected successfully via typing.")
            print("[DEBUG] Supplier selection done.")
            time.sleep(0.5)

        except Exception as e:
            self.log(f"Error selecting supplier: {e}")
            traceback.print_exc()
            
    def select_store(self, store_name):
        """Select a store from the multiselect dropdown."""
        try:
            self.log(f"Selecting store: {store_name}")
            print(f"[DEBUG] Selecting store: {store_name}")

            wait = WebDriverWait(self.driver, 10)

            store_dropdown = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//label[contains(., 'Store')]/following::div[contains(@class, 'multiselect')][1]"
                ))
            )
            store_dropdown.click()
            print("[DEBUG] Store dropdown clicked.")
            self.log("Clicked on store dropdown to open options.")
            time.sleep(0.5)

            store_input = wait.until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//input[@class='multiselect__input' and @placeholder='Select Store']"
                ))
            )
            self.driver.execute_script("arguments[0].focus();", store_input)
            print("[DEBUG] Store input focused.")
            time.sleep(0.2)

            store_input.send_keys(store_name)
            time.sleep(0.5)
            store_input.send_keys(Keys.ENTER)
            self.log(f"Store '{store_name}' selected successfully.")
            print("[DEBUG] Store selection done.")
            time.sleep(0.5)

        except Exception as e:
            self.log(f"Error selecting store: {e}")
            traceback.print_exc()

    def delivery_date_fun(self, delivery_date):
        """
        Set the delivery date properly for Vue-validated input.
        """
        try:
            print("[DEBUG] Locating delivery date input...")
            delivery_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "delivery_date"))
            )
            print("[DEBUG] Delivery input located.")

            self.driver.execute_script("""
                const el = arguments[0];
                const value = arguments[1];
                el.value = value;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            """, delivery_input, delivery_date)
            print(f"[DEBUG] Delivery date set via JS: {delivery_date}")

            self.driver.execute_script(
                "arguments[0].dispatchEvent(new KeyboardEvent('keydown', {'key': 'Enter'}));",
                delivery_input
            )
            print("[DEBUG] Enter key dispatched to delivery input.")
            self.log(f"Delivery date set to: {delivery_date}")
            time.sleep(0.5)

        except Exception as e:
            self.log(f"Error selecting delivery date: {e}")
            traceback.print_exc()

    def prepared_by_fun(self, prepared_name):
        """
        Type the 'Prepared By' name into the input and press Enter, Vue-friendly.
        """
        try:
            self.log(f"Setting Prepared By: {prepared_name}")
            prepared_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "prepared_by"))
            )

            # Clear existing value via JS
            self.driver.execute_script("""
                const el = arguments[0];
                el.value = '';
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            """, prepared_input)
            time.sleep(0.2)

            # Type the new value
            prepared_input.send_keys(prepared_name)
            self.driver.execute_script("""
                const el = arguments[0];
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            """, prepared_input)
            time.sleep(0.2)

            # Press Enter
            prepared_input.send_keys(Keys.ENTER)
            self.log(f"'Prepared By' set successfully: {prepared_name}")

        except Exception as e:
            self.log(f"Error setting 'Prepared By': {e}")
            traceback.print_exc()



    def Credit_days_fun(self, Credit_days):
        """
        Set the credit_days select input for a Vue-controlled dropdown.
        Credit_days must be a string matching the <option> value, e.g., "120", "90", "60".
        """
        try:
            select_element = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.ID, "credit_days"))
            )

            # Scroll into view and click
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select_element)
            time.sleep(0.2)
            select_element.click()  # ensures focus and dropdown opens
            time.sleep(0.2)

            # Set value via JS for Vue reactivity
            self.driver.execute_script("""
                const el = arguments[0];
                const value = arguments[1];
                el.value = value;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            """, select_element, str(Credit_days))

            self.log(f"Credit days successfully set to: {Credit_days}")

        except Exception as e:
            self.log(f"Error selecting credit days: {e}")
            traceback.print_exc()

    def Payment_term_fun(self, visible_text):
        """
        Set the Payment Term select input for Vue-controlled dropdown.
        """
        try:
            self.log(f"Setting Payment Term: {visible_text}")

            # Wait for the select element
            select_element = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "payment_term"))
            )

            # Scroll into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select_element)
            time.sleep(0.2)

            # Map visible text to option value
            options = select_element.find_elements(By.TAG_NAME, "option")
            value_to_select = None
            for option in options:
                if option.text.strip().upper() == visible_text.upper():
                    value_to_select = option.get_attribute("value")
                    break

            if not value_to_select:
                raise Exception(f"No Payment Term option matches '{visible_text}'")

            # Set the value via JS and trigger Vue reactivity
            self.driver.execute_script("""
                const select = arguments[0];
                const value = arguments[1];
                select.value = value;
                select.dispatchEvent(new Event('input', { bubbles: true }));
                select.dispatchEvent(new Event('change', { bubbles: true }));
            """, select_element, value_to_select)

            self.log(f"Payment Term successfully set to: {visible_text}")
            print(f"[DEBUG] Payment Term set to: {visible_text}")

            time.sleep(0.3)

        except Exception as e:
            self.log(f"Error setting Payment Term: {e}")
            traceback.print_exc()

    def select_cc_charge(self, cc_value):
        """Select a CC Charge from the multiselect dropdown."""
        try:
            self.log(f"Selecting CC Charge: {cc_value}")
            print(f"[DEBUG] Selecting CC Charge: {cc_value}")

            wait = WebDriverWait(self.driver, 10)

            # Step 1: Click the multiselect container
            cc_dropdown = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//label[contains(., 'CC Charge')]/following::div[contains(@class, 'multiselect')][1]"
                ))
            )
            cc_dropdown.click()
            print("[DEBUG] CC Charge dropdown clicked.")
            time.sleep(0.3)

            # Step 2: Locate the input inside the container
            cc_input = cc_dropdown.find_element(By.CSS_SELECTOR, "input.multiselect__input")
            self.driver.execute_script("arguments[0].focus();", cc_input)
            print("[DEBUG] CC Charge input focused.")
            time.sleep(0.2)

            # Step 3: Type value and press Enter
            cc_input.send_keys(cc_value)
            time.sleep(0.5)
            cc_input.send_keys(Keys.ENTER)

            self.log(f"CC Charge '{cc_value}' selected successfully.")
            print("[DEBUG] CC Charge selection done.")
            time.sleep(0.5)

        except Exception as e:
            self.log(f"Error selecting CC Charge: {e}")
            traceback.print_exc()


    def select_discount_on(self, discount_value):
        """Select a value from the 'Discount On' multiselect dropdown."""
        try:
            self.log(f"Selecting Discount On: {discount_value}")
            print(f"[DEBUG] Selecting Discount On: {discount_value}")

            wait = WebDriverWait(self.driver, 10)

            # Step 1: Click the multiselect container to open options
            discount_container = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//div[@class='multiselect__tags' and ./span[contains(@class,'multiselect__single')]]"
                ))
            )
            discount_container.click()
            print("[DEBUG] Discount On dropdown clicked.")
            time.sleep(0.5)  # wait for options to render

            # Step 2: Wait for all visible options to appear
            options = wait.until(
                EC.visibility_of_all_elements_located((
                    By.XPATH,
                    "//div[contains(@class,'multiselect__option')]"
                ))
            )

            # Step 3: Loop through options and click the matching one
            matched = False
            for opt in options:
                if opt.text.strip() == discount_value:
                    opt.click()
                    matched = True
                    break

            if not matched:
                raise Exception(f"Discount On option '{discount_value}' not found.")

            self.log(f"Discount On '{discount_value}' selected successfully.")
            print("[DEBUG] Discount On selection done.")
            time.sleep(0.3)

        except Exception as e:
            self.log(f"Error selecting Discount On: {e}")
            traceback.print_exc()
    def tick_checkbox(self, checkbox_id):
        """
        Tick a checkbox by its input ID if not already checked.
        
        :param checkbox_id: The 'id' attribute of the checkbox input.
        """
        try:
            self.log(f"Toggling checkbox: {checkbox_id}")
            print(f"[DEBUG] Toggling checkbox: {checkbox_id}")

            wait = WebDriverWait(self.driver, 10)

            # Step 1: Locate the checkbox input
            checkbox = wait.until(
                EC.presence_of_element_located((By.ID, checkbox_id))
            )

            # Step 2: Check if already selected
            if not checkbox.is_selected():
                # Click the checkbox using JavaScript to avoid overlay issues
                self.driver.execute_script("arguments[0].click();", checkbox)
                self.log(f"Checkbox '{checkbox_id}' ticked successfully.")
                print(f"[DEBUG] Checkbox '{checkbox_id}' ticked.")
            else:
                self.log(f"Checkbox '{checkbox_id}' was already ticked.")
                print(f"[DEBUG] Checkbox '{checkbox_id}' already ticked.")

            time.sleep(0.3)

        except Exception as e:
            self.log(f"Error ticking checkbox '{checkbox_id}': {e}")
            traceback.print_exc()

    def select_catalogue(self, catalogue_name):
        """Select a catalogue by typing, ticking the checkbox, and confirming."""
        try:
            self.log(f"Selecting catalogue: {catalogue_name}")
            print("[DEBUG] Locating Catalogue multiselect container...")

            # Click the main container (not the text span)
            multiselect_container = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[contains(@class, 'multiselect__tags') and .//span[contains(., 'Select Catalogue')]]")
                )
            )
            multiselect_container.click()
            print("[DEBUG] Catalogue dropdown clicked.")
            self.log("Clicked Catalogue dropdown to activate input.")
            time.sleep(0.5)

            # Locate the hidden input field (by placeholder)
            print("[DEBUG] Locating hidden Catalogue input...")
            input_field = self.driver.find_element(
                By.XPATH,
                "//input[@class='multiselect__input' and @placeholder='Select Catalogue']"
            )

            # Focus via JavaScript
            print("[DEBUG] Focusing hidden Catalogue input via JS...")
            self.driver.execute_script("arguments[0].focus();", input_field)
            time.sleep(0.3)

            # Type the catalogue name
            print(f"[DEBUG] Typing Catalogue: {catalogue_name}")
            input_field.send_keys(catalogue_name)
            time.sleep(1)

            # Wait for dropdown option and click it (tick checkbox)
            print("[DEBUG] Waiting for catalogue option to appear...")
            option_xpath = f"//span[contains(@class,'multiselect__option')][contains(., '{catalogue_name}')]"
            option_element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, option_xpath))
            )
            option_element.click()
            print(f"[DEBUG] Catalogue '{catalogue_name}' checkbox clicked.")

            # Close dropdown (press ENTER)
            input_field.send_keys(Keys.ENTER)
            self.log(f"Catalogue '{catalogue_name}' selected successfully.")
            print("[DEBUG] Catalogue selection completed.")
            time.sleep(0.5)

        except Exception as e:
            self.log(f"Error selecting catalogue: {e}")
            print(f"[ERROR] {e}")
            traceback.print_exc()

# Entry point
if __name__ == "__main__":
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    bot = PurchaseOrder(username, password)
    bot.load_dashboard()
