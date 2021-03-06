from Windows import Windows
from Environment import Environment
from DeviceScanner import DeviceScanner
from DataLogger import DataLogger
import logging
import os
import configparser
import time
import datetime
import keyboard
from Dashboard import Dashboard
from RelayController import Heater

#log setup
# set up logging to file
print("working directory: " + os.getcwd())
logging.basicConfig(
     filename='./spacebase.log',
     level=logging.INFO, 
     format= '[%(asctime)s] %(name)s: %(levelname)s - %(message)s',
     datefmt='%d.%m.%Y %H:%M:%S'
 )
# set up logging to console
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# set a format which is simpler for console use
formatter = logging.Formatter('[%(asctime)s] %(name)s: %(levelname)s %(message)s')
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)
logger = logging.getLogger(__name__)



#monitoring pipe
#TODO piping in einem Datenformat für externes Dashboard programm
PIPE_PATH = "/tmp/greenhouse_pipe"
if not os.path.exists(PIPE_PATH):
    os.mkfifo(PIPE_PATH)

#Konfiguartion laden
print("loading config")
config = configparser.ConfigParser()
config.read('/home/pi/spacebase/system/spacebase.conf')
heaterStartVal = float(config['climate']['heater_threshold'])
heaterStopVal = float(config['climate']['heater_stop'])
stage1 = float(config['windows']['stage_1'])    #TODO in objekt
stage2 = float(config['windows']['stage_2'])
stage3 = float(config['windows']['stage_3'])
stage4 = float(config['windows']['stage_4'])

#Logger
print("initialising data logs")
dataLogger = DataLogger()

#GPIO
heater = Heater()

#keypresses
print("keyboard setup")
keyboard.add_hotkey('1', lambda: windows.forceClosed())
keyboard.add_hotkey('2', lambda: windows.forceOpened())
keyboard.add_hotkey('3', lambda: windows.unforce())
keyboard.add_hotkey('4', lambda: windows.reset())
keyboard.add_hotkey('7', lambda: heater.heaterToggle())
#keyboard.add_hotkey('8', lambda: heater.heaterOn())
#keyboard.add_hotkey('9', lambda: heater.heaterOff())

#Geräte suchen und initialisieren
scannedDevices = DeviceScanner.findDevices()
windows = None
environment = None

#UI
#dashboard = Dashboard()

print("device init")
for path in scannedDevices:
    device = scannedDevices[path]
    if device == "windows":
        windows = Windows(path)
        windows.reset()
    if device == "environment":
        environment = Environment(path)
        environment.init()

#Sonnenauf- und untergang
sunrise = 0
sunset = 0

#startup end
logger.info("startup complete")

#config info
print("\n********* Configuration *********")
print("\n* Heater")
print("   Start: " + str(heaterStartVal) + "°C | Stop: " + str(heaterStopVal) + "°C")
print("\n* Windows")
print("   check interval (s): " + config['windows']['check_interval'])
print("   thresholds")
print("   1: " + str(stage1) + "°C | 2: " + str(stage2) + "°C | 3: " + str(stage3) + "°C | 4: " + str(stage4) + "°C")


#main Loop
lastWindowCheck = int(time.time())
lastClimateUpdate = int(time.time())
lastPass = int(time.time())
heatingInProgress = False

while True:
    currentPass = int(time.time())
    windowInterval = int(config['windows']['check_interval'])
    climateLogInterval = int(config['climate']['log_interval'])

    #Klima (aus Window Klasse abspalten)
    if windows and environment and currentPass >= lastClimateUpdate + climateLogInterval:
        #Klimadaten speichern
        print("{0} | Temperature: {1} °C | Humidity: {2} % - logged \r".format(
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            environment.lastTemperature,
            environment.lastHumidity
        ))

        dataLogger.logEnvironment(environment.lastTemperature, environment.lastHumidity)
        lastClimateUpdate = currentPass

    #Fenster
    if windows and environment and currentPass >= lastWindowCheck + windowInterval:
        
        if environment.lastTemperature >= stage4: 
            windows.setToStage(4)
        elif environment.lastTemperature >= stage3: 
            windows.setToStage(3)
        elif environment.lastTemperature >= stage2: 
            windows.setToStage(2)
        elif environment.lastTemperature >= stage1: 
            windows.setToStage(1)
        else:
            windows.setToStage(0)
    
        lastWindowCheck = currentPass
    
    #Sekundentakt
    if currentPass >= lastPass + 1 and environment:
        #Sensordaten holen
        environment.getAtmospherics()

        #Dashboard aktualisieren
        dashboard.set(environment.lastTemperature, environment.lastHumidity, windows.currentStage)

        #Frostschutz Heizung
        if not heatingInProgress:
            if environment.lastTemperature <= heaterStartVal: 
                heater.heaterOn()
                heatingInProgress = True
                logger.warning("below frost threshold")
                print("start heating up")
        else: 
            if environment.lastTemperature >= heaterStopVal: 
                heater.heaterOff()
                heatingInProgress = False
                print("stop heating up")



        #Monitor Pipe
        #moveIllustration = ""
        #for i in range(4):
        #    if i+1 == windows.moving:
        #        moveIllustration = moveIllustration + "▄"
        #    elif i+1 <= windows.currentStage:
        #        moveIllustration = moveIllustration + "█"
        #    else:
        #        moveIllustration = moveIllustration + "-"
    
        #with open(PIPE_PATH, "w") as p:
        #    p.write("{0} | Temperatur: {1} °C | Humidity: {2} % | {3} \r".format(
        #        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        #        windows.lastTemperature,
        #        windows.lastHumidity,
        #        moveIllustration
        #    ))
        lastPass = currentPass