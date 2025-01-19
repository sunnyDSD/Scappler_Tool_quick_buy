import requests
from bs4 import BeautifulSoup
import json
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load configuration from settings.json
def load_settings():
    try:
        with open("config/settings.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Error: settings.json not found in the config folder.")
        exit()
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in settings.json.")
        exit()

# Function to send an email notification
def send_email_notification(subject, body, recipient_email, sender_email, sender_password):
    try:
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)

        print("Email notification sent.")
    except Exception as e:
        print(f"Error sending email: {e}")

# Function to check if the product page is accessible
def check_page_accessibility(product_url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(product_url, headers=headers)
        if response.status_code == 200:
            print(f"Page is accessible: {product_url}")
            return True
        else:
            print(f"Error: Received status code {response.status_code} from {product_url}")
            return False
    except Exception as e:
        print(f"Error checking page accessibility: {e}")
        return False

# Scraper function to check product availability and price
def check_product_availability(product_url, max_price):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(product_url, headers=headers)
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code} from {product_url}")
            return False, None

        soup = BeautifulSoup(response.content, "html.parser")

        # Example selectors - update these based on the website's structure
        price_element = soup.select_one(".price")  # Update with the actual price selector
        stock_element = soup.select_one(".stock-status")  # Update with the actual stock status selector

        if not price_element or not stock_element:
            print("Error: Unable to find price or stock status elements. Check the selectors.")
            return False, None

        # Extract and process price
        price_text = price_element.get_text(strip=True)
        price = float(price_text.replace("$", "").replace(",", ""))

        # Extract and process stock status
        stock_status = stock_element.get_text(strip=True).lower()

        # Check stock and price conditions
        if "in stock" in stock_status and price <= max_price:
            return True, price
        return False, price

    except Exception as e:
        print(f"Error: {e}")
        return False, None

# Main function
if __name__ == "__main__":
    settings = load_settings()

    product_url = settings.get("product_url")
    max_price = settings.get("max_price")
    refresh_interval = settings.get("refresh_interval", 10)  # Default refresh interval of 10 seconds
    recipient_email = settings.get("recipient_email")
    sender_email = settings.get("sender_email")
    sender_password = settings.get("sender_password")

    if not product_url or not max_price or not recipient_email or not sender_email or not sender_password:
        print("Error: product_url, max_price, recipient_email, sender_email, and sender_password must be set in settings.json.")
        exit()

    if not check_page_accessibility(product_url):
        print("Error: Product page is not accessible. Exiting.")
        exit()

    print(f"Monitoring product: {product_url}")
    print(f"Max price: ${max_price}")

    while True:
        available, price = check_product_availability(product_url, max_price)

        if available:
            subject = "Product Available!"
            body = f"The product is available for ${price}! Buy it now: {product_url}"
            send_email_notification(subject, body, recipient_email, sender_email, sender_password)
            print(body)
            break  # Exit the loop once the product is found
        else:
            print(f"Product not available. Current price: ${price if price else 'N/A'}")

        time.sleep(refresh_interval)
