import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789


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
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 5

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
font1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True


buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()


DAYW = "%a, %d %b %Y"
DAYN = "%a, %m/%d/%Y"
TIMEH = "%H:%M:%S"
TIMEI = "%I:%M:%S %p"

DAY = DAYW
TIME = TIMEI

d = 0
t = 0

while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill="#5B009E")

    cmd = "curl -s wttr.in/?format=1"
    WTTR = subprocess.check_output(cmd, shell=True).decode("utf-8")

    if buttonB.value and not buttonA.value: # just button A pressed
        if d % 2 == 0:
            DAY = DAYW
        else:
            DAY = DAYN
        d += 1
    if buttonA.value and not buttonB.value: # just button B pressed
        if t % 2 == 0:
            TIME = TIMEI
        else:
            TIME = TIMEH
        t += 1

    y = top
    draw.text((x, y), time.strftime(DAY), font=font, fill="#FFFFFF")
    y += font.getsize(DAY)[1] + 10
    draw.text((x, y), time.strftime(TIME), font=font, fill="#00AABA")
    y += font.getsize(DAY)[1] + 5
    draw.text((x, y), WTTR, font=font1, fill="#99BA00")
    y += font.getsize(DAY)[1]
    draw.text((x, y), "Have a great day!", font=font, fill="#FF69B4")

    # Display image.
    disp.image(image, rotation)
    time.sleep(0.6)







