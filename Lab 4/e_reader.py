import time
import board
import busio
import subprocess
import adafruit_mpr121

i2c = busio.I2C(board.SCL, board.SDA)

mpr121 = adafruit_mpr121.MPR121(i2c)

def handle_speak(val):
    subprocess.run(["sh","GoogleTTS_demo.sh",val])


while True:
    for i in range(12):
        touched = mpr121.touched_pins

        if touched[1]:
            print("1 touched")
            #handle_speak("The definition of ambiguous is unclear or vague in meaning")

        if touched[4]:
            print ("4 touched")
            #handle_speak(" this is the current sentence")
        
        if touched[10]:
            print("10 touched")

        if touched[6]:
            print("6 touched")

        if touched[1] and touched[10]:
            handle_speak("judiciousness means good judgement")

        if touched[4] and touched[6]:
            handle_speak("I apologize, he said unapologetically, if I am not being clear. But for your selection of wine tonight there are only two options")

            
    time.sleep(0.25)  # Small delay to keep from spamming output messages.

