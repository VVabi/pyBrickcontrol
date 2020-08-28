from ble.blt_device import *
import gatt
import time
import threading
from protocol.brick_cmd import *
from pynput import keyboard
import pygame

def foo():
    while 1:
        pygame.event.wait()

manager = gatt.DeviceManager(adapter_name='hci0')

device = BrickBLEDevice(mac_address='90:84:2B:58:1A:B1', manager=manager)
device.connect()
print("Connected")

x = threading.Thread(target=manager.run)
x.start()
time.sleep(1)
device.prepare()


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
    blue = pygame.joystick.Joystick(0)
    blue.init()
    red = pygame.joystick.Joystick(1)
    red.init()

y = threading.Thread(target=foo)
y.start()

print(red.get_numbuttons())
print(blue.get_numbuttons())

last_shift  = 0
gear        = 1

shift_angles = [0, -90, -180, -270]

old_turn = 0
last_turn_change_ts = 0
while 1:
        now = time.time()

        down = blue.get_button(15)
        up   = red.get_button(15)

        tm = (now-last_shift > 1.0)
  
        if down > 0 and gear > 1 and tm:
            time.sleep(0.2)
            gear = gear-1
            angle = shift_angles[gear-1]
            cmd = brick_cmd(motor_go_to_position(30, 30, 0x01, angle))
            device.write_value(cmd.serialize())
            last_shift = now
        elif up > 0 and gear < 4 and tm:
            time.sleep(0.2)
            print("GOING UP")
            gear = gear+1
            angle = shift_angles[gear-1]
            cmd = brick_cmd(motor_go_to_position(30, 30, 0x01, angle))
            device.write_value(cmd.serialize())
            last_shift = now

        statusblue= blue.get_hat(0)
        statusred = red.get_hat(0)

        forward = -statusblue[0]

        if forward == 0:
            cmd = brick_cmd(set_motor_pwm(0, 0))
        elif forward == 1:
            cmd = brick_cmd(set_motor_pwm(-100, 0))  
        else:
            cmd = brick_cmd(set_motor_pwm(100, 0))
 
        device.write_value(cmd.serialize())   
        time.sleep(0.02)

        turn = statusred[1]

        change = (turn != old_turn) or (now-last_turn_change_ts < 1.0)
        if change:
            if (turn != old_turn):
                last_turn_change_ts = now
            if turn == 0:
                cmd = brick_cmd(motor_go_to_position(100, 100, 0x03, 0))
            elif turn == 1:
                cmd = brick_cmd(motor_go_to_position(100, 100, 0x03, -70))
            else:
                cmd = brick_cmd(motor_go_to_position(100, 100, 0x03, 70))    
        device.write_value(cmd.serialize())
        time.sleep(0.05)

while True:
    with keyboard.Events() as events:
        # Block for as much as possible
        event = events.get(1e6)
        if event.key == keyboard.KeyCode.from_char('q'):
            cmd = brick_cmd(set_motor_pwm(100, 0))
        elif event.key == keyboard.KeyCode.from_char('w'):
            cmd = brick_cmd(set_motor_pwm(-100, 0))
        elif event.key == keyboard.KeyCode.from_char('a'):
            cmd = brick_cmd(motor_go_to_position(100, 100, 0x03, 60))
        elif event.key == keyboard.KeyCode.from_char('s'):
            cmd = brick_cmd(motor_go_to_position(100, 100, 0x03, 0))
        elif event.key == keyboard.KeyCode.from_char('d'):
            cmd = brick_cmd(motor_go_to_position(100, 100, 0x03, -60))
        elif event.key == keyboard.KeyCode.from_char('b'):
            cmd = brick_cmd(motor_go_to_position(30, 30, 0x01, 0))
        elif event.key == keyboard.KeyCode.from_char('n'):
            cmd = brick_cmd(motor_go_to_position(30, 30, 0x01, -90))  
        elif event.key == keyboard.KeyCode.from_char('m'):
            cmd = brick_cmd(motor_go_to_position(30, 30, 0x01, -180))
        elif event.key == keyboard.KeyCode.from_char(';'):
            cmd = brick_cmd(motor_go_to_position(30, 30, 0x01, -270))    
        else:
            cmd = brick_cmd(set_motor_pwm(0, 0))


        device.write_value(cmd.serialize())

#cmd = brick_cmd(motor_go_to_position(100, 100, 0x03, -120))
#device.write_value(cmd.serialize())
#time.sleep(2)
#cmd = brick_cmd(set_motor_pwm(100, 0))
#device.write_value(cmd.serialize())
#cmd = brick_cmd(set_motor_pwm(100, 0))
#ts = time.time() 
#device.write_value(cmd.serialize())
#now = time.time()
#print(now-ts)
#cmd = brick_cmd(set_motor_pwm(0, 0))
#device.write_value(cmd.serialize())   