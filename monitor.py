
import smtplib, ssl, schedule, time

import yaml

with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

# Extracting values from the YAML file
email_recipients = config['email_recipients']
remote_response_threshold = config['remote_response_threshold']

# Extracting set points for parameters
ph_min = config['parameters']['pH']['min']
ph_max = config['parameters']['pH']['max']

temp_min = config['parameters']['Temp']['min']
temp_max = config['parameters']['Temp']['max']

nh4_min = config['parameters']['NH4']['min']
nh4_max = config['parameters']['NH4']['max']

nitrate_min = config['parameters']['Nitrate']['min']
nitrate_max = config['parameters']['Nitrate']['max']

do_min = config['parameters']['Dissolved_Oxygen']['min']
do_max = config['parameters']['Dissolved_Oxygen']['max']

orp_min = config['parameters']['ORP']['min']
orp_max = config['parameters']['ORP']['max']

# Extracting the message schedule
message_schedule = config['message_schedule']

# Printing values to confirm
print("Email Recipients:", email_recipients)
print("Remote Response Threshold (minutes):", remote_response_threshold)
print("pH set points:", ph_min, "-", ph_max)
# ... and so on for the other parameters
print("Scheduled time for running message:", message_schedule)

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "aa.waste.water.monitor@gmail.com"  # Enter your address
receiver_email = "eckenned@umich.edu"  # Enter receiver address
password = "jfacvpymfqbenkup"

def send_emails(subject, body):
    """Send emails to a list of recipients with a given subject and body using SMTP over SSL.

    Args:
    - subject (str): The email subject.
    - body (str): The email body.
    """
    
    # Create email message
    message = f"Subject: {subject}\n\n{body}"

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        for recipient in email_recipients:
            server.sendmail(sender_email, recipient, message)

def still_running():
    send_emails("Remote Monitor: OK", "The monitor is currently running.")

schedule.every().day.at(message_schedule).do(send_emails,"Remote Monitor: OK", f"""
    The monitor is currently running with the following setpoints:
    pH: {ph_min} - {ph_max}
    Temp: {temp_min} - {temp_max} C
    NH4: {nh4_min} - {nh4_max} mg/L
    Nitrate: {nitrate_min} - {nitrate_max} mg/L
    Dissolved Oxygen: {do_min} - {do_max} mg/L
    ORP: {orp_min} - {orp_max} mV
    Remote Response Threshold: {remote_response_threshold} minutes
    """)

while True:
    schedule.run_pending()
    time.sleep(60)  # Wait for one minute