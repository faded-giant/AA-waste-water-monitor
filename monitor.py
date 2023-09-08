
import smtplib, ssl, schedule, time,os,re,datetime

import yaml

directory_path = "/home/ubuntu/Dropbox (University of Michigan)/monitor-test"
alert_sent = False


email_recipients = ""
remote_response_threshold = ""

# Extracting set points for parameters
ph_min = ""
ph_max = ""

temp_min = ""
temp_max = ""

nh4_min = ""
nh4_max = ""

nitrate_min = ""
nitrate_max = ""

do_min = ""
do_max = ""

orp_min = ""
orp_max = ""

# Extracting the message schedule
message_schedule = ""

previous_config = ""

def time_since_last_log(log_line):
    try:
        parts = log_line.split(',')
        if len(parts) >= 2:
            timestamp_str = parts[0].strip()
            timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            
            current_time = datetime.datetime.now()
            time_difference = current_time - timestamp
            
            # Return the time difference in minutes
            return int(time_difference.total_seconds() / 60)
        else:
            return -1  # Return -1 for invalid log format
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return -1  # Return -1 for any errors



def get_last_line_from_recent_file(directory):
    try:
        # List all files in the directory
        files = os.listdir(directory)

        # Filter the files to include only those matching the expected format (e.g., 2023-Sep-08.csv)
        filtered_files = [file for file in files if re.match(r'\d{4}-[A-Za-z]{3}-\d{2}\.csv', file)]

        # Sort the filtered files by modification time (most recent first)
        sorted_files = sorted(filtered_files, key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)

        # Check if there are any matching files
        if sorted_files:
            # Get the most recent file
            most_recent_file = sorted_files[0]

            # Define the full path to the most recent file
            most_recent_file_path = os.path.join(directory, most_recent_file)

            # Read the last line from the most recent file
            with open(most_recent_file_path, 'r') as file:
                lines = file.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    return last_line
                else:
                    return "The most recent file is empty."
        else:
            return "No matching files found in the directory."
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Example usage:
#directory_path = "/home/ubuntu/Dropbox (University of Michigan)/monitor-test"
directory_path = "/Users/ethan/Dropbox (University of Michigan)/monitor-test"
last_line = get_last_line_from_recent_file(directory_path)
print(last_line)


def get_system_status_string():
    global ph_min, ph_max, temp_min, temp_max, nh4_min, nh4_max, nitrate_min, nitrate_max, do_min, do_max, orp_min, orp_max, remote_response_threshold;
    
    return f"""
    Remote Monitor is currently running with the following setpoints:
    pH: {ph_min} - {ph_max}
    Temp: {temp_min} - {temp_max} C
    NH4: {nh4_min} - {nh4_max} mg/L
    Nitrate: {nitrate_min} - {nitrate_max} mg/L
    Dissolved Oxygen: {do_min} - {do_max} mg/L
    ORP: {orp_min} - {orp_max} mV
    Remote Response Threshold: {remote_response_threshold} minutes
    """

def update_config():
    """Update the configuration file with the current values of the parameters."""
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)
    global email_recipients, remote_response_threshold, ph_min, ph_max, temp_min, temp_max, nh4_min, nh4_max, nitrate_min, nitrate_max, do_min, do_max, orp_min, orp_max, message_schedule;
    # Extracting values from the YAML file
    global previous_config;
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
    print(config)
    # Extracting the message schedule
    message_schedule = config['message_schedule']
    if config != previous_config and previous_config != "":
        send_emails("Remote Monitor: Configuration Updated", get_system_status_string())
    previous_config = config

# Printing values to confirm
update_config()
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

schedule.every().day.at(message_schedule).do(send_emails,"Remote Monitor: OK", get_system_status_string())
send_emails("Remote Monitor: Started", get_system_status_string())
time.sleep(3)
def analyze_data():
    global alert_sent
    last_line = get_last_line_from_recent_file(directory_path)
    print(last_line)
    
    time_difference_minutes = time_since_last_log(last_line)
    print(f"Time since last log entry: {time_difference_minutes} minutes")

    if time_difference_minutes >= int(remote_response_threshold):
        if not alert_sent:
            send_emails(f"ALERT: It has been {time_difference_minutes} minutes since last report", get_system_status_string())
            alert_sent = True
    elif alert_sent and time_difference_minutes < int(remote_response_threshold):
        send_emails(f"Remote Monitor: OK. Recieved fresh data","")
        alert_sent = False


while True:
    schedule.run_pending()
    time.sleep(1)  # Wait for one minute
    update_config()
    analyze_data()
    