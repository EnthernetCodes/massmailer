import smtplib, ssl, csv, random, time
from email.message import EmailMessage

# Configuration
replyto = 'services@mailer.buzz'
subject = input('Enter Subject Of your Email:\t')
name = input('Email Name to mask:\t')
rate_limit_delay = 2  # Delay between emails in seconds (adjust as needed)
max_retries = 3       # Max retries on failure

counter = {}
error_log = []

# Load sender accounts from .s.csv
with open("user.csv") as f:
    data = [row for row in csv.reader(f)]

# Email content files
file_list = ['emails/message1.txt']  # Single Email

# Read recipient list from mails.csv
with open('mails.csv', 'r') as csvfile:
    datareader = csv.reader(csvfile)
    recipients = [row for row in datareader]

# Send emails
for row in recipients:
    random_user = random.choice(data)
    sender = random_user[0]
    password = random_user[1]

    if sender not in counter:
        counter[sender] = 0

    if counter[sender] >= 500:
        continue

    retries = 0
    while retries < max_retries:
        try:
            # Create secure SSL context
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL('mail.mailer.buzz', 465, context=context)
            server.login(sender, password)

            # Create email
            em = EmailMessage()
            em['From'] = f'{name} <{sender}>'
            em['Reply-To'] = replyto
            em['To'] = row[0]
            em['Subject'] = subject

            # Attach email content
            random_file = random.choice(file_list)
            with open(random_file, 'r') as file:
                html_msg = file.read()
            em.add_alternative(html_msg, subtype='html')

            # Send email
            server.send_message(em)
            counter[sender] += 1
            print(f"{counter[sender]} emails sent from {sender} to {row[0]} using {random_file}")
            server.close()

            # Remove sent email from the queue
            recipients.remove(row)
            with open("mails.csv", "w", newline='') as file:
                writer = csv.writer(file)
                writer.writerows(recipients)

            # Rate limiting
            time.sleep(rate_limit_delay)
            break

        except Exception as e:
            retries += 1
            print(f"Error sending email from {sender} to {row[0]} (Retry {retries}/{max_retries}):", e)
            error_log.append(f"{sender} -> {row[0]}: {e}")
            time.sleep(1)

# Print summary
print("\nEmail Sending Summary:")
for sender, count in counter.items():
    print(f"{sender}: {count} emails sent")

if error_log:
    print("\nError Log:")
    for error in error_log:
        print(error)

print("\nEmail process completed.")
