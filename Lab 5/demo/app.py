import eventlet
eventlet.monkey_patch()

from flask import Flask, Response,render_template
from flask_socketio import SocketIO, send, emit
from subprocess import Popen, call

import time
import board
import busio
import adafruit_mpu6050
import json
import socket

import signal
import sys
from queue import Queue

 
i2c = busio.I2C(board.SCL, board.SDA)
mpu = adafruit_mpu6050.MPU6050(i2c)

hostname = socket.gethostname()
hardware = 'plughw:2,0'

app = Flask(__name__)
socketio = SocketIO(app)
audio_stream = Popen("/usr/bin/cvlc alsa://"+hardware+" --sout='#transcode{vcodec=none,acodec=mp3,ab=256,channels=2,samplerate=44100,scodec=none}:http{mux=mp3,dst=:8080/}' --no-sout-all --sout-keep", shell=True)

num = 10
i = 0
currSumX = 0
currSumY = 0
currSumZ = 0

pre = (-float('inf'), -float('inf'), -float('inf'))
cur = (-float('inf'), -float('inf'), -float('inf'))
thresh = 2.0
peakCtr = 0

@socketio.on('speak')
def handel_speak(val):
    call(f"espeak '{val}'", shell=True)

@socketio.on('connect')
def test_connect():
    print('connected')
    emit('after connect',  {'data':'Lets dance'})

@socketio.on('ping-gps')
def handle_message(val):
    # print(mpu.acceleration)
    emit('pong-gps', mpu.acceleration)

    currAccel = mpu.acceleration

    # THRESHOLD DETECTION
    if currAccel[0] > 10.0:
        print("-----------------X-direction-----------------")
        print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2" % (currAccel))
    if currAccel[1] > 5.0:
        print("-----------------Y-direction-----------------")
        print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2" % (currAccel))
    if currAccel[2] > 11.0:
        print("-----------------Z-direction-----------------")
        print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2" % (currAccel))

    # AVERAGE
    global i
    global num
    global currSumX
    global currSumY
    global currSumZ

    if i < num:
        i += 1
        currSumX += currAccel[0]
        currSumY += currAccel[1]
        currSumZ += currAccel[2]
    else:
        averageSum = (currSumX/num, currSumY/num, currSumZ/num)
        print("Average: X:%.2f, Y: %.2f, Z: %.2f m/s^2" % (averageSum))
        i = 0
        currSumX = 0
        currSumY = 0
        currSumZ = 0

    # PEAK DETECTION
    global pre
    global cur
    global peakCtr
    
    pre = cur
    cur = currAccel
    if cur[0] - pre[0] > thresh:
        print("PEAK! ", peakCtr)
        peakCtr += 1

@app.route('/')
def index():
    return render_template('index.html', hostname=hostname)

def signal_handler(sig, frame):
    print('Closing Gracefully')
    audio_stream.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000)


