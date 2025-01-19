import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from twilio.rest import Client

# Twilio setup (for notifications)
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = 'your_twilio_number'
TO_PHONE_NUMBER = 'your_phone_number'

# Initialize Twilio Client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Configure Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run browser in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
service = Service('/path/to/chromedriver')  # Update with your chromedriver path
driver = webdriver.Chrome(service=service, options=chrome_options)

def check_product(url, max_price):
    try:
        driver.get(url)
        time.sleep(3)  # Allow JavaScript to load

        # Example XPath - update based on the site
        price_element = driver.find_element(By.XPATH, '//*[@id="price"]')
        stock_element = driver.find_element(By.XPATH, '//*[@id="stock-status"]')

        price = float(price_element.text.replace('$', '').replace(',', ''))
        stock_status = stock_element.text.lower()

        if 'in stock' in stock_status and price <= max_price:
            return True, price
        return False, price
    except Exception as e:
        print(f"Error: {e}")
        return False, None

def send_notification(message):
    client.messages.create(
        body=message,
        from_=TWILIO_PHONE_NUMBER,
        to=TO_PHONE_NUMBER
    )

def main():
    product_url = input("Enter the product URL: ")
    max_price = float(input("Enter the maximum price you're willing to pay: "))
    refresh_interval = int(input("Enter the refresh interval (in seconds): "))

    while True:
        available, price = check_product(product_url, max_price)
        if available:
            message = f"The product is available for ${price}! Buy it now: {product_url}"
            print(message)
            send_notification(message)
            break  # Stop the bot once the product is found
        else:
            print(f"Not available yet. Current price: ${price}")
        time.sleep(refresh_interval)

if __name__ == "__main__":
    main()
