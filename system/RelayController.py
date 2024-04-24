import RPi.GPIO as GPIO
import logging

heaterPin = 5
pumpPin = 6
GPIO.setmode(GPIO.BCM)
GPIO.setup(heaterPin, GPIO.OUT)
GPIO.output(heaterPin, GPIO.HIGH)
GPIO.setup(pumpPin, GPIO.OUT)
GPIO.output(pumpPin, GPIO.HIGH)

#verallgemeinern, in Switch oder sowas umbennen
class Heater():
    state = False
    logger = logging.getLogger(__name__)
    mqttClient = None

    def __init__(self, mqttClient):
        self.mqttClient = mqttClient

    def heaterOn(self):
        GPIO.output(heaterPin, GPIO.LOW)
        self.state = True
        self.mqttClient.logHeater(True)
        self.logger.info("heater on")

    def heaterOff(self):
        GPIO.output(heaterPin, GPIO.HIGH)
        self.state = False
        self.mqttClient.logHeater(False)
        self.logger.info("heater off")

    def heaterToggle(self):
        if self.state == True:
            self.heaterOff()
        else:
            self.heaterOn()

class Pump():
    state = False
    logger = logging.getLogger(__name__)
    mqttClient = None

    def __init__(self, mqttClient):
        self.mqttClient = mqttClient

    def pumpOn(self):
        GPIO.output(pumpPin, GPIO.LOW)
        self.state = True
        self.mqttClient.logPump(True)
        self.logger.info("pump on")

    def pumpOff(self):
        GPIO.output(pumpPin, GPIO.HIGH)
        self.state = False
        self.mqttClient.logPump(False)
        self.logger.info("pump off")

    def pumpToggle(self):
        if self.state == True:
            self.pumpOff()
        else:
            self.pumpOn()

