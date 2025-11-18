import sys
import os
import time
import traceback
from faker import Faker
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Adjust system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.core_setup import BaseCanteenAutomation


# ✅ Initialize Faker
fake = Faker('en_IN')  # Use Indian locale (close to Nepali data style)


def collect_inputs(use_faker=True):
    """Collect all Purchase Order fields dynamically or generate with Faker."""
    data = {}

    if use_faker:
        print("[INFO] Generating fake data using Faker...")

        data['supplier'] = fake.company()
        data['store'] = fake.city()
        data['delivery_date'] = fake.date_this_year().strftime("%Y-%m-%d")
        data['prepared_by'] = fake.name()
        data['credit_days'] = str(fake.random_element(elements=("30", "60", "90", "120")))
        data['payment_term'] = fake.random_element(elements=("CASH", "BT", "AFDL"))
        data['cc_charge'] = fake.random_element(elements=("Included", "Excluded"))
        data['discount_on'] = fake.random_element(elements=("Before", "After"))
        data['tax_on_free_active'] = fake.boolean(chance_of_getting_true=50)
        data['catalogue'] = fake.word().capitalize()
        data['unit_quantity'] = str(fake.random_int(min=1, max=50))
        data['unit_bonus'] = str(fake.random_int(min=0, max=10))
        data['tax'] = f"{round(random.uniform(0, 13), 1)}%"
        data['remarks'] = fake.sentence(nb_words=6)
        data['terms_condition'] = fake.text(max_nb_chars=100)
        data['last_remarks'] = fake.sentence(nb_words=8)

    else:
        print("[INFO] Manual input mode active...")
        data['supplier'] = input("Enter Supplier: ")
        data['store'] = input("Enter Store: ")
        data['delivery_date'] = input("Enter Delivery Date (YYYY-MM-DD): ")
        data['prepared_by'] = input("Enter Prepared By: ")
        data['credit_days'] = input("Enter Credit Days (e.g., 120): ")
        data['payment_term'] = input("Enter Payment Term (e.g., CASH): ")
        data['cc_charge'] = input("Enter CC Charge: ")
        data['discount_on'] = input("Enter Discount On value: ")
        tax_checkbox = input("Enable Tax On Free? (yes/no): ").strip().lower()
        data['tax_on_free_active'] = True if tax_checkbox in ['yes', 'y'] else False
        data['catalogue'] = input("Enter Catalogue: ")
        data['unit_quantity'] = input("Enter Unit Quantity: ")
        data['unit_bonus'] = input("Enter Unit Bonus: ")
        data['tax'] = input("Enter Tax (e.g., 13%): ")
        data['remarks'] = input("Enter Remarks: ")
        data['terms_condition'] = input("Enter Terms & Conditions: ")
        data['last_remarks'] = input("Enter Final Remarks: ")

    print("\n[DEBUG] Generated Input Data:")
    for key, val in data.items():
        print(f"  {key}: {val}")

    return data
