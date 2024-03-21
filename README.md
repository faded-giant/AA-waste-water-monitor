# Remote Data Monitor
This script addresses the challenge of identifying out-of-specification conditions in systems that operate without a reliable internet connection. It should be run in a persistent enviornment like Amazon Web Services `EC2`, but self hosting is also okay. 

Syncing data from the remote site to the monitor instance with `Dropbox` is recommended

## Starting The Montior:

Run `python3 monitor2.py <path/to/.csv files>`

## Formatting Rules
Whatever programming is generating data you wish to monitor needs to follow the following rules:
-  A new `.csv` file containing data is generated on a daily basis, formatted `YYYY-MMM-21.csv` Example: `2024-Mar-21.csv`
- In these `.csv` files:	
  1. First row of the file is a header naming each parameter
  2. First column of each entry is a timestamp formatted: `YYYY-MM-DD hh:mm:ss`
  3. Any parameters being monitored should be a number
 

Example Usage:
![image](https://github.com/faded-giant/AA-waste-water-monitor/assets/59129127/775e4fff-cb6f-425c-92fd-ee2542978c61)

## Configuration
The monitor is driven and controlled by updates of the `config.yml` file. When this file is updated, the program will adapt automatically

Example `config.yml` Contents:

```yaml
email_recipients:
  - ethankethank@gmail.com
  - eckenned@umich.edu
  - kgiamm@umich.edu


# Acceptable duration (in minutes) to not receive a response from the remote system
remote_response_threshold:
  duration: 15
  enabled : yes

# Set points for different water quality parameters
parameters:
  pH:
    min: 6
    max: 9
    enabled: yes
  Temp(C):
    min: 20
    max: 32
    enabled: yes
  NO₄ (mg/L):
    min: 0
    max: 67
    enabled: yes
  NO₃ (mg/L):
    min: 0
    max: 100
    enabled: yes
  ODO(mg/L):
    min: 1
    max: 12
    enabled: yes
  ORP (mV):
    min: 200
    max: 400
    enabled: yes

# The specific time of day to receive a running message (in 24-hour format) NOTE: This is in UTC time
message_schedule: "07:00"
```

### Adding Monitor
add the following to the `parameters` section of `config.yml`:
```yaml
<name>:
    min: <minimum allowable value>
    max: <maximum allowable value>
    enabled: <yes or no>
```
`<name>` must be EXACTLY the same as it appears in the .csv header. 

### Stale Data Detection
The monitor can detect if new data isnt coming in:
```yaml
remote_response_threshold:
  duration: <minutes until data is "stale">
  enabled : <yes or no>
```

### Getting Notifications 
The monitor will let you know if something is wrong:
```yaml
email_recipients:
  - <email1@domain.com>
  - <email2@domain.com>
  - <email3@domain.com>
```
To add more users, just add new entry to this section
### Daily Running Message
The monitor will let you know its running every day:
```yaml
message_schedule: "07:00"
```
the string above is formatted `HH:MM` and is in the `utc` timezone.





