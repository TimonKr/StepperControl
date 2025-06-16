from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image

from kivy.properties import BooleanProperty, ListProperty, ObjectProperty, StringProperty
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.graphics.texture import Texture


import serial
from StepperControl import StepperMotor, DebugStepperMotor



DEBUG = False
CONNECTION_INTERVAL= 10 
POSITION_INTERVAL = 1 




class ControlWindow(BoxLayout):
    stepper_res_ip = ObjectProperty(None)
    com_ip = ObjectProperty(None)
    speed_ip = ObjectProperty(None)
    pin_pul_id = ObjectProperty(None)
    pin_dir_id = ObjectProperty(None)
    connection_idc = ObjectProperty(None)
    pos_current_lb = ObjectProperty(None)
    pos_min_lb = ObjectProperty(None)
    pos_max_lb = ObjectProperty(None)
    






class StepperApp(App):
    def build(self):
        
        self.layout =  GridLayout(cols=1, rows=1,  size_hint_x=1, size_hint_y=1)
        self.control = ControlWindow()
        self.layout.add_widget(self.control)

        self.settings = { "Stepper Resolution": self.control.stepper_res_ip, 
                         "Com Port": self.control.com_ip,
                         "Speed": self.control.speed_ip,
                         "Puls Pin": self.control.pin_pul_id,
                         "Direction Pin": self.control.pin_dir_id
                         }


        
        self.connectivity_check = Clock.schedule_interval(self.check_connection, CONNECTION_INTERVAL)
        self.update_position = Clock.schedule_interval(self.update_stepper_pos, POSITION_INTERVAL)

        return self.layout
    
    def build_config(self, config):
        config.setdefaults("settings",{
                "Stepper Resolution": 200, 
                "Com Port": 'COM12',
                "Speed": 1,
                "Puls Pin": 6,
                "Direction Pin": 7
                })
    
    def on_start(self):
        self.motor = self.init_board_connection(DEBUG)
         
        for key in self.settings:
            self.settings[key].text = str(self.config['settings'][key])

        
        
        

    def update_settings(self, instance,focus, key, ttype):
        try: 
            if not focus: 
                self.config.set('settings', key, ttype(instance.text))            
                self.config.write()
                if self.motor.connected:
                    if key == 'Com Port':
                        self.motor.close()
                        self.motor = self.init_board_connection(DEBUG)
                    elif key == 'Direction Pin':
                        self.motor.pin_dir = int(self.config['settings'][key])
                    elif key == 'Puls Pin':
                        self.motor.pin_pul = int(self.config['settings'][key])
                    elif key == 'Speed':
                        self.motor.speed = float(self.config['settings'][key])
                        self.control.speed_ip.text = str(self.motor.speed)
                        self.config.set('settings', key, ttype(self.motor.speed))
                        self.config.write()
                    elif key == 'Stepper Resolution':
                        self.motor.resolution = int(self.config['settings'][key])



        except:
            pass # i know im a lazy bitch


    def check_connection(self, dt):
        try:
            color = (0, 1, 0, 1) if self.motor.connected else (1, 0, 0, 1)
            self.control.connection_idc.canvas.before.children[0].rgba = color
            if not self.motor.connected:
                self.motor = self.init_board_connection(DEBUG)
                
            
        except: 
            pass

    def update_stepper_pos(self, dt):
        if self.motor.connected:
            self.control.pos_current_lb.text = str(self.motor.step_count)

    def rotate_stepper(self, direction):
            if self.motor.connected:
                if self.motor.moving:
                    self.motor.stop()
                self.motor.direction = direction
                self.motor.rotate()

        
    def stop_stepper(self):
        if self.motor.connected:
            self.motor.stop()
    
    def set_stepper_lim(self, key, reset=False):
        if self.motor.connected:
            if key == 'lower':
                if reset:
                    self.motor.lower_lim = int(-10**100)
                    self.control.pos_min_lb.text = '000'
                else:
                    self.motor.lower_lim = int(self.motor.step_count)
                    self.control.pos_min_lb.text = str(self.motor.lower_lim)
            else:
                if reset:
                    self.motor.upper_lim = int(10**100)
                    self.control.pos_max_lb.text = '000'
                else:
                    self.motor.upper_lim = int(self.motor.step_count)
                    self.control.pos_max_lb.text = str(self.motor.upper_lim)
    
    def zero_stepper_pos(self):
        if self.motor.connected:
            self.motor.zero_steps()



    def init_board_connection(self, debug=False):
        config = self.config['settings']
        if debug: 
            motor = DebugStepperMotor(int(config['Puls Pin']), int(config['Direction pin']), config['Com Port'])
        else:
            motor = StepperMotor(int(config['Puls Pin']), int(config['Direction pin']), config['Com Port'])

        motor.resolution = int(config['Stepper Resolution'])
        motor.speed = float(config['Speed'])

        return motor






if __name__ == "__main__":
    StepperApp().run()