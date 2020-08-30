import gatt
import time
import threading
from protocol.cmd_types import cmd_type
from protocol.brick_cmd import *

class BrickBLEDevice(gatt.Device):
    cbs = dict()
    send_ts = 0
    characteristic_handlers = list()
    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))

    def services_resolved(self):
        super().services_resolved()
        print("resolved")
	
    def characteristic_value_updated(self, characteristic, value):
        id = value[2]
        #print(id)
        if not id in self.cbs:
            return

        print("calling handler")
        handler = self.cbs[id]
        handler(value)

    def prepare(self):
        self.characteristic_handlers.clear()
        lego_service = next(
            s for s in self.services
            if s.uuid == '00001623-1212-efde-1623-785feabcd123')
	
        lego_characteristic = next(
            c for c in lego_service.characteristics
            if c.uuid == '00001624-1212-efde-1623-785feabcd123') 	  
        lego_characteristic.enable_notifications()
        self.characteristic_handlers.append(lego_characteristic)

    available = True
    def characteristic_write_value_succeeded(self, characteristic):
        print(time.time())
        self.available = True

    def write_value(self, cmd):
        while not self.available:
            if time.time() - self.send_ts > 1.0:
                break

        print("SENDING")
        print(time.time())
        self.available = False
        self.send_ts   = time.time()
        if not self.characteristic_handlers:
            print("No characteristic to write to found, please call prepare first!")
            return
        self.characteristic_handlers[0].write_value(cmd)

    def register_cb(self, type, cb):    
        self.cbs[type.value] = cb


def on_mode_update(value):
    print("VALUE UPDATE")
    print(value[3])
    x = int.from_bytes(value[4:], signed=True, byteorder="little")
    print(x)

def launch_brick_ble_communication():
    manager = gatt.DeviceManager(adapter_name='hci0')
    manager.start_discovery()
    device = BrickBLEDevice(mac_address='90:84:2B:58:1A:B1', manager=manager)
    device.connect()


    x = threading.Thread(target=manager.run)
    x.start()
    time.sleep(1)
    device.prepare()
   
    device.register_cb(cmd_type.PORT_VALUE, on_mode_update)
    device.write_value(brick_cmd(enable_mode_updates(port=0x01, mode=0x02, notifications_enabled=1, delta=5)).serialize())
    device.write_value(brick_cmd(enable_mode_updates(port=0x03, mode=0x02, notifications_enabled=1, delta=5)).serialize())
    return device