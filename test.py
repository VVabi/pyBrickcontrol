from ble.blt_device import *
import gatt
import time
import threading
from pynput import keyboard
import pygame
from mqtt_connection.mqtt_brick_client import *
import gamepad

manager = gatt.DeviceManager(adapter_name='hci0')

device = BrickBLEDevice(mac_address='90:84:2B:58:1A:B1', manager=manager)
device.connect()
print("Connected")

x = threading.Thread(target=manager.run)
x.start()
time.sleep(1)
device.prepare()

client = mqtt_brick_client("localhost")
mp = dict()

T = threading.Thread(target=client.run, args = (device,))
T.start()


gamepad.run_gamepad("localhost")