import configparser
import datetime
import logging
import os
import sys
import threading
import time
from os.path import exists

import keyboard
import schedule
from alive_progress import alive_bar
from Dashboard import Dashboard
from DataLogger import DataLogger
from DeviceScanner import DeviceScanner
from Environment import Environment
from Irrigation import Irrigation
from Moisture import Moisture
from MqttClient import MqttClient
from RelayController import Heater, Pump
from Windows import Windows

#hiberantion for general winter idle
hibernationMode = False

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


print("\n getting down to business...")

if mqttClient: mqttClient.publish("STATE", "hello")


#main Loop
heatingInProgress = False

def listCommands():
    print("help................help")
    print("status..............system status")
    print("water...............run irrigation cycle")
    print("wreset..............reset windows")
    print("wset [stage]........set windows")
    print("listjobs............list scheduled jobs")
    print("hibernate [on/off]..activate hibernation")

#system status
def systemStatus():
    global windows
    global environment
    global irrigation
    global moisture
    global mqttClient
    global hibernationMode
    global heaterStartVal
    global heaterStopVal
    global config
    global stage1
    global stage2
    global stage3
    global stage4

    #devices
    print("\n********* devices *********")
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

    # system info
    print("\n********* system *********")
    if mqttClient.connected:
        print("* connected to MQTT broker")
    else: 
        print("! not connected to MQTT broker")
    if hibernationMode:
        print("! hibernation mode is ON")
    else:
        print("* hibernation mode is OFF")


    #config info
    print("\n********* configuration *********")
    print("\n* Heater")
    print("   Start: " + str(heaterStartVal) + "°C | Stop: " + str(heaterStopVal) + "°C")
    print("\n* Windows")
    print("   check interval (s): " + config['windows']['check_interval'])
    print("   thresholds")
    print("   1: " + str(stage1) + "°C | 2: " + str(stage2) + "°C | 3: " + str(stage3) + "°C | 4: " + str(stage4) + "°C")



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
    irrigation.getRainWaterLevel()
    time.sleep(1)
    print("{0} | rainwater level: {1} % - logged \r".format(
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        irrigation.rainWaterLevel
    ))
    dataLogger.logIrrigation(irrigation.rainWaterLevel)

def irrigateAll():
    global irrigation
    global pump
    global hibernationMode

    irrigation.getRainWaterLevel()
    time.sleep(1)
    if irrigation.rainWaterLevel > 30 and not hibernationMode:
        startLevel = irrigation.rainWaterLevel
        failSafeCounter = 400
        amount = 10
        print("starting irrigation...")
        pump.pumpOn()

        with alive_bar(manual=True, stats=False, title="water level") as bar:
            for tick in range(failSafeCounter):
                irrigation.getRainWaterLevel()
                time.sleep(1)
                failSafeCounter = failSafeCounter - 1
                bar(irrigation.rainWaterLevel / 100)
                if irrigation.rainWaterLevel <= startLevel - amount:
                    break

        pump.pumpOff()
        print("irrigation complete ({0})".format(failSafeCounter))
    else:
        
        print("not enough water! ({0})".format(irrigation.rainWaterLevel))

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


#frost protection
def frostProtection():
    #Frostschutz Heizung
    global heatingInProgress
    global heaterStartVal
    global heater
    global logger
    global environment
    global hibernationMode

    if not hibernationMode:
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
    schedule.every().day.at("11:30").do(irrigateAll)

if moisture:
    schedule.every(int(config['climate']['log_interval'])).seconds.do(moistureReport)

if windows:
    schedule.every(int(config['windows']['check_interval'])).seconds.do(adjustWindows)


#terminal commands
def commandHandlerLoop():
    global windows
    global hibernationMode
    global schedule


    while True:
        inputString = input('>')

        args = inputString.split(' ')
        command = args[0]

        if command == "help":
            listCommands()
        if command == "status":
            systemStatus()
        if command == "water":
            irrigateAll()
        if command == "wreset":
            windows.reset()
        
        if command == "wset":
            windows.setToStage(int(args[1]))
        if command == "hibernate":

            if args[1] == "on":
                hibernationMode == True
                print("hibernation mode activated ({0})".format(hibernationMode))
            elif args[1] == "off":
                hibernationMode == False
                print("hibernation mode deactivated ({0})".format(hibernationMode))

        if command == "listjobs":
            jobs = schedule.get_jobs()
            print("active jobs")
            print(*jobs, sep = "\n")



commandHandler = threading.Thread(target=commandHandlerLoop, args=())
commandHandler.start()


#main job loop
while True:
    schedule.run_pending()
    time.sleep(1)
