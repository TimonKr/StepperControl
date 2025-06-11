from machine import Pin, Timer
import time
import sys





class StepperMotor:
    def __init__(self):
        self._pin_pul: Pin = None
        self._pin_dir: Pin = None
        self._resolution: int = 1
        self._speed: float = 1.0
        self._direction = False
        self._step_increment = -1 
        self.initalized = False
        self._moving  = False
        self._step_count = 0
        self._delay = 100
        self._timer = Timer()
        self._step_limit_lower = -2**32
        self._step_limit_upper =  2**32
        
    @property
    def pin_dir(self):
        return self._pin_dir
    @property
    def pin_pul(self):
        return self._pin_pul

    @pin_dir.setter
    def pin_dir(self, value):
        if not isinstance(value, int):
            raise ValueError("Direction Pin has to be integer")
        self._pin_dir = Pin(value, Pin.OUT)
    @pin_pul.setter
    def pin_pul(self, value):
        if not isinstance(value, int):
            raise ValueError("Direction Pin has to be integer")
        self._pin_pul = Pin(value, Pin.OUT)
    @property 
    def step_count(self):
        return self._step_count
    @step_count.setter
    def step_count(self, value):
        if not isinstance(value, int):
            raise ValueError("Step count must be of type int")
        self._step_count = value
    @property
    def resolution(self):
        return self._resolution
    @resolution.setter
    def resolution(self, value):
        if not isinstance(value, int):
            raise ValueError("Resolution has to be given in steps per revolution as int.")
        self._delay = 1/(value*self._speed)
        self._resolution = value
    @property 
    def speed(self):
        return 1/(int(self._delay*1000)*1e-3*self._resolution)
    
    @speed.setter
    def speed(self, value):
        if not isinstance(value, (float, int)):
            raise ValueError("Speed has to be passed as float or in in rotations per second")
        self._delay = 1/(self._resolution*value)
        self._speed = value
        
    @property
    def direction(self):
        return self._direction
    @direction.setter
    def direction(self, value):
        if not isinstance(value, bool):
            raise ValueError("Direction has to be passed as bool")
        self._step_increment  = 1 if value else -1
        self._direction = value
    @property 
    def limit_lower(self):
        return self._step_limit_lower 
    @limit_lower.setter
    def limit_lower(self, value):
        if not isinstance(value, int): 
            raise ValueError("Step limits have to be passsed as int")
        self._step_limit_lower = value
    @property 
    def limit_upper(self):
        return self._step_limit_upper
    @limit_upper.setter
    def limit_upper(self, value):
        if not isinstance(value, int): 
            raise ValueError("Step limits have to be passsed as int")
        self._step_limit_upper = value
    @property
    def moving(self):
        return self._moving


    @property 
    def initialized(self):
        return self.pin_dir is not None and self.pin_pul is not None and self.resolution is not None
    
    def move(self, direction=None):
        if self.initialized and not self._moving:
            self._moving = True

            if isinstance(direction, bool):
                self.direction = direction
                
            if self.direction:
                self._pin_dir.on()
            else:
                self._pin_dir.off()
                
            self._timer.init(period=int(1000*self._delay), mode=Timer.PERIODIC, callback=self.step_motor)

    def step_motor(self, t):
        if self._step_limit_lower<=self.step_count <=self._step_limit_upper:
            self._pin_pul.on()
            time.sleep(self._delay)
            self._pin_pul.off()
            self._step_count += self._step_increment
        else: 
            self.stop()
            
    def stop(self):
        if self._moving:
            self._timer.deinit()  # Stop the timer
            self._moving = False

            


def parse_command(line, motor):
    COMMANDS = {"SET": {"MOVE": bool,  "RES": int,"DIR": bool,  "STEPS": int, "SPEED": float, "LOWERLIM": int, "UPPERLIM": int , "PULPIN": int, "DIRPIN": int}, 
                "GET": {"MOVE": bool, "RES": int, "DIR": bool, "STEPS": int, "SPEED": float, "LOWERLIM": int, "UPPERLIM": int}}

    parts = line.strip().split()

    if not parts:
        return  # Ignore empty lines
    #parts = [p.decode() for p in parts]
    cmd = parts[0]
    subcmd = parts[1]
    if len(parts) < 3:
        print("Invalid SET command. Usage: <SET|GET> <RESOLUTION|SPEED> <value>")
        return

   
    if cmd == "SET":

        
        value = COMMANDS[cmd][subcmd](parts[2])
        if subcmd == "MOVE":
            value = str_to_bool(parts[2])

            if value:
                motor.move()
            else: 
                motor.stop()

        elif subcmd == "RES":
            motor.resolution = value
        elif subcmd == "DIR":
            value = str_to_bool(parts[2])
            motor.direction = value
        elif subcmd == "STEPS":
            motor.step_count = value
        elif subcmd == "SPEED":
            motor.speed = value
        elif subcmd == "PULPIN":
            motor.pin_pul = value
        elif subcmd == "DIRPIN":
            motor.pin_dir = value
        elif subcmd == "LOWERLIM":
            motor.limit_lower = value
        elif subcmd == "UPPERLIM":
            motor.limit_upper = value
        else:
            print("Unknown SET command:", subcmd)

    elif cmd == "GET":
        if subcmd == "MOVE":
            print(motor.moving)
        elif subcmd == "RES":
            print(motor.resolution)
        elif subcmd == "DIR":
            print(motor.direction)
        elif subcmd == "STEPS":
            print(motor.step_count) 
        elif subcmd == "SPEED":
            print(motor.speed)
        elif subcmd == "LOWERLIM":
            print(motor.limit_lower)
        elif subcmd == "UPPERLIM":
            print(motor.limit_upper)
        else:
            print("Unknown SET command:", subcmd)
         
                   
def str_to_bool(s):
    if s.lower() == 'false':
        return False
    else:
        return True


time.sleep(2)
motor = StepperMotor()


while True:
    line = sys.stdin.readline().strip()
        
    parse_command(line, motor)


    
    