import time
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from core_setup import BaseCanteenAutomation


class PurchaseOrder(BaseCanteenAutomation):
    def load_dashboard(self):
        try:
            self.init_driver()
            self.login()
            self.log("Dashboard loaded.")
            time.sleep(2)

            # Go to Purchase Order page
            self.go_to_purchase_order()

            # Apply filter and optional search
            self.filter_purchase_order(
                requisition_status="All",
                from_date="2025-11-04",
                to_date="2025-11-06",
                search_term="Astha Bhandari (Mavorion)"
            )

            self.log("Purchase Order filtered and search executed.")
            time.sleep(1)

        except Exception as e:
            self.log(f"Error loading dashboard: {e}")
            traceback.print_exc()
        finally:
            self.quit()

    def go_to_purchase_order(self):
        """Navigate to Purchase Order from sidebar."""
        try:
            # Expand sidebar if collapsed
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

            # Click Purchase Order link
            purchase_order_link = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Purchase Order']"))
            )
            purchase_order_link.click()
            self.log("Navigated to Purchase Order page.")
            time.sleep(3)

        except Exception as e:
            self.log(f"Error navigating to Purchase Order: {e}")
            traceback.print_exc()

    def filter_purchase_order(self, requisition_status: str, from_date: str, to_date: str, search_term: str = ""):
        """Filter Purchase Orders and optionally search, then click View Detail."""
        try:
            # --- Select requisition status ---
            dropdown = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.ID, "requisition_status"))
            )
            Select(dropdown).select_by_visible_text(requisition_status)
            self.log(f"Selected requisition_status: {requisition_status}")
            time.sleep(0.5)

            # --- Fill From date ---
            from_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "date-range-from"))
            )
            from_input.clear()
            from_input.send_keys(from_date)
            self.log(f"From date set to: {from_date}")
            time.sleep(0.5)

            # --- Fill To date ---
            to_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "date-range-to"))
            )
            to_input.clear()
            to_input.send_keys(to_date)
            self.log(f"To date set to: {to_date}")
            time.sleep(0.5)

            # --- Click main Search button ---
            search_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'btn-success') and .//span[@class='fa fa-search']]"))
            )
            search_button.click()
            self.log("Main Search button clicked.")
            time.sleep(3)  # wait for table to refresh

            # --- Optional search in table ---
            if search_term:
                search_input = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "#purchase-order-table_filter input[type='search']"))
                )
                search_input.clear()
                search_input.send_keys(search_term)
                self.driver.execute_script(
                    "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
                    search_input
                )
                self.log(f"Searched table with term: '{search_term}'")
                time.sleep(2)

            # --- Check if table has data ---
            table_empty = self.driver.find_elements(By.CSS_SELECTOR, "#purchase-order-table .dataTables_empty")
            if table_empty and "No data available" in table_empty[0].text:
                self.log("No data available in the table. Quitting Chrome.")
                self.quit()  # Immediately close the browser
                return  # Exit the function

            # --- Click first "View Detail" button ---
            view_detail_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'View Detail')]"))
            )
            view_detail_btn.click()
            self.log("Clicked 'View Detail' button successfully.")
            time.sleep(2)

        except Exception as e:
            self.log(f"Error filtering purchase order or clicking buttons: {e}")
            traceback.print_exc()
    def create_purchase_order(self):
        """Placeholder for creating a new purchase order."""
        self.log("Creating a new purchase order...")
        # Here you would implement the logic to create a new purchase order
        
        pass


# Entry point
if __name__ == "__main__":
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    bot = PurchaseOrder(username, password)
    bot.load_dashboard()
