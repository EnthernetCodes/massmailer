import smtplib
import ssl
import csv
import random
import time
from email.message import EmailMessage
from urllib.parse import quote

# Configuration
SMTP_SERVER = "mail.mailer.buzz"
PORT = 465
REPLY_TO = "services@mailer.buzz"
RATE_LIMIT_DELAY = 2  # Delay between emails in seconds
MAX_RETRIES = 3       # Max retries on failure

with open('link','r') as f:
 BASE_URL = f.read() #"https://docsxi.vercel.app/?xi="  # Customize this!

def read_email_content(file_path):
    """Read the email content from a file."""
    with open(file_path, 'r') as file:
        return file.read()

def read_recipients(file_path):
    """Read recipients from a CSV file."""
    recipients = []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            recipients.append(row['email'])
    return recipients

def read_senders(file_path):
    """Read sender email accounts from a CSV file."""
    with open(file_path) as f:
        return [row for row in csv.reader(f)]

def send_email(sender, password, recipient, subject, body, email_name):
    """Send an email."""
    context = ssl.create_default_context()
    retries = 0
    while retries < MAX_RETRIES:
        try:
            # Set up the server connection
            with smtplib.SMTP_SSL(SMTP_SERVER, PORT, context=context) as server:
                server.login(sender, password)
                
                # Create personalized link without encoding
                personalized_link = f"<a href='{BASE_URL}{recipient}'>PDF</a>"
                personalized_body = f"{body}\n\n {personalized_link}"
                
                # Create the email
                em = EmailMessage()
                em['From'] = f'{email_name} <{sender}>'
                em['Reply-To'] = REPLY_TO
                em['To'] = recipient
                em['Subject'] = subject
                em.set_content(personalized_body, subtype='html')

                # Send the email
                server.send_message(em)
                print(f"Email sent from {email_name} <{sender}> to {recipient} with link: {personalized_link}")
                return True
        except Exception as e:
            retries += 1
            print(f"Error sending email from {sender} to {recipient} (Retry {retries}/{MAX_RETRIES}): {e}")
            time.sleep(1)  # Short delay before retrying
    
    return False

def main():
    # User inputs
    subject = input("Enter Subject: ")
    email_name = input("Enter Display Name (Receiver Sees This): ")
    email_content_file = "emails/message1.txt"
    recipients_file = "mails.csv"
    senders_file = "user.csv"
    
    # Read email content, recipients, and senders
    email_body = read_email_content(email_content_file)
    recipients = read_recipients(recipients_file)
    senders = read_senders(senders_file)

    # Email sending loop
    counter = {}
    error_log = []

    for recipient in recipients:
        # Randomly pick a sender
        sender, password = random.choice(senders)

        if sender not in counter:
            counter[sender] = 0

        # Rate limit: Max 500 emails per sender
        if counter[sender] >= 500:
            continue

        # Send email and log result
        if send_email(sender, password, recipient, subject, email_body, email_name):
            counter[sender] += 1
            time.sleep(RATE_LIMIT_DELAY)  # Rate limiting
        else:
            error_log.append(f"Failed to send email to {recipient} using {sender}")

    # Print summary
    print("\nEmail Sending Summary:")
    for sender, count in counter.items():
        print(f"{sender}: {count} emails sent")

    if error_log:
        print("\nError Log:")
        for error in error_log:
            print(error)

    print("\nEmail process completed.")

if __name__ == "__main__":
    main()
