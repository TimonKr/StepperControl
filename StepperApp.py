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



DEBUG = True
CONNECTION_INTERVAL= 10 
    




class ControlWindow(BoxLayout):
    stepper_res_ip = ObjectProperty(None)
    com_ip = ObjectProperty(None)
    speed_ip = ObjectProperty(None)
    pin_pul_id = ObjectProperty(None)
    pin_dir_id = ObjectProperty(None)
    connection_idc = ObjectProperty(None)

    






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
        self.motor = init_board_connection(self.config['settings'], DEBUG)
         
        for key in self.settings:
            self.settings[key].text = str(self.config['settings'][key])

        
        
        

    def update_settings(self, instance,focus, key, ttype):
        try: 
            if not focus: 
                self.config.set('settings', key, ttype(instance.text))            
                self.config.write()
                if self.motor.conencted:
                    if key == 'Com Port':
                        self.motor.close()
                        self.motor = init_board_connection(self.config['settings'], DEBUG)
                    elif key == 'Direction Pin':
                        self.motor.pin_dir = int(self.config['settings'][key])
                    elif key == 'Puls Pin':
                        self.motor.pin_pul = int(self.config['settings'][key])
                    elif key == 'Speed':
                        self.motor.speed = float(self.config['settings'][key])
                    elif key == 'Stepper Resolution':
                        self.motor.resolution = int(self.config['settings'][key])



        except:
            pass # i know im a lazy bitch

    def update_stepper_res(self):
        if self.motor.connected:
            self.motor.resolution = int()


    def check_connection(self, dt):
        try:
            color = (0, 1, 0, 1) if self.motor.connected else (1, 0, 0, 1)
            self.control.connection_idc.canvas.before.children[0].rgba = color
            if not self.motor.connected:
                self.motor = init_board_connection(self.config['settings'], DEBUG)
            
        except: 
            pass

def init_board_connection(config, debug):
    if debug: 
        motor = DebugStepperMotor(config['Puls Pin'], config['Direction pin'], config['Com Port'])
    else:
        motor = StepperMotor(config['Puls Pin'], config['Direction pin'], config['Com Port'])

    motor.resolution = int(config['Stepper Resolution'])
    motor.speed = float(config['Speed'])
    return motor






if __name__ == "__main__":
    StepperApp().run()