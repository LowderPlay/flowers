import json
import time

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522, MFRC522

reader = SimpleMFRC522()
reader.READER = MFRC522(spd=1000000)

try:
    while True:
        id, text = reader.read()
        print(id)
        print(text)
        time.sleep(0.1)
    # id, text = reader.write("A"*48)
    # print(id)
    # print(text)
finally:
    GPIO.cleanup()