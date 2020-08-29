import paho.mqtt.client as mqtt
import threading
import sys
import json
import time
from protocol.brick_cmd import *
import queue

class mqtt_brick_client:
    def __init__(self, host):
        self.json_queue = queue.Queue()
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(host)

        T = threading.Thread(target=self.client.loop_forever)
        T.start()

    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe("brick/motor_pwm")
        self.client.subscribe("brick/motor_abs_position")
        self.client.subscribe("brick/read_battery")

    def on_message(self, client, userdata, msg):
        str_payload = msg.payload.decode("utf-8")
        topic   = msg.topic
        loaded_dict = json.loads(str_payload)
        entry =  {"topic":topic, "payload":loaded_dict}
        self.json_queue.put(entry)

    def get_next_message(self):
        return self.json_queue.get()

    def run(self, hub_device):
        while True:
            msg = self.get_next_message()
            if msg['topic'] == "brick/motor_abs_position":
                payload = msg['payload']
                cmd = brick_cmd(motor_go_to_position(payload['pwm'], payload['power'], payload['port'], payload['angle']))
                hub_device.write_value(cmd.serialize())
            elif msg['topic'] == "brick/motor_pwm":
                payload = msg['payload']
                cmd = brick_cmd(set_motor_pwm(payload['pwm'], payload['port']))
                hub_device.write_value(cmd.serialize())
            elif msg['topic'] == "brick/read_battery":
                print("Received battery cmd")
                cmd = brick_cmd(request_battery_update())
                print(cmd.serialize())
                hub_device.write_value(cmd.serialize())  