import serial 




class StepperMotor(object): 
    def __intit__(self, stepper_pin, dir_pin, com_port):
        self._pin_pul: int = stepper_pin
        self._pin_dir: int = dir_pin
        self._com: str = com_port 

        self._connected = False
        self._connect()

    def _connect(self):
        pass
    
    def _send(self, key, value):
        pass

    def _receive(self):
        pass

import time

if __name__ == "__main__":
    ser  =serial.Serial('COM8', baudrate=115200, timeout=0.1)
    line = "SET PULPIN 2\r\n"
    ser.write(line.encode('utf-8'))
    time.sleep(1)
    line = "SET DIRPIN 3\r\n"
    ser.write(line.encode('utf-8'))
    time.sleep(1)
    line = 'SET RES 1600\r\n'
    ser.write(line.encode('utf-8'))
    time.sleep(1)
    line = 'SET SPEED 0.1\r\n'
    ser.write(line.encode('utf-8'))
    time.sleep(1)
    line = 'SET DIR True\r\n'
    ser.write(line.encode('utf-8'))
    line = 'SET MOVE True\r\n'
    time.sleep(1)
    ser.write(line.encode('utf-8'))
    
    time.sleep(4)
    print("t2")
    line = 'SET MOVE False\r\n'
    ser.write(line.encode('utf-8'))
    time.sleep(1)
    
    print(ser.read_all().decode('utf-8'))

    # print("t4")
    ser.close()
    # print("t5")