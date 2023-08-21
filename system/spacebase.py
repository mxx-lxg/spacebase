from Irrigation import Irrigation
from Windows import Windows
from Environment import Environment
from Moisture import Moisture
from DeviceScanner import DeviceScanner
from DataLogger import DataLogger
import logging
import os
import configparser
import time
import datetime
import keyboard
import sys
from os.path import exists
from MqttClient import MqttClient
from Dashboard import Dashboard
from RelayController import Heater, Pump
import schedule


#log setup
# set up logging to file
print("working directory: " + os.getcwd())
logging.basicConfig(
    filename= os.getcwd() + '/spacebase.log',
    level=logging.INFO, 
    format= '[%(asctime)s] %(name)s: %(levelname)s - %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S'
)
# set up logging to console
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
# set a format which is simpler for console use
formatter = logging.Formatter('[%(asctime)s] %(name)s: %(levelname)s %(message)s')
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)
logger = logging.getLogger(__name__)

logger.info("startup")

#monitoring pipe
#TODO piping in einem Datenformat für externes Dashboard programm
PIPE_PATH = "/tmp/greenhouse_pipe"
if not os.path.exists(PIPE_PATH):
    os.mkfifo(PIPE_PATH)

#Konfiguartion laden oder erstellen

if not exists(os.getcwd() + '/spacebase.conf'):
    print("No config file found. Writing new config and exiting...")
    
    newConfig = configparser.ConfigParser()
    newConfig.add_section('windows')
    newConfig.set('windows', 'stage_1', '22')
    newConfig.set('windows', 'stage_2', '24')
    newConfig.set('windows', 'stage_3', '26')
    newConfig.set('windows', 'stage_4', '28')
    newConfig.set('windows', 'check_interval', '300')
    newConfig.add_section('climate')
    newConfig.set('climate', 'log_interval', '300')
    newConfig.set('climate', 'heater_threshold', '1')
    newConfig.set('climate', 'heater_stop', '3')
    newConfig.add_section('irrigation')
    newConfig.set('irrigation', 'left_threshold', '15')
    newConfig.set('irrigation', 'right_threshold', '15')
    newConfig.add_section('mqtt')
    newConfig.set('mqtt', 'broker', 'smart.home')
    newConfig.set('mqtt', 'port', '1883')
    newConfig.set('mqtt', 'client_id', '69420')
    newConfig.set('mqtt', 'user', 'max')
    newConfig.set('mqtt', 'pw', 'public')
    with open(os.getcwd() + '/spacebase.conf', 'x') as configFile:
        newConfig.write(configFile)
        configFile.close()
        sys.exit()


print("loading config")
config = configparser.ConfigParser()
config.read(os.getcwd() + '/spacebase.conf')
heaterStartVal = float(config['climate']['heater_threshold'])
heaterStopVal = float(config['climate']['heater_stop'])

irrigationVal = float(config['irrigation']['left_threshold'])

stage1 = float(config['windows']['stage_1'])    #TODO in objekt
stage2 = float(config['windows']['stage_2'])
stage3 = float(config['windows']['stage_3'])
stage4 = float(config['windows']['stage_4'])

#MQTT Client
mqttClient = MqttClient(config['mqtt'])



#Logger
print("initialising data logs")
dataLogger = DataLogger(mqttClient)

#GPIO
heater = Heater()
pump = Pump()

#keypresses
print("keyboard setup")
keyboard.add_hotkey('1', lambda: windows.forceClosed())
keyboard.add_hotkey('2', lambda: windows.forceOpened())
keyboard.add_hotkey('3', lambda: windows.unforce())
keyboard.add_hotkey('4', lambda: windows.reset())
keyboard.add_hotkey('7', lambda: heater.heaterToggle())
keyboard.add_hotkey('8', lambda: pump.pumpToggle())
#keyboard.add_hotkey('8', lambda: heater.heaterOn())
#keyboard.add_hotkey('9', lambda: heater.heaterOff())

#Geräte suchen und initialisieren
scannedDevices = DeviceScanner.findDevices()
windows = None
environment = None
irrigation = None
moisture = [] 

#UI
#dashboard = Dashboard()

