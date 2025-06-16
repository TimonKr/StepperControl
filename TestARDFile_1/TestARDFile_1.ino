/*
 * Example Arduino code rewriting your MicroPython stepper motor example. 
 * 
 * Hardware assumptions:
 *  - Two digital pins controlling DIR (direction) and PUL (step) signals.
 *  - "resolution" is the number of microsteps per full revolution (e.g., 200 for a typical 1.8° stepper).
 *  - "speed" in revolutions per second (RPS).
 *  - Optional step limits (_step_limit_lower and _step_limit_upper).
 * 
 * Usage (over Serial):
 *    SET PULPIN <pin>
 *    SET DIRPIN <pin>
 *    SET RES <int>
 *    SET SPEED <float>
 *    SET DIR <true|false>
 *    SET MOVE <true|false>
 *    SET STEPS <int>
 *    SET LOWERLIM <int>
 *    SET UPPERLIM <int>
 *    GET MOVE
 *    GET RES
 *    GET SPEED
 *    GET DIR
 *    GET STEPS
 *    GET LOWERLIM
 *    GET UPPERLIM
 * 
 * Example:
 *    SET PULPIN 8
 *    SET DIRPIN 9
 *    SET RES 200
 *    SET SPEED 1
 *    SET DIR true
 *    SET MOVE true
 *    GET STEPS
 *
 * Make sure to open the Serial Monitor/Serial Plotter, set a matching baud (115200)
 * and send commands ending with a newline.
 */

#include <Arduino.h>

class StepperMotor {
private:
    int       _pin_pul    = -1;
    int       _pin_dir    = -1;
    long      _step_count = 0;
    long      _step_limit_lower = -2147483647; // default large negative
    long      _step_limit_upper =  2147483647; // default large positive

    // For controlling direction:
    bool      _direction  = false; // false = (e.g.) “reverse”, true = “forward”
    int       _step_increment = -1; // +1 if direction=true, -1 otherwise

    int       _resolution = 200;    // steps per revolution
    float     _speed      = 1.0;    // revolutions per second

    // Non-blocking step timing:
    bool      _moving     = false;
    unsigned long _lastStepMicros = 0;
    unsigned long _stepIntervalMicros = 5000; // time between steps in microseconds

    // Called whenever we want to generate one step pulse
    void stepMotor() {
        // Turn the step pin on briefly
        digitalWrite(_pin_pul, HIGH);
        // A small pulse width; 10-20 microseconds is often enough for most drivers
        delayMicroseconds(10);
        digitalWrite(_pin_pul, LOW);

        // Increment or decrement our internal step counter
        _step_count += _step_increment;
        
        // Check limit
        if (_step_count > _step_limit_upper || _step_count < _step_limit_lower) {
            stop();
        }
    }

    // Recompute the timing based on resolution & speed
    void updateStepInterval() {
        // stepsPerSecond = _resolution * _speed
        // interval in microseconds = 1e6 / stepsPerSecond
        if (_resolution > 0 && _speed > 0) {
            float stepsPerSec = float(_resolution) * _speed;
            _stepIntervalMicros = (unsigned long)(1000000.0f / stepsPerSec);
        }
    }

public:
    StepperMotor() {}
    
    // Call this from loop() to generate step pulses if moving
    void update() {
        if (_moving) {
            unsigned long nowMicros = micros();
            if (nowMicros - _lastStepMicros >= _stepIntervalMicros) {
                _lastStepMicros = nowMicros;
                stepMotor();
            }
        }
    }

    // Basic movement control
    void move(bool dir) {
        setDirection(dir);  // set direction pin
        move();             // start moving
    }
    void move() {
        if (_pin_dir == -1 || _pin_pul == -1) {
            // Not initialized properly
            Serial.println("StepperMotor not fully initialized (pins).");
            return;
        }
        if (!_moving) {
            _moving = true;
            // Immediately set direction pin
            digitalWrite(_pin_dir, _direction ? HIGH : LOW);
            _lastStepMicros = micros(); // restart timing
        }
    }
    void stop() {
        _moving = false;
    }

    // “Properties”
    bool isMoving() const {
        return _moving;
    }
    // Direction
    void setDirection(bool dir) {
        _direction = dir;
        _step_increment = (_direction ? 1 : -1);
        if (_pin_dir != -1) {
            digitalWrite(_pin_dir, _direction ? HIGH : LOW);
        }
    }
    bool getDirection() const {
        return _direction;
    }
    // Speed (RPS)
    void setSpeed(float s) {
        if (s <= 0) {
            Serial.println("Invalid speed. Must be > 0. Ignoring.");
            return;
        }
        _speed = s;
        updateStepInterval();
    }
    float getSpeed() const {
        return _speed;
    }

    // Steps per revolution
    void setResolution(int res) {
        if (res <= 0) {
            Serial.println("Resolution must be a positive integer. Ignoring.");
            return;
        }
        _resolution = res;
        updateStepInterval();
    }
    int getResolution() const {
        return _resolution;
    }

