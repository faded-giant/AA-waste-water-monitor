import time,sys

CURRENT_VALUES = {}

class Timer:
    def __init__(self, key= None, seconds_setpoint=0):
        self.seconds_setpoint = seconds_setpoint
        self.elapsed = 0
        self.last_time = time.time()
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
        if(self.elapsed >= self.seconds_setpoint and not self.tripped):
            print (f"{self.key}: It has been {round(self.elapsed/60,1)} minutes since this timer has been set")
            self.tripped = True
        elif(self.elapsed < self.seconds_setpoint and self.tripped):
            self.tripped = False
            
class SpecWatcher:
    def __init__(self,key = "",low_setpoint=sys.maxsize,high_setpoint=0):
        self.low_setpoint = low_setpoint
        self.high_setpoint = high_setpoint
        self.key = key
        self.tripped = False

    def check(self):
        if (CURRENT_VALUES[self.key] >= self.high_setpoint or CURRENT_VALUES[self.key] <= self.low_setpoint) and not self.tripped:
            print (f"{self.key} is out of specification ({self.low_setpoint}-{self.high_setpoint}) at {CURRENT_VALUES[self.key]}")
            self.tripped = True
        elif (CURRENT_VALUES[self.key] < self.high_setpoint and CURRENT_VALUES[self.key] > self.low_setpoint) and self.tripped:
            self.tripped = False


    
    
class Monitor:
    def __init__(self,monitor_constructor):
        self.module = monitor_constructor
    def reset(self):
        self.module.reset()
    def check(self):
        self.module.check()


Monitors = []
Monitors.append(Monitor(Timer(key = "since_last",seconds_setpoint=5)))
Monitors.append(Monitor(SpecWatcher(key = "pH",low_setpoint=4,high_setpoint=9)))

while True:
    CURRENT_VALUES["pH"] = 3
    for monitor in Monitors:
        monitor.check()


