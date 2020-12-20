import paho.mqtt.client as mqtt
import threading
import sys
import json
import time
import pygame

#red:
#A 0
#X 1
#B 2
#Y 3
#ZR 15
#R   14   
# blue:
# L 14
# ZL 15
# <-    0
# up   2
# down  1
# ->      3



def red_hat_cb(client, status):
    pwm = 100*status[0]
    cmd = dict()
    cmd["port"] = "A"
    cmd["pwm"]  = pwm
    client.publish("bottom/brickcontrol/motor/pwm", json.dumps(cmd)) 

def blue_hat_cb(client, status):
    pwm = 100*status[0]
    cmd = dict()
    cmd["port"] = "B"
    cmd["pwm"]  = pwm
    client.publish("bottom/brickcontrol/motor/pwm", json.dumps(cmd)) 

def run_top_motor(client, pwm, port):
    cmd = dict()
    cmd["port"] = port
    cmd["pwm"]  = pwm
    client.publish("top/brickcontrol/motor/pwm", json.dumps(cmd)) 

class gamepad:
    def __init__(self, gamepad):
        self.gamepad = gamepad
        self.cbs = dict()
        self.last_status = dict()
        self.hat_status = dict()
        self.hat_cb = dict()

    def register_button_cb(self, button, cb):
        self.cbs[button] = cb
        self.last_status[button] = self.gamepad.get_button(button)


    def run(self, client):
        for key, value in self.last_status.items():
            new_status = self.gamepad.get_button(key)
            if value != new_status:
                self.cbs[key](client, new_status)
                self.last_status[key] = new_status
        for key, value in self.hat_status.items():
            new_hat = self.gamepad.get_hat(key)
            if new_hat != value:
                self.hat_cb[key](client, new_hat)
                self.hat_status[key] = new_hat

    def register_hat_cb(self, id, cb):
        self.hat_cb[id] = cb
        self.hat_status[id]= self.gamepad.get_hat(id)



def pygame_wait_loop():
    while 1:
        pygame.event.wait()

def on_message(client, userdata, message):
    try:
        payload = json.loads(str(message.payload.decode("utf-8")))
        print("received message =", payload)
        global angle
        angle = payload["position"]
    except:
        print("An exception occurred") 



def shift(client, shift_angle, target_gear):
    cmd = dict()
    cmd["pwm"]   = 20
    cmd["max_power"] = 40
    cmd["port"]  = "B"
    cmd["target_angle"] = shift_angle+90*target_gear
    payload = json.dumps(cmd)
    client.publish("top/brickcontrol/motor/go_to_position", payload)

def run_gamepad(host):
    print(angle)
    client = mqtt.Client()
    client.on_message=on_message
    client.connect(host)
    client.loop_start()
    client.subscribe('top/brickcontrol/motor/output/position_update')
    enable_mode_update = '{"port": "B", "mode": 2, "notifications_enabled": 1, "delta": 5}'
    client.publish('top/brickcontrol/generic/set_mode_update', enable_mode_update)

    cmd = dict()
    cmd["pwm"]   = 20
    cmd["max_power"] = 20
    cmd["port"]  = "B"
    cmd["target_angle"] = 50
    payload = json.dumps(cmd)

    client.publish("top/brickcontrol/motor/go_to_position", payload)
    time.sleep(2)

    cmd = dict()
    cmd["pwm"]   = 20
    cmd["max_power"] = 20
    cmd["port"]  = "B"
    cmd["target_angle"] = -1000
    payload = json.dumps(cmd)

    client.publish("top/brickcontrol/motor/go_to_position", payload)
    time.sleep(2)
    shift_angle = angle
    print("SHIFT ANGLE")
    print(shift_angle)

    pygame.init()
    pygame.display.init()
    # Initialize the joysticks
    pygame.joystick.init()

    joystick_count = pygame.joystick.get_count()
    print ("There is ", joystick_count, "joystick/s")
    if joystick_count < 2:
        print ("Error, I did not find enough gamepads")
    else:
        if pygame.joystick.Joystick(0).get_name() == 'Joy-Con (L)':
            blue = pygame.joystick.Joystick(0)
            red = pygame.joystick.Joystick(1)
        else:
            blue = pygame.joystick.Joystick(1)
            red = pygame.joystick.Joystick(0)

        blue.init()
        red.init()

    y = threading.Thread(target=pygame_wait_loop)
    y.start()
    
    blue_gp = gamepad(blue)
    blue_gp.register_button_cb(0, lambda client, status : shift(client, shift_angle, 0))
    blue_gp.register_button_cb(1, lambda client, status : shift(client, shift_angle, 1))
    blue_gp.register_button_cb(2, lambda client, status : shift(client, shift_angle, 2))
    blue_gp.register_button_cb(3, lambda client, status : shift(client, shift_angle, 3))
    red_gp = gamepad(red)
    red_gp.register_button_cb(0, lambda client, status : run_top_motor(client, 100*status, 'A'))
    red_gp.register_button_cb(1, lambda client, status : run_top_motor(client, -100*status, 'A'))
    red_gp.register_button_cb(2, lambda client, status : run_top_motor(client, 100*status, 'C'))
    red_gp.register_button_cb(3, lambda client, status : run_top_motor(client, -100*status, 'C'))


    red_gp.register_hat_cb(0, red_hat_cb)
    blue_gp.register_hat_cb(0, blue_hat_cb)
    while 1:
        blue_gp.run(client)
        red_gp.run(client)
        time.sleep(0.02)


angle   = 0

run_gamepad("127.0.0.1")        