    // Step count
    void setStepCount(long val) { _step_count = val; }
    long getStepCount() const { return _step_count; }

    // Limits
    void setLowerLimit(long val) { _step_limit_lower = val; }
    long getLowerLimit() const   { return _step_limit_lower; }
    void setUpperLimit(long val) { _step_limit_upper = val; }
    long getUpperLimit() const   { return _step_limit_upper; }

    // Pin setup
    void setPinPUL(int pin) {
        _pin_pul = pin;
        pinMode(_pin_pul, OUTPUT);
        digitalWrite(_pin_pul, LOW);
    }
    void setPinDIR(int pin) {
        _pin_dir = pin;
        pinMode(_pin_dir, OUTPUT);
        digitalWrite(_pin_dir, LOW);
    }
};

// A helper to interpret "true"/"false" from strings
bool strToBool(String s) {
    s.trim();
    s.toLowerCase();
    if (s == "false") return false;
    return true;
}

// Parse incoming line from Serial and act on the StepperMotor instance
void parse_command(const String &line, StepperMotor &motor) {
    if (line.length() == 0) return;  // ignore empty

    // Basic splitting by spaces
    int firstSpace = line.indexOf(' ');
    if (firstSpace == -1) {
        Serial.println("Invalid command. Usage: <SET|GET> <PARAM> <value>");
        return;
    }
    String cmd = line.substring(0, firstSpace);          // "SET" or "GET"
    String remainder = line.substring(firstSpace + 1);   // e.g. "RES 200"

    int secondSpace = remainder.indexOf(' ');
    if (secondSpace == -1) {
        // If this is a GET command with no third part, might be okay,
        // but generally we expect something
        Serial.println("Invalid command. Usage: <SET|GET> <PARAM> <value>");
        return;
    }

    String subcmd = remainder.substring(0, secondSpace);  // e.g. "RES"
    String valStr = remainder.substring(secondSpace + 1); // e.g. "200"

    // Convert numeric input as needed
    if (cmd == "SET") {
        if (subcmd == "MOVE") {
            bool moveVal = strToBool(valStr);
            if (moveVal) {
                motor.move();
            } else {
                motor.stop();
            }
        } else if (subcmd == "RES") {
            int r = valStr.toInt();
            motor.setResolution(r);
        } else if (subcmd == "SPEED") {
            float spd = valStr.toFloat();
            motor.setSpeed(spd);
        } else if (subcmd == "DIR") {
            bool dirVal = strToBool(valStr);
            motor.setDirection(dirVal);
        } else if (subcmd == "STEPS") {
            long steps = valStr.toInt();
            motor.setStepCount(steps);
        } else if (subcmd == "LOWERLIM") {
            long lli = valStr.toInt();
            motor.setLowerLimit(lli);
        } else if (subcmd == "UPPERLIM") {
            long uli = valStr.toInt();
            motor.setUpperLimit(uli);
        } else if (subcmd == "PULPIN") {
            int p = valStr.toInt();
            motor.setPinPUL(p);
        } else if (subcmd == "DIRPIN") {
            int p = valStr.toInt();
            motor.setPinDIR(p);
        } else {
            Serial.print("Unknown SET command: ");
            Serial.println(subcmd);
        }
    }
    else if (cmd == "GET") {
        if (subcmd == "MOVE") {
            Serial.println(motor.isMoving() ? "true" : "false");
        } else if (subcmd == "RES") {
            Serial.println(motor.getResolution());
        } else if (subcmd == "SPEED") {
            Serial.println(motor.getSpeed(), 6); // print with some decimals
        } else if (subcmd == "DIR") {
            Serial.println(motor.getDirection() ? "true" : "false");
        } else if (subcmd == "STEPS") {
            Serial.println(motor.getStepCount());
        } else if (subcmd == "LOWERLIM") {
            Serial.println(motor.getLowerLimit());
        } else if (subcmd == "UPPERLIM") {
            Serial.println(motor.getUpperLimit());
        } else {
            Serial.print("Unknown GET command: ");
            Serial.println(subcmd);
        }
    }
    else {
        Serial.print("Unknown command type: ");
        Serial.println(cmd);
    }
}

// Create a global StepperMotor object
StepperMotor motor;

void setup() {
    Serial.begin(115200);
    // Give a welcome message
    Serial.println("StepperMotor Arduino rewrite ready!");
    // You can set default pins here (comment out if you want them set via commands)
     motor.setPinPUL(8);
     motor.setPinDIR(9);
}

void loop() {
    // Read lines from Serial
    static String buffer;
    while (Serial.available() > 0) {
        char c = (char)Serial.read();
        if (c == '\n' || c == '\r') {
            // If there's a line, parse it
            if (buffer.length() > 0) {
                parse_command(buffer, motor);
                buffer = "";
            }
        } else {
            buffer += c;
        }
    }
    // Update stepper movement
    motor.update();
}