class PurchaseOrder(BaseCanteenAutomation):

    def load_dashboard(self, input_data=None):
        """Load dashboard and fill Purchase Order dynamically from input_data dict."""
        try:
            self.init_driver()
            self.login()
            self.log("Dashboard loaded.")
            time.sleep(2)
            self.go_to_purchase_order()
            self.open_add_purchase_order_page()
            time.sleep(3)

            if input_data:
                self.select_supplier(input_data.get('supplier'))
                self.select_store(input_data.get('store'))
                time.sleep(1)
                self.delivery_date_fun(input_data.get('delivery_date'))
                self.prepared_by_fun(input_data.get('prepared_by'))
                self.Credit_days_fun(input_data.get('credit_days'))
                self.Payment_term_fun(input_data.get('payment_term'))
                self.select_cc_charge(input_data.get('cc_charge'))
                self.select_discount_on(input_data.get('discount_on'))

                # Handle checkbox
                if input_data.get('tax_on_free_active'):
                    self.tick_checkbox("tax_on_free_active")

                self.select_catalogue(input_data.get('catalogue'))
                self.unit_quantity(input_data.get('unit_quantity'))
                self.unit_bonus(input_data.get('unit_bonus'))
                self.tax(input_data.get('tax'))
                self.remarks(input_data.get('remarks'))
                self.click_add_btn()
                self.terms_condition(input_data.get('terms_condition'))
                self.last_remarks(input_data.get('last_remarks'))
            else:
                self.log("No input_data provided; skipping dynamic form filling.")

        except Exception as e:
            self.log(f"Error loading dashboard: {e}")
            traceback.print_exc()
        finally:
            time.sleep(2)
            self.quit()



    def go_to_purchase_order(self):
        """Navigate to Purchase Order from sidebar."""
        try:
            try:
                toggle_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.sidebar-toggle"))
                )
                if toggle_button.get_attribute("aria-expanded") == "false":
                    toggle_button.click()
                    self.log("Sidebar expanded.")
                    time.sleep(1)
            except Exception:
                self.log("Sidebar toggle not found or already expanded.")
            purchase_order_link = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Purchase Order']"))
            )
            purchase_order_link.click()
            self.log("Navigated to Purchase Order page.")
            time.sleep(3)

        except Exception as e:
            self.log(f"Error navigating to Purchase Order: {e}")
            traceback.print_exc()


    def open_add_purchase_order_page(self):
        """Click 'Add New' button and wait for the Purchase Order creation page."""
        try:
            self.log("Attempting to open 'Add New Purchase Order' page...")
            add_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "addPurchaseOrder"))
            )
            add_button.click()
            self.log("Clicked 'Add New Purchase Order' button.")

            # Wait until the URL changes or a page element of the new page is visible
            WebDriverWait(self.driver, 10).until(
                EC.url_contains("/phar/pharmacy/purchase_order/create")
            )
            self.log("Purchase Order page loaded successfully.")
            time.sleep(1)

        except Exception as e:
            self.log(f"Error opening Add Purchase Order page: {e}")
            traceback.print_exc()


    def select_supplier(self, supplier_name):
        """Select a supplier by typing and pressing ENTER."""
        try:
            self.log(f"Selecting supplier: {supplier_name}")
            multiselect_span = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@class='multiselect custom-widthed-multiselect']//div[@class='multiselect__tags']")
                )
            )
            multiselect_span.click()
            self.log("Clicked multiselect span to activate input.")
            time.sleep(0.5)
            input_field = self.driver.find_element(
                By.XPATH,
                "//div[@class='multiselect custom-widthed-multiselect']//input[@name='supplier']"
            )
            self.driver.execute_script("arguments[0].focus();", input_field)
            time.sleep(0.2)
            input_field.send_keys(supplier_name)
            time.sleep(0.5)

            input_field.send_keys(Keys.ENTER)
            self.log(f"Supplier '{supplier_name}' selected successfully via typing.")
            time.sleep(0.5)

        except Exception as e:
            self.log(f"Error selecting supplier: {e}")
            traceback.print_exc()


    def select_store(self, store_name):
        """Select a store from the multiselect dropdown."""
        try:
            self.log(f"Selecting store: {store_name}")

            wait = WebDriverWait(self.driver, 10)

            store_dropdown = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//label[contains(., 'Store')]/following::div[contains(@class, 'multiselect')][1]"
                ))
            )
            store_dropdown.click()
            self.log("Clicked on store dropdown to open options.")
            time.sleep(0.5)

            store_input = wait.until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//input[@class='multiselect__input' and @placeholder='Select Store']"
                ))
            )
            self.driver.execute_script("arguments[0].focus();", store_input)
            time.sleep(0.2)

            store_input.send_keys(store_name)
            time.sleep(0.5)
            store_input.send_keys(Keys.ENTER)
            self.log(f"Store '{store_name}' selected successfully.")
            time.sleep(0.5)

        except Exception as e:
            self.log(f"Error selecting store: {e}")
            traceback.print_exc()


    def delivery_date_fun(self, delivery_date):
        """
        Set the delivery date properly for Vue-validated input.
        """
        try:
            delivery_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "delivery_date"))
            )

            self.driver.execute_script("""
                const el = arguments[0];
                const value = arguments[1];
                el.value = value;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            """, delivery_input, delivery_date)

            self.driver.execute_script(
                "arguments[0].dispatchEvent(new KeyboardEvent('keydown', {'key': 'Enter'}));",
                delivery_input
            )
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

            time.sleep(0.3)

        except Exception as e:
            self.log(f"Error setting Payment Term: {e}")
            traceback.print_exc()


    def select_cc_charge(self, cc_value):
        """Select a CC Charge from the multiselect dropdown."""
        try:
            self.log(f"Selecting CC Charge: {cc_value}")

            wait = WebDriverWait(self.driver, 10)

            # Step 1: Click the multiselect container
            cc_dropdown = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//label[contains(., 'CC Charge')]/following::div[contains(@class, 'multiselect')][1]"
                ))
            )
            cc_dropdown.click()
            time.sleep(0.3)

            # Step 2: Locate the input inside the container
            cc_input = cc_dropdown.find_element(By.CSS_SELECTOR, "input.multiselect__input")
            self.driver.execute_script("arguments[0].focus();", cc_input)
            time.sleep(0.2)

            # Step 3: Type value and press Enter
            cc_input.send_keys(cc_value)
            time.sleep(0.5)
            cc_input.send_keys(Keys.ENTER)

            self.log(f"CC Charge '{cc_value}' selected successfully.")
            time.sleep(0.5)

        except Exception as e:
            self.log(f"Error selecting CC Charge: {e}")
            traceback.print_exc()


    def select_discount_on(self, discount_value):
        """Select a value from the 'Discount On' multiselect dropdown (Vue version)."""
        try:
            self.log(f"Selecting Discount On: {discount_value}")

            wait = WebDriverWait(self.driver, 10)

            # Step 1: Click the input field directly (instead of parent span)
            discount_input = wait.until(
                EC.element_to_be_clickable((By.ID, "discount_on"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", discount_input)
            discount_input.click()
            time.sleep(0.3)

            # Step 2: Type the desired value
            discount_input.clear()
            discount_input.send_keys(discount_value)
            time.sleep(0.5)

            # Step 3: Wait for dropdown options and pick match
            options = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//span[contains(@class,'multiselect__option')]"))
            )

            matched = False
            for opt in options:
                if discount_value.lower() in opt.text.strip().lower():
                    opt.click()
                    matched = True
                    break

            if not matched:
                raise Exception(f"Discount On option '{discount_value}' not found.")

            self.log(f"Discount On '{discount_value}' selected successfully.")
            time.sleep(0.5)

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
            else:
                self.log(f"Checkbox '{checkbox_id}' was already ticked.")

            time.sleep(0.3)

        except Exception as e:
            self.log(f"Error ticking checkbox '{checkbox_id}': {e}")
            traceback.print_exc()


    def select_catalogue(self, catalogue_name):
        """Select a catalogue from the Vue multiselect dropdown where Enter key is required."""
        try:
            self.log(f"Selecting catalogue: {catalogue_name}")

            wait = WebDriverWait(self.driver, 10)

            # Step 1: Click the multiselect container to open dropdown
            catalogue_dropdown = wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    "div.input-group.custom-widthed-multiselect div.multiselect__tags"
                ))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", catalogue_dropdown)
            time.sleep(1)
            catalogue_dropdown.click()
            self.log("Clicked on catalogue dropdown to open options.")
            time.sleep(0.5)

            # Step 2: Focus on the input field inside the dropdown
            catalogue_input = wait.until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "div.input-group.custom-widthed-multiselect input[placeholder='Select Catalogue']"
                ))
            )
            self.driver.execute_script("arguments[0].focus();", catalogue_input)
            time.sleep(0.2)

            # Step 3: Type catalogue name and press Enter
            catalogue_input.clear()
            catalogue_input.send_keys(catalogue_name)
            time.sleep(2)

            catalogue_input.send_keys(Keys.ENTER)
            self.log(f"Catalogue '{catalogue_name}' selected successfully.")
            time.sleep(0.5)
        except Exception as e:
            self.log(f"Error selecting catalogue: {e}")
            traceback.print_exc()


    def unit_quantity(self,unit_value):
        """Set the unit for an item in the purchase order."""
        try:
            self.log(f"Setting unit: {unit_value}")

            wait = WebDriverWait(self.driver, 5)

            unit_dropdown = wait.until(
                EC.element_to_be_clickable((By.ID, "selected_in_box"))
            )
            unit_dropdown.click()
    
            unit_input = wait.until(
                EC.presence_of_element_located((By.ID, "selected_in_box"))
            )
            self.driver.execute_script("arguments[0].focus();", unit_input)


            unit_input.send_keys(unit_value)
            time.sleep(0.5)
            unit_input.send_keys(Keys.ENTER)

            self.log(f"Unit '{unit_value}' selected successfully.")
            time.sleep(0.5)
        except Exception as e:
            self.log(f"Error setting unit: {e}")
            traceback.print_exc()


    def unit_bonus(self,unit_bonus_value):
        """Set the unit for an item in the purchase order."""
        try:
            self.log(f"Setting unit: {unit_bonus_value}")
            wait = WebDriverWait(self.driver, 5)

            unit_dropdown = wait.until(
                EC.element_to_be_clickable((By.ID, "selected_unit_bonus"))
            )
            unit_dropdown.click()
            unit_input = wait.until(
                EC.presence_of_element_located((By.ID, "selected_unit_bonus"))
            )   
            self.driver.execute_script("arguments[0].focus();", unit_input)
            unit_input.clear()
            unit_input.send_keys(unit_bonus_value)
            time.sleep(2)
            unit_input.send_keys(Keys.ENTER)
            self.log(f"Unit '{unit_bonus_value}' selected successfully.")
            time.sleep(2)
        except Exception as e:
            self.log(f"Error setting unit: {e}")
            traceback.print_exc()


    def tax(self,tax_value):
        """Set the tax for an item in the purchase order."""
        try:
            self.log(f"Setting tax: {tax_value}")
            wait = WebDriverWait(self.driver, 5)

            tax_dropdown = wait.until(
                EC.element_to_be_clickable((By.ID, "selected_item_tax"))
            )
            tax_dropdown.click()
            tax_input = wait.until(
                EC.presence_of_element_located((By.ID, "selected_item_tax"))
            )   
            self.driver.execute_script("arguments[0].focus();", tax_input)
            tax_input.clear() 
            tax_input.send_keys(tax_value)
            time.sleep(0.5)
            tax_input.send_keys(Keys.ENTER)
            self.log(f"Tax '{tax_value}' selected successfully.")
            time.sleep(0.5)
        except Exception as e:
            self.log(f"Error setting tax: {e}")
            traceback.print_exc()


    def remarks(self,remarks_value):
        """Set the remarks for an item in the purchase order."""
        try:
            self.log(f"Setting remarks: {remarks_value}")
            wait = WebDriverWait(self.driver, 5)

            remarks_input = wait.until(
                EC.element_to_be_clickable((By.ID, "selected_item_remarks"))
            )
            self.driver.execute_script("arguments[0].focus();", remarks_input)
            remarks_input.clear()
            remarks_input.send_keys(remarks_value)
            time.sleep(0.5)
            self.log(f"Remarks '{remarks_value}' entered successfully.")
            time.sleep(0.5)
        except Exception as e:
            self.log(f"Error setting remarks: {e}")
            traceback.print_exc()


    def click_add_btn(self):
        """Click the Add button to add the item to the purchase order."""
        try:
            self.log("Clicking Add button to add item.")

            wait = WebDriverWait(self.driver, 5)

            add_button = wait.until(
                EC.element_to_be_clickable((By.ID, "add_item"))
            )
            add_button.click()
            self.log("Add button clicked successfully.")
            time.sleep(1)
        except Exception as e:
            self.log(f"Error clicking Add button: {e}")
            traceback.print_exc()


    def terms_condition(self, terms_value):
        """Set Terms and Conditions textarea."""
        try:
            self.log(f"Setting Terms and Conditions: {terms_value}")
            wait = WebDriverWait(self.driver, 5)

            # Locate textarea by its preceding label text
            terms_input = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//label[contains(text(),'Terms And Conditions')]/following-sibling::textarea"
                ))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", terms_input)
            self.driver.execute_script("arguments[0].focus();", terms_input)
            terms_input.clear()
            terms_input.send_keys(terms_value)
            time.sleep(0.5)
            self.log(f"Terms and Conditions entered successfully.")
            time.sleep(0.5)

        except Exception as e:
            self.log(f"Error setting Terms and Conditions: {e}")
            traceback.print_exc()
            

    def last_remarks(self, remarks_value):
        """Set Remarks textarea."""
        try:
            self.log(f"Setting Remarks: {remarks_value}")
            wait = WebDriverWait(self.driver, 5)

            # Locate textarea by its preceding label text
            remarks_input = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//label[contains(text(),'Remarks')]/following-sibling::textarea"
                ))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", remarks_input)
            self.driver.execute_script("arguments[0].focus();", remarks_input)
            remarks_input.clear()
            remarks_input.send_keys(remarks_value)
            time.sleep(0.5)
            self.log(f"Remarks entered successfully.")
            time.sleep(0.5)

        except Exception as e:
            self.log(f"Error setting Remarks: {e}")
            traceback.print_exc()


if __name__ == "__main__":
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    bot = PurchaseOrder(username, password)

    # ✅ Choose whether to use Faker or manual input
    choice = input("Use Faker data? (yes/no): ").strip().lower()
    use_faker = choice in ['yes', 'y']

    # ✅ Collect input data
    input_data = collect_inputs(use_faker=use_faker)

    # ✅ Run dashboard with input data
    bot.load_dashboard(input_data)