import time
import requests
from bs4 import BeautifulSoup
from src.scraper import check_product_availability

# Load configuration
def load_settings():
    try:
        with open("config/settings.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Error: settings.json not found.")
        exit()
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in settings.json.")
        exit()

# Monitor a target page for new product links
def monitor_page(target_url, keywords, interval=10):
    print(f"Monitoring page: {target_url}")
    seen_links = set()

    while True:
        try:
            response = requests.get(target_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            })
            if response.status_code != 200:
                print(f"Error: Status code {response.status_code} while monitoring {target_url}")
                time.sleep(interval)
                continue

            soup = BeautifulSoup(response.content, "html.parser")

            # Find all links on the page
            links = soup.find_all("a", href=True)
            for link in links:
                url = link["href"]
                text = link.get_text(strip=True).lower()

                # Check if the link contains a keyword and is new
                if any(keyword in text for keyword in keywords) and url not in seen_links:
                    seen_links.add(url)
                    print(f"New product link found: {url}")

                    # Validate product link using scraper logic
                    settings = load_settings()
                    max_price = settings.get("max_price")

                    available, price = check_product_availability(url, max_price)
                    if available:
                        print(f"Product available for ${price}: {url}")
                        # Trigger purchase logic here
                        # purchase_product(url, credentials=settings.get('credentials'))
                        return

        except Exception as e:
            print(f"Error during monitoring: {e}")

        time.sleep(interval)

# Main function
if __name__ == "__main__":
    settings = load_settings()

    target_url = settings.get("target_url")
    keywords = settings.get("keywords", [])
    refresh_interval = settings.get("refresh_interval", 10)

    if not target_url or not keywords:
        print("Error: target_url and keywords must be set in settings.json.")
        exit()

    monitor_page(target_url, keywords, refresh_interval)
