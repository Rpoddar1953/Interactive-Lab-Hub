from flask import Flask, Response, render_template, request
from flask_socketio import SocketIO, send, emit
from PIL import Image, ImageDraw, ImageFont

import time
import board
import busio
import socket
import signal
import sys
import adafruit_mpu6050
import qwiic_joystick
import qwiic_twist
import adafruit_ssd1306

# For drawing text on the OLED display
font1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)

# For the accelerometer
i2c = busio.I2C(board.SCL, board.SDA)
mpu = adafruit_mpu6050.MPU6050(i2c)

# For the joystick
joystick = qwiic_joystick.QwiicJoystick()
joystick.begin()

# For the rotary encoder
twist = qwiic_twist.QwiicTwist()
twist.begin()
twist.set_count(0)

# For the OLED display
oled_obj = {
    'oled': adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
}

mode = -1

# Mode selection
def mode_selection():
    global mode

    def draw_orig_text():
        oled_obj['oled'].fill(0)
        oled_obj['image'] = Image.new("1", (oled_obj['oled'].width, oled_obj['oled'].height))
        oled_obj['draw'] = ImageDraw.Draw(oled_obj['image'])
        oled_obj['draw'].text((0, 0), "Select a mode:", font=font1, fill=255)
        oled_obj['draw'].text((0, 15), "Joystick", font=font2, fill=255)
        oled_obj['draw'].text((38, 15), "Accelerometer", font=font2, fill=255)
        oled_obj['draw'].text((100, 15), "Arms", font=font2, fill=255)
        oled_obj['oled'].image(oled_obj['image'])
        oled_obj['oled'].show()

    while not twist.is_pressed():
        curr_pos = twist.count % 3
        if curr_pos % 3 == 0:
            draw_orig_text()
            oled_obj['draw'].text((0,20), "________", font=font2, fill=255)
            oled_obj['oled'].image(oled_obj['image'])
            oled_obj['oled'].show()
            mode = 0
        elif curr_pos % 3 == 1:
            draw_orig_text()
            oled_obj['draw'].text((38,20), "______________", font=font2, fill=255)
            oled_obj['oled'].image(oled_obj['image'])
            oled_obj['oled'].show()
            mode = 1
        elif curr_pos % 3 == 2:
            draw_orig_text()
            oled_obj['draw'].text((100,20), "_____", font=font2, fill=255)
            oled_obj['oled'].image(oled_obj['image'])
            oled_obj['oled'].show()
            mode = 2

    return mode

hostname = socket.gethostname()
hardware = 'plughw:2,0'

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('connect')
def test_connect():
    print('connected')
    emit('after connect',  {'data':'Lets dance'})

@app.route('/mode')
def mode():
    if mode == 0:
        return render_template('joystick/mode.html', hostname=hostname)
    elif mode == 1:
        return render_template('accel/mode.html', hostname=hostname)
    else:
        return render_template('arms/mode.html', hostname=hostname)

@app.route('/new_game', methods=['GET', 'POST'])
def new_game():
    if request.method == 'GET':
        return render_template('new_game.html', hostname=hostname)
    if request.method == 'POST':
        mode_selection()
        return 'done'

# Send back joystick interaction
@socketio.on('ping-joystick')
def handle_message(val):
    if joystick.get_horizontal() > 500:
        emit('pong-joystick','make a jump')

# Send back accelerometer interaction
@socketio.on('ping-accel')
def handle_message(val):
    curr_accel = mpu.acceleration
    if curr_accel[0] > 5:
        emit('pong-accel', curr_accel)

def signal_handler(sig, frame):
    print('Closing Gracefully')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000)

