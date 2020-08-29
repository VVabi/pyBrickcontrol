from ble.blt_device import *
import gatt
import time
import threading
from mqtt_connection.mqtt_brick_client import *
import gamepad

device = launch_brick_ble_communication()
client = mqtt_brick_client("localhost")

mqtt_thread = threading.Thread(target=client.run, args = (device,))
mqtt_thread.start()

gamepad.run_gamepad("localhost")