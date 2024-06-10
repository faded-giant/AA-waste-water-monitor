import time,sys , yaml,os,re,ssl, smtplib,schedule,datetime,pytz
from unidecode import unidecode
port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "aa.waste.water.monitor@gmail.com"  # Enter your address
password = "jfacvpymfqbenkup"
email_recipients=""
Monitors = {}
directory_path = sys.argv[1]
previous_config = ""
alert_sent = False
with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)

def send_daily_update():
    send_emails("Remote Monitor Daily Report", get_system_status_string())

def get_system_status_string():
    global config, alert_sent, Monitors
    status ="Enabled Montiors:\n"
    for __,monitor in Monitors.items():
        status = status + f"{unidecode(monitor.module.key)}: {monitor.module.low_setpoint} - {monitor.module.high_setpoint}"
        if monitor.module.current_value != "X":
            status = status + f", Currently at {monitor.module.current_value}"
        if monitor.module.tripped:
            status = status + " (out of specification)\n"
        else:
            status = status + "\n"
    resp_val = config["remote_response_threshold"]["duration"]
    if (config["remote_response_threshold"]["enabled"]):
        status = status + f"Remote Response Threshold: {resp_val} minutes"
        if alert_sent:
            
            status = status + " (data is currently stale)"
    else:
        status = status + f"Remote Response Threshold is disabled"
    return status
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

            
def time_since_last_log(log_line):
    try:
        parts = log_line.split(',')
        if len(parts) >= 2:
            timestamp_str = parts[0].strip()
            timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            est = pytz.timezone('America/New_York')
            timestamp = est.localize(timestamp)  # Localize the timestamp to EST
            timestamp = timestamp.astimezone(pytz.UTC)  # Convert it to UTC
            print (timestamp)
            current_time = datetime.datetime.now(pytz.UTC)  # Updated to ensure current time is UTC
            time_difference = current_time - timestamp

            # Return the time difference in minutes
            return int(time_difference.total_seconds() / 60)
        else:
            return -1  # Return -1 for invalid log format
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return -1  # Return -1 for any errorsrrors

def update_config():
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)
    # Extracting values from the YAML file
    global previous_config;
    if config != previous_config and previous_config != "":
        send_emails("Remote Monitor: Configuration Updated", "")
        exit(0)

def get_last_line_from_recent_file(directory):
    global Montiors
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
                keys = lines[0].split(',')
                manifest = {}
                for i,key in enumerate(keys,start=0):
                    for __,monitor in Monitors.items():
                        if key == monitor.module.key:
                            monitor.module.column_id = i
                            manifest[key] = i
                if lines:
                    last_line = lines[-1].strip()
                    data = last_line.split(',')
                    for monitor_key, col_id in manifest.items():
                        if data[col_id].isnumeric():
                            Monitors[monitor_key].module.current_value = float(data[col_id])
                        else:
                            Monitors[monitor_key].module.current_value = '-'
                        print (monitor_key + str(data[int(col_id)]))
                    return last_line
                else:
                    return "The most recent file is empty."
        else:
            return "No matching files found in the directory."
    except Exception as e:
        return f"An error occurred: {str(e)}"

class Timer:
    def __init__(self, key= None, seconds_setpoint=0):
        self.seconds_setpoint = seconds_setpoint
        self.elapsed = 0
        self.last_time = time.time()
        self.current_value = 'X'
        self.key = key
        self.tripped = False
    def reset(self):
        self.elapsed = 0
        self.last_time = time.time()

    def check(self):
        """Update the elapsed time."""
        current_time = time.time()
        self.elapsed += current_time - self.last_time
        self.last_time = current_time
        print (self.elapsed)
        print (self.seconds_setpoint)
        if(self.elapsed >= self.seconds_setpoint and not self.tripped):
            print (f"{self.key}: It has been {round(self.elapsed/60,1)} minutes since this timer was last reset")
            self.tripped = True
        elif(self.elapsed < self.seconds_setpoint and self.tripped):
            self.tripped = False
            
class SpecWatcher:
    def __init__(self,key = "",low_setpoint=sys.maxsize,high_setpoint=0):
        self.low_setpoint = low_setpoint
        self.high_setpoint = high_setpoint
        self.current_value = 'X'
        self.key = key
        self.column_id = -1
        self.tripped = False

    def check(self):
        if self.column_id == -1 or self.current_value == 'X':
            print(self.key + "not found in data")
            print (self.column_id)
            return
            print (unidecode(self.key))
        if (self.current_value == '-' or self.current_value > self.high_setpoint or self.current_value < self.low_setpoint) and not self.tripped:
            send_emails(f"{unidecode(self.key)} is out of specification", f"{self.low_setpoint}-{self.high_setpoint} is acceptable, {unidecode(self.key)} is at {self.current_value}")
            print (f"ALERT: {self.key} is out of specification ({self.low_setpoint}-{self.high_setpoint}) at {self.current_value}")
            self.tripped = True
        elif (self.current_value <= self.high_setpoint and self.current_value >= self.low_setpoint) and self.tripped:
            self.tripped = False
            print (f"Remote Monitor: {self.key} returned to specification ({self.low_setpoint}-{self.high_setpoint}) at {self.current_value}")
            send_emails(f"{unidecode(self.key)} returned to specification", f"{self.low_setpoint}-{self.high_setpoint} is acceptable, {unidecode(self.key)} is at {self.current_value}")


    
    
class Monitor:
    def __init__(self,monitor_constructor):
        self.module = monitor_constructor
    def reset(self):
        self.module.reset()
    def check(self):
        if self.module.current_value == 'X':
            print("Monitor: " + self.module.key + " has no data")
            return
        self.module.check()




previous_config = config
for parameter in config["parameters"]:
    if config["parameters"][parameter]["enabled"]:
        Monitors[parameter] = Monitor(SpecWatcher(key = parameter,low_setpoint=float(config["parameters"][parameter]["min"]),high_setpoint=float(config["parameters"][parameter]["max"])))
#if config["remote_response_threshold"]["enabled"]:
    #Monitors["remote_data_recieved"] = (Monitor(Timer(key = "remote_data_recieved",seconds_setpoint=int(config["remote_response_threshold"]["duration"])*60)))
email_recipients = config['email_recipients']
message_schedule = config['message_schedule']
send_emails("Remote Monitor: Restarted", get_system_status_string())
#Monitors.append(Monitor(SpecWatcher(key = "pH",low_setpoint=4,high_setpoint=9)))
schedule.every().day.at(message_schedule).do(send_daily_update)


def analyze_data():
    global Monitors,alert_sent
    for i in range(3): #sometimes dropbox has lock on file, and may erronuously say data is stale
        last_line = get_last_line_from_recent_file(directory_path)
        time_difference_minutes = time_since_last_log(last_line)
        if time_difference_minutes <= int(config["remote_response_threshold"]["duration"]):
            break
        time.sleep(3)
    print(f"Time since last log entry: {time_difference_minutes} minutes")
    if time_difference_minutes >= int(config["remote_response_threshold"]["duration"]):
        if not alert_sent:
            send_emails(f"ALERT: Stale Data ", f"It has been {time_difference_minutes} minutes since new data was recieved")
            alert_sent = True
    elif alert_sent and time_difference_minutes < int(config["remote_response_threshold"]["duration"]):
        send_emails(f"Remote Monitor: OK. Recieved Fresh Data","")
        alert_sent = False

while True:
    schedule.run_pending()
    analyze_data()
    for _,monitor in Monitors.items():
        monitor.module.check()
    update_config()





