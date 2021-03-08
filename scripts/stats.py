import time
import board
import busio
import adafruit_scd30
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import subprocess

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# Create the interface to the SCD30 sensor (CO2, Temperature, Humidity)
scd = adafruit_scd30.SCD30(i2c)
 
# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
 
# Clear display.
disp.fill(0)
disp.show()
 
# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))
 
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
 
# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)
 
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0
 
# Load default font.
font = ImageFont.load_default()
 
# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)
 
while True:
 
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    
    # get the IP address
    cmd = "hostname -I | cut -d' ' -f1"
    IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
  
    # Write the text.
 
    draw.text((x, top + 0), "IP: " + IP, font=font, fill=255)
    draw.text((x, top + 8), "CO2: {:.0f} PPM".format(scd.CO2), font=font, fill=255)
    draw.text((x, top + 16), "Temp: {:.1f} C/ {:.1f} F".format(scd.temperature, scd.temperature*1.8+32), font=font, fill=255)
    draw.text((x, top + 25), "Humidity: {:.1f} %%rH".format(scd.relative_humidity), font=font, fill=255)
 
    # Display image.
    disp.image(image)
    disp.show()
    time.sleep(1)
