import requests
from bs4 import BeautifulSoup
import json
import time
from src.purchase import automate_purchase  # Purchase module

# Load configuration
def load_settings(path="config/settings.json"):
    """Loads configuration settings."""
    try:
        with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("❌ Error: settings.json not found.")
        exit()
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format in settings.json. Error: {e}")
        exit()


# Scrape product page for details
def scrape_product_details(product_url, max_price):
    """Scrapes the product page for price and stock status."""
    print(f"🔍 Scraping product page: {product_url}")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(product_url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Error: Received status code {response.status_code} from {product_url}")
            return None, None

        soup = BeautifulSoup(response.content, "html.parser")

        # Example selectors - update these based on the website's structure
        price_element = soup.select_one(".price")  # Replace with the actual price selector
        stock_element = soup.select_one(".stock-status")  # Replace with the actual stock status selector
        title_element = soup.select_one(".product-title")  # Replace with the actual product title selector

        if not price_element or not stock_element:
            print("❌ Error: Unable to find price or stock status elements. Check the selectors.")
            return None, None

        # Extract product details
        price_text = price_element.get_text(strip=True)
        price = float(price_text.replace("$", "").replace(",", ""))
        stock_status = stock_element.get_text(strip=True).lower()
        title = title_element.get_text(strip=True) if title_element else "Unknown Product"

        # Print extracted details
        print(f"📄 Product Details:\n - Title: {title}\n - Price: ${price}\n - Stock Status: {stock_status}")

        # Check if the product meets criteria
        if "in stock" in stock_status and price <= max_price:
            return price, title
        return None, title

    except Exception as e:
        print(f"❌ Error scraping product page: {e}")
        return None, None


# Monitor product
def monitor_product(product_url):
    """Monitors the product page and proceeds to purchase if criteria are met."""
    settings = load_settings()
    max_price = settings.get("max_price")
    refresh_interval = settings.get("refresh_interval", 10)

    while True:
        price, title = scrape_product_details(product_url, max_price)
        if price:
            print(f"🎉 Product is available for ${price}! Initiating purchase process for {title}...")
            automate_purchase(product_url)  # Trigger purchase logic
            break
        else:
            print(f"🔄 Product not available or criteria not met. Retrying in {refresh_interval} seconds...")
        time.sleep(refresh_interval)
