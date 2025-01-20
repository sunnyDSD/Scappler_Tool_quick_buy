import time
import requests
from bs4 import BeautifulSoup
import json
from src.scraper import monitor_product
from src.notifications import send_email_notification


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


# Save the validated product link to settings.json
def save_product_url(product_url, path="config/settings.json"):
    """Saves the product URL to settings.json."""
    try:
        settings = load_settings(path)
        settings["product_url"] = product_url
        with open(path, "w") as file:
            json.dump(settings, file, indent=4)
        print(f"✅ Product URL saved: {product_url}")
    except Exception as e:
        print(f"❌ Error saving product URL: {e}")


# Monitor a target page for new product links
def monitor_page(target_url, keywords, interval=10):
    """Monitors a page for product links matching keywords."""
    print(f"🔍 Monitoring page: {target_url}")
    seen_links = set()

    while True:
        try:
            response = requests.get(target_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            })
            if response.status_code != 200:
                print(f"❌ Error: Status code {response.status_code} while monitoring {target_url}")
                time.sleep(interval)
                continue

            soup = BeautifulSoup(response.content, "html.parser")

            # Find all links on the page
            links = soup.find_all("a", href=True)
            for link in links:
                url = link["href"]
                text = link.get_text(strip=True).lower()

                # Check if the link contains a keyword and is new
                if any(keyword.lower() in text for keyword in keywords) and url not in seen_links:
                    seen_links.add(url)
                    print(f"🎯 New product link found: {url}")

                    # Send an email to the user for confirmation
                    notify_user_for_confirmation(url, keywords)
                    
                    # Ask for user confirmation
                    user_input = input(f"Is this the correct link? (yes/no): ").strip().lower()
                    if user_input == "yes":
                        save_product_url(url)
                        return url  # Exit monitoring and return the confirmed link
                    else:
                        print("🔄 Continuing to monitor for new links...")

        except Exception as e:
            print(f"❌ Error during monitoring: {e}")

        time.sleep(interval)


# Notify the user about a new product link
def notify_user_for_confirmation(link, keywords):
    """Sends an email notification when a new product link is found."""
    subject = "New Product Link Found!"
    body = (
        f"A new product link matching your keywords ({', '.join(keywords)}) was found:\n\n"
        f"{link}\n\n"
        "Please confirm if this is the correct link to proceed."
    )
    settings = load_settings()
    send_email_notification(
        recipient_email=settings.get("recipient_email"),
        subject=subject,
        body=body,
        sender_email=settings.get("sender_email"),
        sender_password=settings.get("sender_password")
    )


# Main function
if __name__ == "__main__":
    settings = load_settings()

    product_url = settings.get("product_url")
    target_url = settings.get("target_url")
    keywords = settings.get("keywords", [])
    refresh_interval = settings.get("refresh_interval", 10)

    if not target_url or not keywords:
        print("❌ Error: target_url and keywords must be set in settings.json.")
        exit()

    # If product_url is already provided, skip automator and go directly to scraper
    if product_url:
        print(f"📌 Product URL already provided: {product_url}")
        monitor_product(product_url)
    else:
        print("🔄 No product URL provided. Starting automator...")
        validated_url = monitor_page(target_url, keywords, refresh_interval)
        if validated_url:
            print(f"✅ Validated product link: {validated_url}")
            monitor_product(validated_url)
