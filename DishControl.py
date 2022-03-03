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
# GPIO.setmode(GPIO.BOARD)

# # Set pin 11 as an output, and set servo1 as pin 11 as PWM
# GPIO.setup(11,GPIO.OUT)
# servo1 = GPIO.PWM(11,50) # Note 11 is pin, 50 = 50Hz pulse

# #start PWM running, but with value of 0 (pulse off)
# servo1.start(0)
# print ("Waiting for 2 seconds")
# time.sleep(2)

Window.clearcolor = (0.5,0.5,0.6,0.6)

class DishLayout(FloatLayout):
    elevation = 45.0
    azimuth = 90.0

    def __init__(self,**kwargs):
        super(DishLayout,self).__init__(**kwargs)

        self.elevation_label = Label(text = format(self.elevation, ".2f"), size_hint=(.1, .15),pos_hint={'x':.35, 'y':.65})
        self.azimuth_label = Label(text = format(self.azimuth, ".2f"), size_hint=(.1, .15),pos_hint={'x':.35, 'y':.26})
        self.movingStatus = Label(text = "Dish: SET", size_hint=(.1, .1), pos_hint={'x':.7,'y':.32})

        # sliders
        self.elevationControl = Slider(min = 0, max = 90, size_hint=(.43, .1), pos_hint={'x':.18,'y':.58}, value = self.elevation, step = 1, cursor_size = ("80sp", "80sp"))
        self.elevationControl.fbind('value', self.on_elev_slider)
        self.add_widget(self.elevationControl)
        self.azimuthControl = Slider(min = 0, max = 180, size_hint=(.43, .1), pos_hint={'x':.18,'y':.18}, value = self.azimuth, step = 1, cursor_size = ("80sp", "80sp"))
        self.azimuthControl.fbind('value', self.on_az_slider)
        self.add_widget(self.azimuthControl)

    #Main Buttons
        self.inc_elev = Button(text = "+", size_hint=(.1, .1), pos_hint={'x':.47, 'y':.68}, on_release = self.incElev, background_color = (0.5,0.7,0.8,1))
        self.dec_elev = Button(text = "-", size_hint=(.1, .1),pos_hint={'x':.23, 'y':.68}, on_release = self.decElev, background_color = (0.5,0.7,0.8,1))
        self.inc_az = Button(text = "+", size_hint=(.1, .1),pos_hint={'x':.47, 'y':.28}, on_release = self.incAz, background_color = (0.5,0.7,0.8,1))
        self.dec_az = Button(text = "-", size_hint=(.1, .1),pos_hint={'x':.23, 'y':.28}, on_release = self.decAz, background_color = (0.5,0.7,0.8,1))
        self.execute = Button(text = "GO", size_hint = (.1,.25), pos_hint={'x':.7,'y':.4}, on_release = self.moveDish, background_color = (0,0.8,0.4,1))
    
    # labels
        self.elev_text = Label(text = "Elevation", size_hint=(.1,.1), pos_hint={'x':.35,'y':.79}, color = (0,0,0,1))
        self.elev_text.font_size = '130dp'
        self.az_text = Label(text = "Azimuth", size_hint=(.1,.1), pos_hint={'x':.36,'y':.39}, color = (0,0,0,1))
        self.az_text.font_size = '130dp'

        self.elevation_label.font_size = '80dp'
        self.azimuth_label.font_size = '80dp'
        self.inc_elev.font_size = '60dp'
        self.dec_elev.font_size = '100dp'
        self.inc_az.font_size = '60dp'
        self.dec_az.font_size = '100dp'
        self.execute.font_size = '40dp'
        self.movingStatus.font_size = '40dp'

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

    def on_elev_slider(self, instance, val):
        self.movingStatus.text = "Dish: SET"
        self.elevation = val
        self.elevation_label.text = format(self.elevation, ".2f")

    def on_az_slider(self, instance, val):
        self.movingStatus.text = "Dish: SET"
        self.azimuth = val
        self.azimuth_label.text = format(self.azimuth, ".2f")

    def decAz(self,event):
        self.movingStatus.text = "Dish: SET"
        self.azimuth = self.azimuth - .05
        self.azimuth = round(self.azimuth, 2)
        if self.azimuth < 0:
            self.azimuth = 0
        self.azimuth_label.text = format(self.azimuth, ".2f")
    
    def decElev(self,event):
        self.movingStatus.text = "Dish: SET"
        self.elevation = self.elevation - .05
        self.elevation = round(self.elevation, 2)
        if self.elevation < 0:
            self.elevation = 0
        self.elevation_label.text = format(self.elevation, ".2f")
    
    def incAz(self,event):
        self.movingStatus.text = "Dish: SET"
        self.azimuth = self.azimuth + .05
        self.azimuth = round(self.azimuth, 2)
        if self.azimuth > 180:
            self.azimuth = 180
        self.azimuth_label.text = format(self.azimuth, ".2f")
    
    def incElev(self,event):
        self.movingStatus.text = "Dish: SET"
        self.elevation = self.elevation + .05
        self.elevation = round(self.elevation, 2)
        if self.elevation > 90:
            self.elevation = 90
        self.elevation_label.text = format(self.elevation, ".2f")
        
    def moveDish(self,event):
        self.movingStatus.text = "Dish: MOVING"
        # angle = float(self.azimuth)
        # servo1.ChangeDutyCycle(2.9+(angle/17))
        # time.sleep(1)
        # servo1.ChangeDutyCycle(0)
        # self.movingStatus.text = "Dish: SET"

class DishApp(App):
    def build(self):
        return DishLayout()
if __name__=="__main__":
     DishApp().run()