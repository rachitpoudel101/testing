import time
import traceback
from core_setup import BaseCanteenAutomation
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
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
            self.delivery_date_fun("2025-11-10")
            print("[DEBUG] Delivery date function completed.")

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


# Entry point
if __name__ == "__main__":
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    bot = PurchaseOrder(username, password)
    bot.load_dashboard()