print("device init")
for path in scannedDevices:
    device = scannedDevices[path]
    if device == "windows":
        windows = Windows(path, mqttClient)
    if device == "environment":
        environment = Environment(path)
        environment.init()
    if device == "water":
        irrigation = Irrigation(path)
        irrigation.init()
    if device == "moisture":
        moisture.append(Moisture(path))
        moisture[-1].init()

#Sonnenauf- und untergang
sunrise = 0
sunset = 0

#startup end
logger.info("startup complete")


#system summary
print("\n********* system summary *********")
if windows:
    print("* window actuators")
if environment:
    print("* environmental sensor-package")
if irrigation:
    print("* irrigation and water management")
if moisture:
    print("* soil-moisture sensors:")
    for patch in moisture:
        print("    " + patch.patchId)


#config info
print("\n********* Configuration *********")
print("\n* Heater")
print("   Start: " + str(heaterStartVal) + "°C | Stop: " + str(heaterStopVal) + "°C")
print("\n* Windows")
print("   check interval (s): " + config['windows']['check_interval'])
print("   thresholds")
print("   1: " + str(stage1) + "°C | 2: " + str(stage2) + "°C | 3: " + str(stage3) + "°C | 4: " + str(stage4) + "°C")

print("\n getting down to business...")

if mqttClient: mqttClient.publish("STATE", "hello")


#main Loop
heatingInProgress = False

def environmentReport():
    #Klimadaten speichern
    global environment
    global dataLogger
    print("{0} | temperature: {1} °C | humidity: {2} % - logged \r".format(
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        environment.lastTemperature,
        environment.lastHumidity
    ))
    dataLogger.logEnvironment(environment.lastTemperature, environment.lastHumidity)

def irrigationReport():
    global irrigation
    global dataLogger
    print("{0} | rainwater level: {1} % - logged \r".format(
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        irrigation.rainWaterLevel
    ))
    dataLogger.logIrrigation(irrigation.rainWaterLevel)

def irrigateAll():
    global irrigation
    global pump

    irrigation.getRainWaterLevel()
    time.sleep(1)
    if irrigation.rainWaterLevel > 30:
        startLevel = irrigation.rainWaterLevel
        print("starting irrigation...")
        pump.pumpOn()
        while irrigation.rainWaterLevel >= startLevel - 10: #TODO config value  
            irrigation.getRainWaterLevel()
            time.sleep(1)
            print(".")
        pump.pumpOff()
        print("irrigation complete")
    print("not enough water!")

def moistureReport():
    #Bodenfeuchtigkeit speichern
    for patch in moisture:
        print("{0} | patch {1} moisture: {2} % - logged \r".format(
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            patch.patchId,
            patch.lastMoisture
        ))
    #TODO moisture logging
    #Bewässerung
    #1 mal morgens
        #Bewässerung unabhängig von Feuchtigkeit
    #2 mal täglich
        #Liste der beete durchgehen und für jedes Moisture Sensor abfragen
        #Wenn unter Grenze Bewässerung aktivieren

def adjustWindows():
    #Fenster einstellen
    global environment
    global windows
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

def frostProtection():
    #Frostschutz Heizung
    global heatingInProgress
    global heaterStartVal
    global heater
    global logger
    global environment
    if not heatingInProgress:
        if environment.lastTemperature <= heaterStartVal: 
            heater.heaterOn()
            heatingInProgress = True
            logger.warning("below frost threshold: " + str(environment.lastTemperature))
            print("starting defrost")
    else: 
        if environment.lastTemperature >= heaterStopVal: 
            heater.heaterOff()
            heatingInProgress = False
            print("stopping defrost")



#Jobs anlegen
if environment:
    schedule.every(int(config['climate']['log_interval'])).seconds.do(environmentReport)
    schedule.every(1).seconds.do(frostProtection)

if irrigation:
    irrigation.getRainWaterLevel()
    schedule.every(int(config['climate']['log_interval'])).seconds.do(irrigationReport)
    schedule.every().day.at("8:30:00").do(irrigateAll)

if moisture:
    schedule.every(int(config['climate']['log_interval'])).seconds.do(moistureReport)

if windows:
    windows.reset()
    schedule.every(int(config['windows']['check_interval'])).seconds.do(adjustWindows)


while True:
    schedule.run_pending()
    time.sleep(1)
