import paho.mqtt.client as mqtt
import threading
import sys
import json
import time
import pygame

def foo():
    while 1:
        pygame.event.wait()

def run_gamepad(host):
    client = mqtt.Client()
    client.connect(host)

    time.sleep(1) #TODO
    pygame.init()
    pygame.display.init()
    # Initialize the joysticks
    pygame.joystick.init()
    done = False

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

    y = threading.Thread(target=foo)
    y.start()

    print(red.get_numbuttons())
    print(blue.get_numbuttons())

    last_shift  = 0

    gear = 1
    shift_angles = [0, -90, -180, -270]

    old_turn = 0
    last_turn_change_ts = 0
    while 1:
        now = time.time()

        down = blue.get_button(15)
        up   = red.get_button(15)

        tm = (now-last_shift > 0.5)

        if down > 0 and gear > 1 and tm:
            time.sleep(0.2)
            gear = gear-1
            angle = shift_angles[gear-1]
            cmd = dict()
            cmd["pwm"]   = 30
            cmd["power"] = 30
            cmd["port"]  = 1
            cmd["angle"] = angle
            payload = json.dumps(cmd)

            client.publish("brick/motor_abs_position", payload)
            last_shift = now
        elif up > 0 and gear < 4 and tm:
            time.sleep(0.2)
            gear = gear+1
            angle = shift_angles[gear-1]
            cmd = dict()
            cmd["pwm"]   = 30
            cmd["power"] = 30
            cmd["port"]  = 1
            cmd["angle"] = angle
            payload = json.dumps(cmd)

            client.publish("brick/motor_abs_position", payload)

        statusblue= blue.get_hat(0)
        statusred = red.get_hat(0)

        forward = -statusblue[0]

        if forward == 0:
            pwm = 0
        elif forward == 1:
            pwm = -100
        else:
            pwm = 100
        cmd = dict()
        cmd["port"] = 0
        cmd["pwm"]  = pwm

        client.publish("brick/motor_pwm", json.dumps(cmd)) 
        time.sleep(0.02)

        turn = statusred[1]

        change = (turn != old_turn) or (now-last_turn_change_ts < 1.0)
        if change:
            if (turn != old_turn):
                last_turn_change_ts = now
            if turn == 0:
                angle = 0
            elif turn == 1:
                angle = -70
            else:
                angle = 70
            cmd = dict()
            cmd["pwm"]   = 100
            cmd["power"] = 100
            cmd["port"]  = 3
            cmd["angle"] = angle
            payload = json.dumps(cmd)

            client.publish("brick/motor_abs_position", payload)
        time.sleep(0.02)
