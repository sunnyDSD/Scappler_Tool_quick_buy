from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import json


# Load credentials
def load_credentials(path="config/credentials.json"):
    """Loads credentials for purchase automation."""
    try:
        with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("❌ Error: credentials.json not found.")
        exit()
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format in credentials.json. Error: {e}")
        exit()


# Automate purchase on Amazon
def automate_purchase_amazon(product_url):
    """Automates the purchase process for Amazon."""
    credentials = load_credentials()
    driver = webdriver.Chrome()  # Ensure ChromeDriver is in PATH

    try:
        # Step 1: Navigate to product page
        print(f"🚀 Navigating to product page: {product_url}")
        driver.get(product_url)
        time.sleep(3)

        # Detect page context (product page or checkout page)
        if is_checkout_page(driver):
            print("📦 Already on the checkout page. Proceeding to place order...")
            place_order(driver)
        else:
            print("🛒 On product page. Clicking 'Buy Now' button...")
            click_buy_now(driver)
            time.sleep(3)

            # Handle login if necessary
            if "Sign-In" in driver.title:
                handle_login(driver, credentials)

            # Proceed to place the order
            if is_checkout_page(driver):
                print("📦 Proceeding to place the order...")
                place_order(driver)
            else:
                print("❌ Failed to reach checkout page after 'Buy Now'.")
    except Exception as e:
        print(f"❌ Error during purchase process: {e}")
    finally:
        driver.quit()


# Helper to detect if on checkout page
def is_checkout_page(driver):
    """Determines if the current page is the checkout page."""
    try:
        # Look for the "Buy Now" button specific to the checkout context
        return bool(driver.find_element(By.ID, "buy-now-button"))
    except Exception:
        return False


# Click the "Buy Now" button
def click_buy_now(driver):
    """Clicks the 'Buy Now' button on the product page."""
    try:
        buy_now_button = driver.find_element(By.ID, "buy-now-button")
        buy_now_button.click()
    except Exception as e:
        print(f"❌ Error clicking 'Buy Now' button: {e}")


# Handle login
def handle_login(driver, credentials):
    """Logs into Amazon if the user is prompted."""
    try:
        print("🔒 Logging in...")
        email_input = driver.find_element(By.ID, "ap_email")
        email_input.send_keys(credentials["email"])
        driver.find_element(By.ID, "continue").click()
        time.sleep(2)

        password_input = driver.find_element(By.ID, "ap_password")
        password_input.send_keys(credentials["password"])
        driver.find_element(By.ID, "signInSubmit").click()
        time.sleep(3)
    except Exception as e:
        print(f"❌ Error during login: {e}")


# Place the order on the checkout page
def place_order(driver):
    """Places the order on the checkout page."""
    try:
        print("📦 Placing the order...")
        place_order_button = driver.find_element(By.NAME, "placeYourOrder1")  # Replace if selector differs
        place_order_button.click()
        print("🎉 Order placed successfully!")
    except Exception as e:
        print(f"❌ Error placing the order: {e}")


# Main function for testing
if __name__ == "__main__":
    product_url = input("Enter the product URL: ").strip()
    automate_purchase_amazon(product_url)
