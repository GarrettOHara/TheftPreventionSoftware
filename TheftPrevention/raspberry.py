import ctypes
import threading

from mybluetooth import btserver
from datetime import datetime
from queue import Queue
import signal
import sys
import cv2 # pip install opencv-python
import SMS
import Alarm
import time
import os

bluetooth_server = None
user_phone_number = None
enabled = False

img_buffer_size = 10
img_buffer = []

def signal_handler(sig, frame):
    bluetooth_server.shutdown()
    sys.exit(1)


def save_images():
    global img_buffer

    for i, img in zip(range(len(img_buffer)), img_buffer):
        file_name = os.path.join("capture"+str(i)+".png") # Timestamp
        cv2.imwrite(file_name, img)

def bt_data_received(tuple_data):
    global user_phone_number, enabled, img_buffers

    key = tuple_data[0]
    data = tuple_data[1]

    if key == "imgs":
        print("received images")
        for img in data:
            img_buffer.append(img)

            if len(img_buffer) > img_buffer_size:
                del img_buffer[0]


    if key == "#":
        user_phone_number = data
        print("received user phone#:", user_phone_number)
    elif key == "en":
        enabled = True
        print("system enabled")
    elif key == "dis":
        enabled = False
        print("system disabled")
    elif key == "sms":
        if user_phone_number is not None:
            SMS.send_sms(user_phone_number)


def laptop_disconnected():
    global user_phone_number, enabled

    print("laptop disconnected")
    if enabled and user_phone_number is not None:
        print("sending sms.")
        #SMS.send_sms(user_phone_number)
        #Alarm.play_alarm()
        save_images()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    #time.sleep(10)
    bluetooth_server = btserver.BTServer()
    bluetooth_server.add_connect_listener(lambda: print("client connected."))
    bluetooth_server.add_disconnect_listener(laptop_disconnected)
    bluetooth_server.add_data_recv_listener(bt_data_received)
    print("Starting bluetooth server")
    bluetooth_server.start()
    print("Started")
    # don't let thread finish. Or else SIGINT handler wont work
    while True:
        time.sleep(50)
