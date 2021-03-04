import os
from signal import pause
from time import sleep, time

import requests
from gpiozero import Button
from gpiozero import LED

import thingspeak
import codaconfig  # contains TABLE_ID, DOC_ID, API_TOKEN, SENTIMENT_COLUMN_ID
import config  # contains CHANNEL and API_KEY

import board
import busio
import adafruit_scd30

from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import subprocess


###########
### CODA API (to be removed)
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
### SENSOR
##################

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# Create the interface to the SCD30 sensor (CO2, Temperature, Humidity)
scd = adafruit_scd30.SCD30(i2c)

def sample_sensors():
    ret = {}
    ret["temperature_c"] = scd.temperature
    ret["temperature_f"] = scd.temperature * 1.8 + 32
    ret["co2"] = scd.CO2
    ret["humidity"] = scd.relative_humidity
    return ret


##################
### THINGSPEAK
##################

ch = thingspeak.Channel(config.CHANNEL, api_key=config.API_KEY)


def post_thingspeak(sensor_reading, sentiment=None):
    if sentiment:
        print("Sentiment is %s" % sentiment)
    else:
        print("posting %s ppm" % sensor_reading["co2"])

    data = {2: sensor_reading["temperature_c"], 3: sensor_reading["temperature_f"], 4: sensor_reading["humidity"] }
    if sensor_reading["co2"] > 0:
        data[1] = sensor_reading["co2"]
    if sentiment:
        data[5] = sentiment
    ch.update(data)


#################
### BETTER BUTTONS
#################

class FlexButton(Button):
    def __init__(self, pin, buttonvalue, on_short_press, on_long_press=None):
        Button.__init__(self, pin)
        self.buttonvalue = buttonvalue
        self.on_short_press = on_short_press
        self.on_long_press = on_long_press
        self.when_pressed = self.handle_press

    def handle_press(self):
        start_time = time()
        diff = 0

        while self.is_active and (diff < 2):
            diff = time() - start_time

        if diff < 2 or self.on_long_press is None:
            self.on_short_press(self)
        else:
            self.on_long_press(self)


####################
### LED SETUP
####################

class LEDs():
    def __init__(self, red_pin, green_pin=None):
        self.red = LED(red_pin)
        self.green = None
        if green_pin:
            self.green = LED(green_pin)

    def signal_error(self, error_code):
        self.red.blink(1, .33, error_code)

    def signal_ok(self):
        if self.green:
            self.green.blink(.33, n=2)
        else:
            self.red.blink(.2, .2, n=2)

    def signal_ready(self):
        if self.green:
            self.green.blink(.2, .2, n=3, background=True)
        self.red.blink(.2, .2, n=3, background=True)


###################
### CONTROL FLOW
###################


def sentiment_action(button):
    try:
        post_thingspeak(sample_sensors(), button.buttonvalue)
        post_sentiment_coda(button.buttonvalue)
        leds.signal_ok()
    except:
        leds.signal_error(5)


from subprocess import call


def shutdown_action(button):
    leds.signal_ready()
    call("sudo nohup shutdown -h now", shell=True)


if __name__ == '__main__':

    PINS = [26, 25, 24, 23, 22]  # typically three or 5 buttons
    leds = LEDs(6, 5)  # either one LED or two (red and green)

    buttons = []
    i = 1
    for pin in PINS:
        button = FlexButton(pin, i, sentiment_action, shutdown_action)
        buttons.append(button)
        i += 1

    # startup blink
    leds.signal_ready()

    while True:
        temp = sample_sensors()
        post_thingspeak(temp)
        sleep(30)
