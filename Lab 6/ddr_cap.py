import time
import board
import busio
import subprocess
import adafruit_mpr121

import paho.mqtt.client as mqtt
import uuid

topic1 = 'IDD/move_setter'
topic2 = 'IDD/dance_moves'



def handle_speak(val):
    subprocess.run(["sh","GoogleTTS_demo.sh",val])


#this is the callback that gets called once we connect to the broker. 
#we should add our subscribe functions here as well
def on_connect(client, userdata, flags, rc):
    print(f"connected with result code {rc}")
    client.subscribe(topic1)
    # you can subsribe to as many topics as you'd like
    # client.subscribe('some/other/topic')


# this is the callback that gets called each time a message is recived
def on_message(client, userdata, msg):
    print(f"topic: {msg.topic} msg: {msg.payload.decode('UTF-8')}")
    # you can filter by topics
    # if msg.topic == 'IDD/some/other/topic': do thing
    isTouched = 0;
    handle_speak(msg.payload.decode('UTF-8'))
    print(msg.payload.decode('UTF-8'))

    if "Game over" not in msg.payload.decode('UTF-8'):
        
        while isTouched == 0: 
    
            for i in range(12):
                touched = mpr121.touched_pins

                if touched[1]:
                    val = "D"
                    print("1 touched")
                    client.publish(topic2, val)
                    isTouched = 1;
                    break;

                if touched[4]:
                    val = "U"
                    print ("4 touched")
                    client.publish(topic2, val)
                    isTouched = 1;
                    break;

                if touched[10]:
                    val = "L"
                    print("10 touched")
                    client.publish(topic2, val)
                    isTouched = 1;
                    break;

                if touched[6]:
                    val = "R"
                    print("6 touched")
                    client.publish(topic2, val) 
                    isTouched = 1;
                    break;
            
            time.sleep(0.25)  # Small delay to keep from spamming output messages.

client = mqtt.Client(str(uuid.uuid1()))
client.tls_set()
client.username_pw_set('idd', 'device@theFarm')

# attach out callbacks to the client
client.on_connect = on_connect
client.on_message = on_message

client.connect(
    'farlab.infosci.cornell.edu',
    port=8883)


i2c = busio.I2C(board.SCL, board.SDA)

mpr121 = adafruit_mpr121.MPR121(i2c)


client.loop_forever()

