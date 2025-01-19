import json
import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def load_email_template(path="config/email_template.json"):
    """Loads the email template from a JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {path} not found. Using default template.")
        return {
            "subject": "Product Alert: {product_name} is Available!",
            "body": "Hello {username},\n\n"
                    "The product '{product_name}' is now available for ${price}.\n"
                    "Check it out here: {product_url}\n\n"
                    "Best,\nYour Product Sniper Bot"
        }
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse {path}. Using default template. Error: {e}")
        return {
            "subject": "Product Alert: {product_name} is Available!",
            "body": "Hello {username},\n\n"
                    "The product '{product_name}' is now available for ${price}.\n"
                    "Check it out here: {product_url}\n\n"
                    "Best,\nYour Product Sniper Bot"
        }


def format_email(template_data, username, product_name, price, product_url):
    """Formats the email subject and body using the template."""
    subject = template_data["subject"].format(product_name=product_name)
    body = template_data["body"].format(
        username=username,
        product_name=product_name,
        price=price,
        product_url=product_url
    )
    return subject, body


def send_email_notification(recipient_email, subject, body, sender_email, sender_password):
    """Sends an email notification with the provided details."""
    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print("Email notification sent successfully.")
    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}")


def load_credentials(path="config/credentials.json"):
    """Loads credentials from a JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {path} not found.")
        exit()
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse {path}. Error: {e}")
        exit()


def notify_product_in_stock(product_name, price, product_url):
    """Generates and sends a product stock notification email."""
    try:
        credentials = load_credentials()
        username = credentials.get("username")
        sender_email = credentials.get("email")
        sender_password = credentials.get("password")
        recipient_email = credentials.get("recipient_email")

        if not all([username, sender_email, sender_password, recipient_email]):
            print("Error: Missing required fields in credentials.json.")
            exit()

        # Load and format the email template
        template_data = load_email_template()
        subject, body = format_email(
            template_data,
            username=username,
            product_name=product_name,
            price=price,
            product_url=product_url
        )

        # Send email
        send_email_notification(
            recipient_email=recipient_email,
            subject=subject,
            body=body,
            sender_email=sender_email,
            sender_password=sender_password
        )

    except Exception as e:
        print(f"Error in notify_product_in_stock: {e}")


if __name__ == "__main__":
    # Example usage (use environment variables for sensitive data in production)
    product_name = "NVIDIA GeForce RTX 5090"
    price = 1499.99
    product_url = "https://example.com/rtx-5090"

    notify_product_in_stock(
        product_name=product_name,
        price=price,
        product_url=product_url
    )
