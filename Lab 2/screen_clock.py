import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
import board
import busio
import adafruit_apds9960.apds9960
import time
import qwiic_button
import sys

#gesture sensor
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_apds9960.apds9960.APDS9960(i2c)

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))

# Display the image
disp.image(image, rotation)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
font1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
font3 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 23)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

# Initialize the buttons on the screen
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()

# Initialize the red LED button
buttonR = qwiic_button.QwiicButton()
buttonR.begin()

# Define the different formats
DAYW = "%a, %d %b %Y"
DAYN = "%a, %m/%d/%Y"
TIMEH = "%H:%M:%S"
TIMEI = "%I:%M:%S %p"

# Set the default day and time format
DAY = DAYW
TIME = TIMEI

# Counters to switch the formats and backgrounds
dt = 0
b = 0

# For the proximity sensor
sensor.enable_proximity = True

# For the red LED button
buttonR.LED_off()

# Set the default image to display
image = Image.open("images/background1.jpg")

while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    background = Image.new("RGB", (width, height))

    cmd = "curl -s wttr.in/?format=1"
    WTTR = subprocess.check_output(cmd, shell=True).decode("utf-8")

    prox = sensor.proximity
    if prox > 2:
        backlight.value = True
    else:
        backlight.value = False

    if buttonB.value and not buttonA.value: # just button A pressed
        if dt % 2 == 0:
            DAY = DAYW
            TIME = TIMEI
        else:
            DAY = DAYN
            TIME = TIMEH
        dt += 1
    if buttonA.value and not buttonB.value: # just button B pressed
        if b % 3 == 0:
            image = Image.open("images/background1.jpg")
        elif b % 3 == 1:
            image = Image.open("images/background2.jpg")
        else:
            image = Image.open("images/background3.jpg")
        b += 1 

    if buttonR.is_button_pressed() == True:
        buttonR.LED_on(100)
        numS = 0
        numM = 0
        temp = Image.new("RGB", (width, height))
        temp_draw = ImageDraw.Draw(temp)
        while buttonR.is_button_pressed() == False:
            temp_draw.rectangle((0, 0, width, height), outline=0, fill=0)
            if numS != 0 and numS % 60 == 0:
                numM += 1
            ptime = "{0:0=2d}".format(numM) + ":" + "{0:0=2d}".format(numS % 60)
            temp_draw.text((50, 40), ptime, font=font2, fill="#FFFFFF")
            disp.image(temp, rotation)
            numS += 1
            time.sleep(0.9)
        buttonR.LED_off()
        time.sleep(1)
        draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))

    image = image.convert('RGB')
    image = image.resize((width, height), Image.BICUBIC)

    background.paste(image, mask = image.split()[0])

    img_draw = ImageDraw.Draw(background)

    y = top
    img_draw.text((5, y), time.strftime(DAY), font=font, fill="#FFFFFF")
    y += font.getsize(DAY)[1] + 10
    img_draw.text((5, y), time.strftime(TIME), font=font, fill="#FFFFFF")
    y += font.getsize(DAY)[1] + 5
    img_draw.text((5, y), WTTR, font=font1, fill="#FFFFFF")
    y += font.getsize(DAY)[1]

    if int(time.strftime("%H")) < 6 or int(time.strftime("%H")) >= 18:
        img_draw.text((5, y), "Have a good night!", font=font3, fill="#FFFFFF")
    else:
        img_draw.text((5, y), "Have a great day!", font=font3, fill="#FFFFFF")

    disp.image(background, rotation)
    time.sleep(0.1)






