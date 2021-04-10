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

from scipy.signal import find_peaks
 
i2c = busio.I2C(board.SCL, board.SDA)
mpu = adafruit_mpu6050.MPU6050(i2c)

hostname = socket.gethostname()
hardware = 'plughw:2,0'

app = Flask(__name__)
socketio = SocketIO(app)
audio_stream = Popen("/usr/bin/cvlc alsa://"+hardware+" --sout='#transcode{vcodec=none,acodec=mp3,ab=256,channels=2,samplerate=44100,scodec=none}:http{mux=mp3,dst=:8080/}' --no-sout-all --sout-keep", shell=True)


@socketio.on('speak')
def handel_speak(val):
    call(f"espeak '{val}'", shell=True)

@socketio.on('connect')
def test_connect():
    print('connected')
    emit('after connect',  {'data':'Lets dance'})


totalx = []
totaly = []
totalz = []
n = 0
@socketio.on('ping-gps')
def handle_message(val):
    # print(mpu.acceleration)
    emit('pong-gps', mpu.acceleration) 
    #if mpu.acceleration[0] > 2:
        #print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2" % (mpu.acceleration))

    #print(find_peaks(mpu.acceleration[0], 5))
    global totalx = []
    global totaly = []
    global totalz = []


    n = n+1
    totalx.append(mpu.acceleration[0])
    totaly.append(mpy.acceleration[1])
    totalz.append(mpu.acceleration[2])

    if n > 50:
        Xpeaks, _ = find_peaks(totalx)
        print("peaks for x", totalx[Xpeaks])





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


