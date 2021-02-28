import os
from signal import pause
from time import sleep

import requests
from gpiozero import Button
from gpiozero import LED

import thingspeak
import codaconfig # contains TABLE_ID, DOC_ID, API_TOKEN, SENTIMENT_COLUMN_ID
import config # contains CHANNEL and API_KEY

###########
### CODA 
###########


def post_sentiment_coda(sentiment: int):
    headers = {'Authorization': 'Bearer %s' % codaconfig.API_TOKEN}
    uri = 'https://coda.io/apis/v1/docs/%s/tables/%s/rows' % (codaconfig.DOC_ID, codaconfig.TABLE_ID)
    payload = {
        'rows': [
            {
                'cells': [
                    {'column': codaconfig.SENTIMENT_COLUMN_ID, 'value': sentiment},
                ],
            },
        ],
    }
    req = requests.post(uri, headers=headers, json=payload)
    req.raise_for_status()  # Throw if there was an error.
    res = req.json()
    return res


##################
### THINGSPEAK
##################

ch = thingspeak.Channel(config.CHANNEL, api_key=config.API_KEY)


def post_thingspeak(temperature, sentiment=-1):
    print("posting %s and %s" % (temperature, sentiment))
    ch.update({1: temperature, 2: sentiment}) if sentiment >= 0 else ch.update({1: temperature})


def sample_sensors():
    temp = os.popen("vcgencmd measure_temp").readline()
    return (temp.replace("temp=", ""))


#################
### BETTER BUTTONS
#################

class FlexButton(Button):
    def __init__(self, pin, onShortPress, onLongPress = None):
        Button.__init__(self, pin)
        self.nShortPress = onShortPress
        self.onLongPress = onLongPress
    
    def when_released(self):
        if self.onLongPress != None && held_time > 3:
            onLongPress
        else:
            onShortPress



####################
### LED SETUP
####################

class LEDs():
    def __init__(self, red_pin, green_pin = None):
        self.red = LED(red_pin)
        self.green = None
        if green_pin:
            self.green = LED(green_pin) 

    def signal_error(self, error_code): 
        self.red.blink(1,.33,error_code)

    def signal_ok(self):
        if self.green:
            self.green.blink(.33,n=2)
        else: 
            self.red.blink(.2,.2, n=2)

    def signal_ready(self): 
        if self.green:
            self.green.blink(.1, .2, n=3, background=True)
        self.red.blink(.1, .2, n=3, background=True)

###################
### CONTROL FLOW
###################


def sentiment_action(value):
    print(value)
    try:
        post_thingspeak(sample_sensors(), value)
        post_sentiment_coda(alue)
        leds.signal_ok()
    except:
        leds.signal_error(5)
        
        
from subprocess import call

def shutdown_action():
    call("sudo nohup shutdown -h now", shell=True)

if __name__ == '__main__':

    PINS = [12, 1, 24, 23, 14] # typically three or 5 buttons
    leds = LEDs(26) # either one LED or two (red and green)

    i = 1
    for pin in PINS:
        button = FlexButton(pin, lambda: sentiment_action(i), shutdown_action)
        i += 1

    # startup blink
    leds.signal_ready()

    while True:
        temp = sample_sensors()
        post_thingspeak(temp)
        print("temp " + temp)
        sleep(30)
