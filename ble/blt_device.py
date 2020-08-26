import gatt

class BrickBLEDevice(gatt.Device):
    characteristic_handlers = list()
    waiting                 = False
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
        print("Notifications")
        for b in value:
        	print(b)

        if (value[2] == 130 and value[4] > 8): #TODO
            print("releasing")    
            self.waiting = False

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

                    	 	
    def write_value(self, cmd):
        if not self.characteristic_handlers:
            print("No characteristic to write to found, please call prepare first!")
            return
        print("Sending cmd")
        self.characteristic_handlers[0].write_value(cmd)
        self.waiting = True

        while self.waiting:
            pass

