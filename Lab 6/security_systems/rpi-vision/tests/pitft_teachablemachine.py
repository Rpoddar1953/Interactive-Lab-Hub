import time
import argparse
import pygame
import os
import sys
import numpy as np
import subprocess

from rpi_vision.agent.capture import PiCameraStream
from rpi_vision.models.teachablemachine import TeachableMachine

import paho.mqtt.client as mqtt
import uuid

CONFIDENCE_THRESHOLD = 0.6   # at what confidence level do we say we detected a thing
PERSISTANCE_THRESHOLD = 0.5  # what percentage of the time we have to have seen a thing

os.environ['SDL_FBDEV'] = "/dev/fb1"
os.environ['SDL_VIDEODRIVER'] = "fbcon"

pygame.init()
screen = pygame.display.set_mode((500,500), pygame.RESIZABLE)

capture_manager = PiCameraStream(resolution=(screen.get_width(), screen.get_height()), rotation=180, preview=False)

client = mqtt.Client(str(uuid.uuid1()))
client.tls_set()
client.username_pw_set('idd', 'device@theFarm')
client.connect(
    'farlab.infosci.cornell.edu',
    port=8883)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--include-top', type=bool,
                        dest='include_top', default=True,
                        help='Include fully-connected layer at the top of the network.')

    parser.add_argument('savedmodel', help='TeachableMachine savedmodel')

    parser.add_argument('--tflite',
                        dest='tflite', action='store_true', default=False,
                        help='Convert base model to TFLite FlatBuffer, then load model into TFLite Python Interpreter')
    args = parser.parse_args()
    return args

def main(args):
    last_seen = [None] * 10
    last_spoken = None

    pygame.mouse.set_visible(False)
    screen.fill((0,0,0))
    try:
        splash = pygame.image.load(os.path.dirname(sys.argv[0])+'/bchatsplash.bmp')
        screen.blit(splash, ((screen.get_width() / 2) - (splash.get_width() / 2),
                    (screen.get_height() / 2) - (splash.get_height() / 2)))
    except pygame.error:
        pass
    pygame.display.update()

    smallfont = pygame.font.Font(None, 24)

    model = TeachableMachine(args.savedmodel)
    capture_manager.start()
    
    topic = "security_cam"

    while not capture_manager.stopped:
        if capture_manager.frame is None:
            continue
        frame = capture_manager.read()
        previewframe = np.ascontiguousarray(np.flip(np.array(capture_manager.frame), 2))
        img = pygame.image.frombuffer(previewframe, capture_manager.camera.resolution, 'RGB')
        screen.blit(img, (0, 0))

        timestamp = time.monotonic()
        if args.tflite:
            prediction = model.tflite_predict(frame)[0]
        else:
            prediction = model.predict(frame)[0]
        delta = time.monotonic() - timestamp

        for p in prediction:
            label, name, conf = p
            if label == 0 and conf > CONFIDENCE_THRESHOLD:
                print("Detected", name)

                persistant_obj = False  # assume the object is not persistant
                last_seen.append(name)
                last_seen.pop(0)

                inferred_times = last_seen.count(name)
                if inferred_times / len(last_seen) > PERSISTANCE_THRESHOLD:  # over quarter time
                    persistant_obj = True

                detecttext = name.replace("_", " ")
                detecttextfont = smallfont
                detecttext_color = (0, 255, 0) if persistant_obj else (255, 255, 255)
                detecttext_surface = detecttextfont.render(detecttext, True, detecttext_color)
                detecttext_position = (screen.get_width()//2,
                                       screen.get_height() - detecttextfont.size(detecttext)[1])
                screen.blit(detecttext_surface, detecttext_surface.get_rect(center=detecttext_position))
		
                client.publish(topic, "Shivani")

                break

            elif label == 1 and conf > CONFIDENCE_THRESHOLD:
                print("Detected", name)

                persistant_obj = False  # assume the object is not persistant
                last_seen.append(name)
                last_seen.pop(0)

                inferred_times = last_seen.count(name)
                if inferred_times / len(last_seen) > PERSISTANCE_THRESHOLD:  # over quarter time
                    persistant_obj = True

                detecttext = name.replace("_", " ")
                detecttextfont = smallfont
                detecttext_color = (0, 255, 0) if persistant_obj else (255, 255, 255)
                detecttext_surface = detecttextfont.render(detecttext, True, detecttext_color)
                detecttext_position = (screen.get_width()//2,
                                       screen.get_height() - detecttextfont.size(detecttext)[1])
                screen.blit(detecttext_surface, detecttext_surface.get_rect(center=detecttext_position))
                
		client.publish(topic, "Ritika")
                
                break

            elif label == 2 and conf > CONFIDENCE_THRESHOLD:
                print("Detected", name)

                persistant_obj = False  # assume the object is not persistant
                last_seen.append(name)
                last_seen.pop(0)

                inferred_times = last_seen.count(name)
                if inferred_times / len(last_seen) > PERSISTANCE_THRESHOLD:  # over quarter time
                    persistant_obj = True

                detecttext = name.replace("_", " ")
                detecttextfont = smallfont
                detecttext_color = (0, 255, 0) if persistant_obj else (255, 255, 255)
                detecttext_surface = detecttextfont.render(detecttext, True, detecttext_color)
                detecttext_position = (screen.get_width()//2,
                                       screen.get_height() - detecttextfont.size(detecttext)[1])
                screen.blit(detecttext_surface, detecttext_surface.get_rect(center=detecttext_position))

		client.publish(topic, "Unknown")
                
                break

        else:
            last_seen.append(None)
            last_seen.pop(0)
            if last_seen.count(None) == len(last_seen):
                last_spoken = None

        pygame.display.update()

if __name__ == "__main__":
    args = parse_args()
    try:
        main(args)
    except KeyboardInterrupt:
        capture_manager.stop()

