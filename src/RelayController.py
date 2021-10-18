import RPi.GPIO as GPIO
import logging

heaterPin = 5
GPIO.setmode(GPIO.BCM)
GPIO.setup(heaterPin, GPIO.OUT)
GPIO.output(heaterPin, GPIO.HIGH)

#verallgemeinern, in Switch oder sowas umbennen
class Heater():
    __state = False
    logger = logging.getLogger(__name__)

    def heaterOn(self):
        GPIO.output(heaterPin, GPIO.LOW)
        self.__state = True
        self.logger.info("heater on")

    def heaterOff(self):
        GPIO.output(heaterPin, GPIO.HIGH)
        self.__state = False
        self.logger.info("heater off")

    def heaterToggle(self):
        if self.__state == True:
            self.heaterOff()
        else:
            self.heaterOn()

