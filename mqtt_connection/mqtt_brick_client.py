import paho.mqtt.client as mqtt
import threading
import sys
import json
import time
from protocol.brick_cmd import *
import queue
from protocol.cmd_types import cmd_type

class mqtt_brick_client:
    def __init__(self, host):
        self.json_queue = queue.Queue()
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(host)
        self.client.loop_start()

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

    def on_property_update(self, value):
        print("ON UPDATE")

        if (value[3] == 0x06):
            v = value[5]
            response = dict()
            response["battery_charging_state"] = v
            self.client.publish("brick/properties/battery", json.dumps(response))

    def run(self, hub_device):
        hub_device.register_cb(cmd_type.HUB_PROPERTIES, self.on_property_update)
        while True:
            while (self.json_queue.qsize() > 10):
                self.get_next_message()

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
                hub_device.write_value(cmd.serialize())  