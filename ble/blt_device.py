import gatt
import time
import threading

class BrickBLEDevice(gatt.Device):
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
        print(value)
        pass

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

    
    def characteristic_write_value_succeeded(self, characteristic):
        pass

    def write_value(self, cmd):
        if not self.characteristic_handlers:
            print("No characteristic to write to found, please call prepare first!")
            return
        self.characteristic_handlers[0].write_value(cmd)
        

def launch_brick_ble_communication():
    manager = gatt.DeviceManager(adapter_name='hci0')
    manager.start_discovery()
    device = BrickBLEDevice(mac_address='90:84:2B:58:1A:B1', manager=manager)
    device.connect()
    print("Connected")

    x = threading.Thread(target=manager.run)
    x.start()
    time.sleep(1)
    device.prepare()
    return device