import RPi.GPIO as gpio
import time
from mfrc522 import SimpleMFRC522
from datetime import datetime


# GPIO-Einstellungen
gpio.setwarnings(False)                                 # Warnungen Ausschalten
gpio.setmode(gpio.BCM)                                  # GPIO Pinlayout auf GPIO Pins setzen


#Klassen
class Servo():
  def __init__(self, pin):
    self.servo_pin = pin
    gpio.setup(self.servo_pin, gpio.OUT)
    self.p = gpio.PWM(self.servo_pin, 50)
    self.s = self.p.start(2.5)
    self.door_open = False
    
  
  def open_door(self):
    self.p.ChangeDutyCycle(10)                          # Max: 120Grad, mehr geht nicht
    self.door_open = True
      

  def close_door(self):
    self.p.ChangeDutyCycle(2.5)                         # Weniger als 0Grad geht nicht
    self.door_open = False 

  def motoraus(self):
    self.p.ChangeDutyCycle(0)

  def start(self):
      if self.s != self.p.start(2.5):
          self.p.ChangeDutyCycle(2.5)
          self.door_open = False
          
          
class NFC():
  def __init__(self):
    self.reader = SimpleMFRC522()
    self.id = 0
    self.text = ""

  def read(self):
    self.id, self.text = self.reader.read()
    return(self.id)

    
class Knopf:
    def __init__(self, pbutton):
        self.knopf = int(pbutton)
        self.pressed = None
        self.state = None
        gpio.setup(self.knopf, gpio.IN)
        
        
    def ppressed(self):
        self.state = gpio.input(self.knopf)
        if self.state == 1:
            self.pressed = True
            return self.pressed
        else:
            self.pressed = False
            return self.pressed

class Text:
    def __init__(self):
        self.datei_name = ('LOG.txt')
        self.now = datetime.now()
        self.date = self.now.strftime("%d.%m.%Y, %H:%M:%S")
        self.name = ("")
        self.Benutzer = [""]
        self.nfc = NFC()
        
        self.id = str(self.nfc.read())

    def ausgabe(self):
        file = open(self.datei_name,'a')
        file.write(self.text+ '\n')

    def einloggen(self):
        self.name = self.id
        if self.name in self.Benutzer:
            self.text = (self.date +(" -- ")+ self.id+" hat sich eingeloggt")
        else:
            self.text = (self.date +(" -- ")+ "Jemand mit den Kartenname "+ self.id +" hat versucht sich unbefugt anzumelden")
    
    def zu(self):
        self.text = (self.date +(" -- ")+ "Schloss wurde durch Knopf geschlossen" )



class Door():
  def __init__(self):
    self.servo = Servo(18)
    self.knopf = Knopf(21)
    self.nfc = NFC()
    self.bool = True
    self.text = Text()
    self.ids = [384576693246, 146234160166]
    self.text.Benutzer = str(self.ids)
  
  def run(self):
    while True:
        
        if self.bool == True:
            self.servo.start()
            time.sleep(2)
            self.servo.motoraus()
            self.nfc.read()
            print(self.nfc.id)
        
        
            if self.nfc.id in self.ids:
                self.text.einloggen()
                self.text.ausgabe()
                
                self.servo.open_door()
                time.sleep(1)
                self.servo.motoraus()
                self.bool = False
            
            else:
                self.servo.motoraus()
                self.text.einloggen()
                self.text.ausgabe()
                self.bool = False
                
            
        else:
            if self.knopf.ppressed() == True:
              self.servo.close_door()
              time.sleep(1)
              self.servo.motoraus()
              self.text.zu()
              self.text.ausgabe()
              self.bool = True
            
              
if __name__ == '__main__':

      door = Door()
      door.run()