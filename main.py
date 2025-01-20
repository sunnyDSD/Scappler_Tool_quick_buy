from src.automator import monitor_page
from src.scrapper import check_product_availability

def main():
    print("Starting the Product Sniper Bot...")
    
    # Automator: Monitor for the product link
    product_link = monitor_page()
    if not product_link:
        print("No product link found. Exiting.")
        return
    
    print(f"Product link found: {product_link}")
    
    # Scraper: Monitor availability and price
    check_product_availability(product_link)

if __name__ == "__main__":
    main()