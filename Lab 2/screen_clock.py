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
backlight.value = False


buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()


#Date and Time formats
DAYW = "%a, %d %b %Y"
DAYN = "%a, %m/%d/%Y"
TIMEH = "%H:%M:%S"
TIMEI = "%I:%M:%S %p"

DAY = DAYW
TIME = TIMEI

#initalize date and time counter
d = 0
t = 0

#initialize background and background counter
image1 = Image.open("red.jpg")
image1 = image1.convert('RGB')
image1 = image1.resize((width, height), Image.BICUBIC)

#image2 = Image.open("cat.jpg")
#image2 = image2.convert('RGB')
#image2 = image2.resize((width, height), Image.BICUBIC)

imaged = image1

disp.image(image1, rotation)
b = 0

sensor.enable_proximity = True

while True:
    # Draw a black filled box to clear the image.
    #draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    #image = Image.open("red.jpg")
    #image = image.convert('RGB')
    #image = image.resize((width, height), Image.BICUBIC)
    #draw = ImageDraw.Draw(image)
    #image = imaged

    prox = sensor.proximity
    if prox > 2:
        backlight.value = True
        
    else:
        backlight.value = False



    cmd = "curl -s wttr.in/?format=1"
    WTTR = subprocess.check_output(cmd, shell=True).decode("utf-8")

    if buttonB.value and not buttonA.value: # just button A pressed
        if d % 2 == 0 or t % 2 == 0:
            DAY = DAYW
            TIME = TIMEI
        else:
            DAY = DAYN
            TIME = TIMEH
        d += 1
        t += 1
       

    if buttonA.value and not buttonB.value: # just button B pressed
        if b % 2 == 0:
            #image = image1
            image = Image.open("red.jpg")
            image = image.convert('RGB')
            image = image.resize((width, height), Image.BICUBIC)
            #draw = ImageDraw.Draw(image)

        else:
            #image = image2
            image = Image.open("cat.jpg")
            image = image.convert('RGB')
            image = image.resize((width,height), Image.BICUBIC)
            #draw = ImageDraw.Draw(image)

        b += 1

    #if buttonA.value and buttonB.value:
     #   image = Image.open("cat.jpg")
     #   image = image.convert('RGB')
     #   image = image.resize((width, height), Image.BICUBIC)
        #draw = ImageDraw.Draw(image)

    
    draw = ImageDraw.Draw(image)
    y = top
    
    draw.text((x, y), time.strftime(DAY), font=font, fill="#FFFFFF")
    y += font.getsize(DAY)[1] + 10
    draw.text((x, y), time.strftime(TIME), font=font, fill="#FFFFFF")
    y += font.getsize(DAY)[1] + 5
    draw.text((x, y), WTTR, font=font1, fill="#99BA00")
    y += font.getsize(DAY)[1]

    if(time.strftime("%p") == "PM"):
        draw.text((x, y), "Have a good night!", font=font, fill="#FF69B4")
    else:
        draw.text((x, y), "Have a great day!", font=font, fill="#FF69B4")

    # Display image.
    disp.image(image, rotation)
    time.sleep(0.6)







