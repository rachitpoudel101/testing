import sys
import os
import time
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Adjust system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.core_setup import BaseAutomation, STOCK_TRANSFER_URL

class StockTransfer(BaseAutomation):

    def load_dashboard(self):
        """Load dashboard and navigate to Stock Transfer page."""
        try:
            self.init_driver()
            self.login()
            self.log("Dashboard loaded.")
            time.sleep(2)
            
            self.driver.get(STOCK_TRANSFER_URL)
            self.log("Navigated to Stock Transfer page.")
            time.sleep(2)
            self.select_vue_multiselect("Select a Store", "ER DISPENSARY")
            time.sleep(1)
            self.select_item("Select Item", "DIC10")
            time.sleep(1)
            self.enter_quantity("transfer_quantity", 50)
            time.sleep(1)
            self.click_button("add")


        except Exception as e:
            self.log(f"[ERROR] Exception during load_dashboard: {e}")
            self.log(traceback.format_exc())
        finally:
            if self.driver:
                self.driver.quit()
                self.log("Driver closed.")

    def select_vue_multiselect(self, placeholder_text, option_text):
        """
        Select an option from a Vue multiselect dropdown reliably.
        """
        try:
            self.log(f"Selecting '{option_text}' from Vue multiselect with placeholder '{placeholder_text}'")
            wait = WebDriverWait(self.driver, 20)

            # STEP 1: Wait for the placeholder span to appear
            placeholder_span = wait.until(
                lambda d: d.find_element(
                    By.XPATH,
                    f"//span[contains(@class,'multiselect__single') and normalize-space(text())='{placeholder_text}']"
                )
            )

            # STEP 2: Get the ancestor multiselect container
            multiselect_box = placeholder_span.find_element(By.XPATH, "./ancestor::div[contains(@class,'multiselect')]")

            # Scroll into view and click to open
            self.driver.execute_script("arguments[0].scrollIntoView(true);", multiselect_box)
            time.sleep(0.3)
            multiselect_box.click()
            time.sleep(0.5)

            # STEP 3: Wait for the input inside the dropdown
            search_input = wait.until(
                lambda d: multiselect_box.find_element(
                    By.XPATH,
                    ".//input[contains(@class,'multiselect__input')]"
                )
            )

            # Make input visible if hidden
            self.driver.execute_script("arguments[0].style.display='block';", search_input)
            search_input.clear()
            search_input.send_keys(option_text)
            time.sleep(0.5)

            # Press Enter to select the option
            search_input.send_keys(Keys.ENTER)
            time.sleep(0.3)

            self.log(f"Option '{option_text}' selected successfully from '{placeholder_text}'")

        except Exception as e:
            self.log(f"[ERROR] Exception in select_vue_multiselect: {e}")
            traceback.print_exc()

    def select_item(self, placeholder_text, item_name):
        """Select an item from a Vue multiselect using placeholder and typing."""
        try:
            self.log(f"Selecting item '{item_name}' from multiselect with placeholder '{placeholder_text}'")

            wait = WebDriverWait(self.driver, 10)

            # Step 1: Locate the multiselect container by input placeholder
            multiselect_container = wait.until(
                lambda d: d.find_element(
                    By.XPATH,
                    f"//input[@placeholder='{placeholder_text}']/ancestor::div[contains(@class,'multiselect')]"
                )
            )

            # Step 2: Click on the tags area to open dropdown
            tags_div = multiselect_container.find_element(By.CLASS_NAME, "multiselect__tags")
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tags_div)
            time.sleep(3)
            tags_div.click()
            time.sleep(3)

            # Step 3: Find the input field and make it visible
            input_field = multiselect_container.find_element(By.XPATH, f".//input[@placeholder='{placeholder_text}']")
            self.driver.execute_script("arguments[0].style.display='block';", input_field)
            input_field.clear()
            input_field.send_keys(item_name)
            time.sleep(3)

            # Step 4: Press Enter to select
            input_field.send_keys(Keys.ENTER)
            self.log(f"Item '{item_name}' selected successfully from '{placeholder_text}'")
            time.sleep(3)

        except Exception as e:
            self.log(f"[ERROR] Exception in select_item: {e}")
            traceback.print_exc()

    def enter_quantity(self, field_id, quantity):
        """
        Enter a numeric quantity into an input field.
        
        Args:
            field_id (str): The `id` of the input field.
            quantity (int/float/str): The value to enter.
        """
        try:
            self.log(f"Entering quantity '{quantity}' into field with id '{field_id}'")

            wait = WebDriverWait(self.driver, 10)

            # Locate the input field by id
            input_field = wait.until(
                lambda d: d.find_element(By.ID, field_id)
            )

            # Scroll into view
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", input_field)
            time.sleep(0.2)

            # Clear any existing value and enter new quantity
            input_field.clear()
            input_field.send_keys(str(quantity))
            time.sleep(0.2)

            self.log(f"Quantity '{quantity}' entered successfully in '{field_id}'")

        except Exception as e:
            self.log(f"[ERROR] Exception in enter_quantity: {e}")
            traceback.print_exc()

    def click_button(self, button_id):
        """
        Click a button by its ID.

        Args:
            button_id (str): The `id` of the button to click.
        """
        try:
            self.log(f"Clicking button with id '{button_id}'")

            wait = WebDriverWait(self.driver, 10)

            # Locate the button by id
            button = wait.until(
                lambda d: d.find_element(By.ID, button_id)
            )

            # Scroll into view and click
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", button)
            time.sleep(0.2)
            button.click()
            time.sleep(0.3)

            self.log(f"Button '{button_id}' clicked successfully")

        except Exception as e:
            self.log(f"[ERROR] Exception in click_button: {e}")
            traceback.print_exc()


if __name__ == "__main__":
    automation = StockTransfer("rachit", "Rachit@123")
    automation.load_dashboard()
