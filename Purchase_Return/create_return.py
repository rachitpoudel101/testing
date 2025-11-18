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
from core.core_setup import BaseAutomation,PURCHASE_RETURN_URL


class PurchaseReturn(BaseAutomation):
    def load_dashboard(self):
        """Load dashboard and fill Purchase Order dynamically from input_data dict."""
        try:
            self.init_driver()
            self.login()
            self.log("Dashboard loaded.")
            time.sleep(2)
            self.driver.get(PURCHASE_RETURN_URL)
            self.log("Navigated to Purchase Return page.")
            time.sleep(2)
            self.select_supplier("ABC")
        except Exception as e:
            self.log(f"[ERROR] Exception during load_dashboard: {e}")
            self.log(traceback.format_exc())
        finally:
            if self.driver:
                self.driver.quit()
                self.log("Driver closed.")

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

                
if __name__ == "__main__":
    # Example usage
    automation = PurchaseReturn("rachit", "Rachit@123")
    automation.load_dashboard()