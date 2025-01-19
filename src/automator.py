import time
import requests
from bs4 import BeautifulSoup
import json
from src.scraper import check_product_availability, monitor_product
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

                    # Validate product link using scraper logic
                    settings = load_settings()
                    max_price = settings.get("max_price")

                    available, price = check_product_availability(url, max_price)
                    if available:
                        print(f"✅ Product available for ${price}: {url}")

                        # Send notification
                        notify_new_link(url, keywords, settings.get("recipient_email"), settings.get("sender_email"), settings.get("sender_password"))

                        # Trigger scraper to monitor product availability
                        monitor_product(url)
                        return  # Exit after finding a valid product

        except Exception as e:
            print(f"❌ Error during monitoring: {e}")

        time.sleep(interval)

# Function to send notifications for a new link
def notify_new_link(link, keywords, recipient_email, sender_email, sender_password):
    """Sends an email notification when a new product link is found."""
    subject = "New Product Link Found!"
    body = (
        f"A new product link matching your keywords ({', '.join(keywords)}) was found:\n\n"
        f"{link}\n\n"
        "Check it out before it's gone!"
    )
    send_email_notification(
        recipient_email=recipient_email,
        subject=subject,
        body=body,
        sender_email=sender_email,
        sender_password=sender_password
    )

# Main function
if __name__ == "__main__":
    settings = load_settings()

    target_url = settings.get("target_url")
    keywords = settings.get("keywords", [])
    refresh_interval = settings.get("refresh_interval", 10)

    if not target_url or not keywords:
        print("❌ Error: target_url and keywords must be set in settings.json.")
        exit()

    monitor_page(target_url, keywords, refresh_interval)
