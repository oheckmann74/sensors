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
### HARDWARE
#################

class ValueButton(Button):
    def __init__(self, pin, action_value):
        Button.__init__(self, pin)
        self.action_value = action_value


def blink(device, num, duration, off_duration=0):
    for i in range(num):
        device.on()
        sleep(duration)
        device.off()
        if i < num - 1:
            sleep(off_duration if off_duration != 0 else duration)



###################
### CONTROL FLOW
###################


def button_action(button):
    print(button.action_value)
    try:
        post_thingspeak(sample_sensors(), button.action_value)
        post_sentiment_coda(button.action_value)
        blink(red, 1, .3)
    except:
        blink(red, 10, .1, .2)


if __name__ == '__main__':

    PINS = [12, 1, 24, 23, 14]
    red = LED(26)

    buttons = []
    i = 1
    for pin in PINS:
        button = ValueButton(pin, i)
        button.when_released = button_action
        buttons.append(button)
        i += 1

    # startup blink
    blink(red, 3, .1, .4)

    while True:
        temp = sample_sensors()
        post_thingspeak(temp)
        print("temp " + temp)
        sleep(30)
