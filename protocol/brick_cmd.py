class set_motor_pwm:

    def __init__(self, desired_pwm, port):
        self.pwm = desired_pwm
        self.pwm = min(100, self.pwm)
        self.pwm = max(-100, self.pwm)
        self.port = port
        #TODO check port to be 0 <=, <= 3

    def serialize(self):
            pwm_as_byte = self.pwm
            if pwm_as_byte < 0:
                pwm_as_byte = pwm_as_byte+256
            
            payload = bytes([self.port, 0x01, 0x01, pwm_as_byte])
            return payload


    def get_cmd_id(self):
        return 0x81

class motor_go_to_position:

    def __init__(self, desired_pwm, max_power, port, target_angle):
        self.pwm = desired_pwm
        self.pwm = min(100, self.pwm)
        self.pwm = max(-100, self.pwm)
        self.port = port
        self.max_power = max_power
        self.max_power = min(100, self.max_power)
        self.max_power = max(0, self.max_power)
        self.target_angle = target_angle

    def serialize(self):
            pwm_as_byte = self.pwm
            if pwm_as_byte < 0:
                pwm_as_byte = pwm_as_byte+256

            sub = self.target_angle.to_bytes(4, 'little', signed = True);
            payload = bytes([self.port, 0x01, 0x0D, sub[0], sub[1], sub[2], sub[3], self.pwm, self.max_power, 127, 0])
            return payload


    def get_cmd_id(self):
        return 0x81

class request_battery_update:
    def serialize(self):
        payload = bytes([0x6, 0x5])
        return payload

    def get_cmd_id(self):
        return 0x01


class brick_cmd:
    def __init__(self, subcommand):
        self.id = subcommand.get_cmd_id()
        self.subcommand = subcommand

    def serialize(self):
        sub = self.subcommand.serialize()
        length = 3+len(sub)

        if length > 127:
            pass #TODO
        header = bytes([length, 0, self.id])
        return header+sub



    
