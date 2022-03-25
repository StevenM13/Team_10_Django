#!/usr/bin/env python
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.uix.slider import Slider
from kivy.properties import NumericProperty
from kivy.core.window import Window
from kivy.config import Config
from kivy.uix.switch import Switch
from kivy.lang import Builder
import RPi.GPIO as GPIO
import time

# # Set GPIO numbering mode
GPIO.setmode(GPIO.BOARD)

# Set pin 11 as an output, and set servo1 as pin 11 as PWM
GPIO.setup(11,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(15,GPIO.OUT)
GPIO.setup(16,GPIO.OUT)
GPIO.setup(29,GPIO.OUT)
GPIO.setup(31,GPIO.OUT)
GPIO.setup(33,GPIO.OUT)
GPIO.setup(35,GPIO.OUT)

Window.clearcolor = (0.5,0.5,0.6,0.9)
Window.fullscreen = 'auto'

class DishLayout(FloatLayout):
    elevation = 36.0
    azimuth = 90.0
    LPWM_Output = 11
    RPWM_Output = 13
    rotate_left = 29
    rotate_right = 31
    oldAzimuth = 0
    oldElevation = 0
    difference = 0

    def __init__(self,**kwargs):
        super(DishLayout,self).__init__(**kwargs)

        self.elevation_label = Label(text = format(self.elevation, ".2f"), size_hint=(.1, .15),pos_hint={'x':.45, 'y':.62})
        self.azimuth_label = Label(text = format(self.azimuth, ".2f"), size_hint=(.1, .15),pos_hint={'x':.45, 'y':.22})
        self.dish_status = Label(text = "Dish Status:", size_hint=(.1, .1), pos_hint={'x':.83,'y':.45}, color = (0,0,0,1))
        self.movingStatus = Label(text = "SET", size_hint=(.1, .1), pos_hint={'x':.83,'y':.4}, color = (0,0,0,1))

        # sliders
        self.elevationControl = Slider(min = 0, max = 72, size_hint=(.63, .2), pos_hint={'x':.18,'y':.49}, sensitivity = 'handle', value = self.elevation, step = 1, cursor_size = ("30sp", "40sp"))
        self.elevationControl.fbind('value', self.on_elev_slider)
        self.add_widget(self.elevationControl)
        self.azimuthControl = Slider(min = 0, max = 180, size_hint=(.63, .2), pos_hint={'x':.18,'y':.09}, sensitivity = 'handle', value = self.azimuth, step = 1, cursor_size = ("30sp", "40sp"))
        self.azimuthControl.fbind('value', self.on_az_slider)
        self.add_widget(self.azimuthControl)

        # Buttons
        self.inc_elev = Button(text = "+", size_hint=(.2, .15), pos_hint={'x':.62, 'y':.62}, on_release = self.incElev, background_color = (0.7,0.8,0.9,1))
        self.dec_elev = Button(text = "-", size_hint=(.2, .15),pos_hint={'x':.18, 'y':.62}, on_release = self.decElev, background_color = (0.7,0.8,0.9,1))
        self.inc_az = Button(text = "+", size_hint=(.2, .15),pos_hint={'x':.62, 'y':.22}, on_release = self.incAz, background_color = (0.7,0.8,0.9,1))
        self.dec_az = Button(text = "-", size_hint=(.2, .15),pos_hint={'x':.18, 'y':.22}, on_release = self.decAz, background_color = (0.7,0.8,0.9,1))
        self.execute = Button(text = "Execute Scroll Change", size_hint = (.25,.1), pos_hint={'x':.13,'y':.02}, on_release = self.moveDish, background_color = (0,0.8,0.4,1))
        self.exit = Button(text = "Exit", size_hint = (.25,.1), pos_hint={'x':.63,'y':.02}, on_release = self.exitProgram, background_color = (0.6,0.1,0,1))
        self.calibrate = Button(text = "Calibrate", size_hint = (.25,.1), pos_hint={'x':.38,'y':.02}, on_release = self.calibration, background_color = (0.8,0.8,0,1))

        # labels
        self.elev_text = Label(text = "Elevation", size_hint=(.1,.1), pos_hint={'x':.45,'y':.8}, color = (0,0,0,1))
        self.az_text = Label(text = "Azimuth", size_hint=(.1,.1), pos_hint={'x':.45,'y':.4}, color = (0,0,0,1))

        self.elev_text.font_size = '80dp'
        self.az_text.font_size = '80dp'
        self.elevation_label.font_size = '50dp'
        self.azimuth_label.font_size = '50dp'
        self.inc_elev.font_size = '60dp'
        self.dec_elev.font_size = '100dp'
        self.inc_az.font_size = '60dp'
        self.dec_az.font_size = '100dp'
        self.dish_status.font_size = '30dp'
        self.movingStatus.font_size = '30dp'

        self.add_widget(self.elev_text)
        self.add_widget(self.az_text)
        self.add_widget(self.elevation_label)
        self.add_widget(self.azimuth_label)
        self.add_widget(self.inc_elev)
        self.add_widget(self.dec_elev)
        self.add_widget(self.inc_az)
        self.add_widget(self.dec_az)
        self.add_widget(self.execute)
        self.add_widget(self.movingStatus)
        self.add_widget(self.dish_status)
        self.add_widget(self.exit)
        self.add_widget(self.calibrate)
        
    # calibration steps
        self.verify_elev = Button(text = "Click when linear motor is retracted", size_hint = (.25,.1), pos_hint={'x':.13,'y':.02}, on_release = self.elev_calibrated, background_color = (0,0.8,0.4,1))
        self.verify_az = Button(text = "Click when facing South", size_hint = (.25,.1), pos_hint={'x':.13,'y':.02}, on_release = self.calibrated, background_color = (0,0.8,0.4,1))
        
    def calibration(self,event):
        self.movingStatus.text = "CALIBRATING"
        self.add_widget(self.verif_elev)
        GPIO.output(15, GPIO.HIGH)
        GPIO.output(16, GPIO.HIGH)
        #### retract the linear actuator
        GPIO.output(self.RPWM_Output, GPIO.HIGH)
        GPIO.output(self.LPWM_Output, GPIO.LOW)
        self.elevationControl.disabled = True
        self.azimuthControl.disabled = True
        self.execute.disabled = True
        self.calibrate.disabled = True
        self.inc_elev.disabled = True
        self.dec_elev.disabled = True
        self.inc_az.disabled = True
        self.dec_az.disabled = True
           
    def elev_calibrated(self,event):
        self.remove_widget(self.verify_elev)
        #### stop the linear actuator
        GPIO.output(15, GPIO.LOW)
        GPIO.output(16, GPIO.LOW)
        GPIO.output(self.RPWM_Output, GPIO.HIGH)
        GPIO.output(self.LPWM_Output, GPIO.LOW)
        self.add_widget(self.verify_az)
        #### rotate the slew drive
        GPIO.output(33, GPIO.HIGH)
        GPIO.output(35, GPIO.HIGH)
        GPIO.output(self.rotate_left, GPIO.LOW)
        GPIO.output(self.rotate_right, GPIO.HIGH)
        
    def calibrated(self,event):
        self.movingStatus.text = "CALIBRATED"
        self.remove_widget(self.verif_az)
        #### stop the slew drive
        GPIO.output(33, GPIO.LOW)
        GPIO.output(35, GPIO.LOW)
        GPIO.output(self.rotate_left, GPIO.LOW)
        GPIO.output(self.rotate_right, GPIO.LOW)
        self.elevationControl.disabled = False
        self.azimuthControl.disabled = False
        self.execute.disabled = False
        self.calibrate.disabled = False
        self.inc_elev.disabled = False
        self.dec_elev.disabled = False
        self.inc_az.disabled = False
        self.dec_az.disabled = False
        ### set the new values
        self.elevation = 72
        self.elevation = round(self.elevation, 2)
        self.elevationControl.value = self.elevation
        self.azimuth = 90
        self.azimuth = round(self.azimuth, 2)
        self.azimuthControl.value = self.azimuth
    
    # various functions for the buttons

    def on_elev_slider(self, instance, val):
        self.movingStatus.text = "SET"
        self.elevation = val
        self.elevation_label.text = format(self.elevation, ".2f")

    def on_az_slider(self, instance, val):
        self.movingStatus.text = "SET"
        self.azimuth = val
        self.azimuth_label.text = format(self.azimuth, ".2f")

    def decAz(self,event):
        self.oldAzimuth = self.azimuth
        self.movingStatus.text = "ROTATING"
        self.azimuth = self.azimuth - .05
        self.azimuth = round(self.azimuth, 2)
        if self.azimuth < 0:
            self.azimuth = 0
        self.azimuthControl.value = self.azimuth
        ### Calculate the difference
       
        #### rotate the dish by applying the difference
        GPIO.output(33, GPIO.HIGH)
        GPIO.output(35, GPIO.HIGH)
        GPIO.output(self.rotate_left, GPIO.LOW)
        GPIO.output(self.rotate_right, GPIO.HIGH)
        self.azimuth_label.text = format(self.azimuth, ".2f")
        self.movingStatus.text = "SET"
    
    def decElev(self,event):
        self.movingStatus.text = "LOWERING"
        self.elevation = self.elevation - .05
        self.elevation = round(self.elevation, 2)
        if self.elevation < 0:
            self.elevation = 0
        self.elevationControl.value = self.elevation
        GPIO.output(15, GPIO.HIGH)
        GPIO.output(16, GPIO.HIGH)
        #### extend the linear actuator
        GPIO.output(self.RPWM_Output, GPIO.LOW)
        GPIO.output(self.LPWM_Output, GPIO.HIGH)
        self.elevation_label.text = format(self.elevation, ".2f")
        self.movingStatus.text = "SET"
    
    def incAz(self,event):
        self.movingStatus.text = "ROTATING"
        self.azimuth = self.azimuth + .05
        self.azimuth = round(self.azimuth, 2)
        if self.azimuth > 180:
            self.azimuth = 180
        self.azimuthControl.value = self.azimuth
        GPIO.output(33, GPIO.HIGH)
        GPIO.output(35, GPIO.HIGH)
        #### rotate the slew drive
        GPIO.output(self.rotate_left, GPIO.HIGH)
        GPIO.output(self.rotate_right, GPIO.LOW)
        self.azimuth_label.text = format(self.azimuth, ".2f")
        self.movingStatus.text = "SET"
    
    def incElev(self,event):
        self.movingStatus.text = "RAISING"
        self.elevation = self.elevation + .05
        self.elevation = round(self.elevation, 2)
        if self.elevation > 72:
            self.elevation = 72
        self.elevationControl.value = self.elevation
        GPIO.output(33, GPIO.HIGH)
        GPIO.output(35, GPIO.HIGH)
        #### retract the linear actuator
        GPIO.output(self.RPWM_Output, GPIO.HIGH)
        GPIO.output(self.LPWM_Output, GPIO.LOW)
        self.elevation_label.text = format(self.elevation, ".2f")
        self.movingStatus.text = "SET"
        
    def moveDish(self,event):
        self.movingStatus.text = "MOVING"
        GPIO.output(self.rotate_left, GPIO.LOW)
        GPIO.output(self.rotate_right, GPIO.LOW)
        GPIO.output(self.RPWM_Output, GPIO.LOW)
        GPIO.output(self.LPWM_Output, GPIO.LOW)
        #### make any changes to elevation or azimuth

    def exitProgram(self,event):
        GPIO.cleanup()
        Window.close()

class DishApp(App):
    def build(self):
        return DishLayout()
if __name__=="__main__":
     DishApp().run()
