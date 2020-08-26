from ble.blt_device import *
import gatt
import time
import threading
from protocol.brick_cmd import *

manager = gatt.DeviceManager(adapter_name='hci0')

device = BrickBLEDevice(mac_address='90:84:2B:58:1A:B1', manager=manager)
device.connect()
print("Connected")

x = threading.Thread(target=manager.run)
x.start()
device.prepare()



cmd = brick_cmd(motor_go_to_position(100, 100, 0x03, 740))
device.write_value(cmd.serialize())
#time.sleep(2)
#cmd = brick_cmd(set_motor_pwm(100, 0))
#device.write_value(cmd.serialize())
cmd = brick_cmd(set_motor_pwm(0, 0))
device.write_value(cmd.serialize())
    