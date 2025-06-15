import serial 

import numpy as np


class StepperMotor  (object): 
    COMMANDS = {"SET": {"MOVE": bool,  "RES": int,"DIR": bool,  "STEPS": int, "SPEED": float, "LOWERLIM": int, "UPPERLIM": int , "PULPIN": int, "DIRPIN": int}, 
    "GET": {"MOVE": bool, "RES": int, "DIR": bool, "STEPS": int, "SPEED": float, "LOWERLIM": int, "UPPERLIM": int}}
    DELAY = 0.5
    def __init__(self, stepper_pin, dir_pin, com_port):
        self._pin_pul: int = stepper_pin
        self._pin_dir: int = dir_pin
        self._com: str = com_port 
        self._ser: None
        self._connected = False
        self._connect()
        self._resolution: int = 1
        self._speed: float = 1.0
        self._direction = False
        self._moving  = False
        self._step_count = 0
        self._delay = 100

        self._step_limit_lower = -10**100
        self._step_limit_upper =  10**100

    def _connect(self):
        try: 
            self._ser = serial.Serial(self._com, baudrate=115200, timeout=None)
            if self._ser is not None: 
                self._connected = True
                self.pin_dir = self._pin_dir
                self.pin_pul = self._pin_pul
            else:
                self._connected = False
        except:
            self._connected = False
        
    
    def _send(self, cmd, key, value=None):
        
        if cmd not in self.COMMANDS.keys(): raise ValueError("Invalid Command:", cmd)
        if key not in self.COMMANDS[cmd].keys(): raise ValueError("Invalid Command:", cmd, key)

        command = f'{cmd} {key} {value}\r\n'
        command = command.encode('utf-8')
        if self._connected: 
            self._ser.write(command)




    def _receive(self, key):

        if self._connected:
            
            line = self._ser.readline()

            line = line.strip()

            line = line.decode('utf-8')

        try:
            value = self.COMMANDS['GET'][key](line)
            return value 
        except:
            ValueError("Got unexpected message from board")
        
    @property
    def connected(self):
        return self._connected
    @property
    def pin_dir(self):
        return self._pin_dir
    
    @pin_dir.setter
    def pin_dir(self, value):
        if not isinstance(value, int):
            raise ValueError("Direction Pin has to be integer")
        self._send('SET', 'DIRPIN', value)
        self._pin_dir = value
    
    @property
    def pin_pul(self):
        return self._pin_pul

    @pin_pul.setter
    def pin_pul(self, value):
        if not isinstance(value, int):
            raise ValueError("Direction Pin has to be integer")
        self._send('SET', 'PULPIN', value)
        self._pin_pul = value

    @property
    def resolution(self):
        self._send('GET', 'RES')
        return self._receive('RES')
    @resolution.setter
    def resolution(self, value):
        if not isinstance(value, int):
            raise ValueError("Resolution has to be integer")
        self._send('SET', 'RES', value)
        self._resolution = value
    
    @property
    def speed(self):
        self._send('GET', 'SPEED')
        return self._receive('SPEED')
    @speed.setter
    def speed(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("Resolution has to be integer/float")
        self._send('SET', 'SPEED', value)
        self._speed = value 
    @property
    def direction(self):
        self._send('GET', 'DIR')
        return self._receive('DIR')

    @direction.setter
    def direction(self, value):
        if not isinstance(value, bool):
            raise ValueError("Direction has to be bool")
        self._send('SET', 'DIR', value)
        self._direction = value

    def rotate(self):
        if self._connected:
            self._send('SET', 'MOVE', True)
        
    def stop(self):
        if self._connected:
            self._send('SET', 'MOVE', False)
    @property
    def moving(self):
        self._send('GET', 'MOVE')
        return self._receive('MOVE')
    
    @property
    def step_count(self):
        self._send('GET', 'STEPS')
        return self._receive('STEPS')
    
    def zero_steps(self):
        self._send('SET', 'STEPS', 0)

    @property
    def lower_lim(self):
        self._send('GET', 'LOWERLIM')
        return self._receive('LOWERLIM')

    @lower_lim.setter
    def lower_lim(self, value):
        if not isinstance(value, int):
            raise ValueError("Limit has to be aset as int")
        self._send('SET', 'LOWERLIM', value)
    @property
    def upper_lim(self):
        self._send('GET', 'UPPERLIM')
        return self._receive('UPPERLIM')


    @upper_lim.setter
    def upper_lim(self, value):
        if not isinstance(value, int):
            raise ValueError("Limit has to be aset as int")
        self._send('SET', 'UPPERLIM', value)

    def close(self):
        if self._connected:
            self._ser._close()
        
        


class MockSerial:
    def __init__(self, *args, **kwargs):
        self.buffer = []

    def write(self, command):
        print(f"Mock write: {command.decode('utf-8').strip()}")

    def readline(self):
        # Simulate responses based on commands sent
        if self.buffer:
            return self.buffer.pop(0)
        return b'0\n'  # Default response for GET commands

    def close(self):
        print("Mock close called.")


class DebugStepperMotor(StepperMotor):
    def __init__(self, stepper_pin, dir_pin, com_port):
        # Replace actual serial with MockSerial
        self._ser = MockSerial()
        self._connected = True  # Simulate being connected
        super().__init__(stepper_pin, dir_pin, com_port)

    def _connect(self):
        # Override to avoid trying to connect to real serial port
        self._connected = True
    @property
    def step_count(self):
        return np.random.randint(10)
# Example usage:


        

import time

if __name__ == "__main__":
    motor = DebugStepperMotor(stepper_pin=1, dir_pin=2, com_port='COM3')

    # Setting properties and observing debug prints
    motor.pin_dir = 3  # Should print "Setting pin_dir to 3"
    current_speed = motor.speed  # Should print "Getting speed"

    # You can also simulate sending commands and receiving responses by modifying the buffer.
    motor._ser.buffer.append(b'100\n')  # Simulate response for speed
    print(motor.speed)  # Sh

    t = StepperMotor(10, 11,'COM5')
    # t.resolution = 1600
    
    # t.speed = 0.4
    
    # t.direction = True

    # t.rotate()
    
    # time.sleep(2)
    # t.direction = False
    # t.stop()
    # print('out', t.step_count)
    # t.rotate()
    # time.sleep(1)
    # t.stop()

    # t.zero_steps()
    # print('out', t.step_count)
    
    # print(t.upper_lim)
    # t.upper_lim = 50000
    # print(t.upper_lim)
    # print(t.lower_lim)
    # time.sleep(1)
    # print(t._ser.read_all())
    # t.close()
