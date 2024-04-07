import logging
import schedule
import time
import datetime
import keyboard

from RelayController import Heater, Pump
from DeviceScanner import DeviceScanner
from Windows import Windows
from Irrigation import Irrigation
from Environment import Environment
from Moisture import Moisture
from MqttClient import MqttClient

class Habitat():
    hibernation_mode = False
    heating_in_progress = False
    logger = logging.getLogger(__name__)
    config  = None
    heaterStartVal = 0
    heaterStopVal = 2
    irrigationVal = 20
    mqttClient = None

    heater = Heater()
    pump = Pump()
    windows = None
    irrigation = None
    environment = None
    moisture = [] 

    def __init__(self, config):
        print("new spacebase")
        self.config = config
                
        self.heaterStartVal = float(config['climate']['heater_threshold'])
        self.heaterStopVal = float(config['climate']['heater_stop'])
        self.irrigationVal = float(config['irrigation']['left_threshold'])

        #MQTT Client
        self.mqttClient = MqttClient(config['mqtt'])

        self.initialize_devices()
        self.create_jobs()


    def initialize_devices(self):
        #Geräte suchen und initialisieren
        scannedDevices = DeviceScanner.findDevices()

        print("device init")
        for path in scannedDevices:
            device = scannedDevices[path]
            if device == "windows":
                self.windows = Windows(path, self.mqttClient)
            if device == "environment":
                self.environment = Environment(path)
                self.environment.init()
            if device == "water":
                self.irrigation = Irrigation(path)
                self.irrigation.init()
            if device == "moisture":
                self.moisture.append(Moisture(path))
                self.moisture[-1].init()

    def create_jobs(self):
        #Jobs anlegen
        if self.environment:
            schedule.every(int(self.config['climate']['log_interval'])).seconds.do(self.environmentReport)
            schedule.every(1).seconds.do(self.frostProtection)

        if self.irrigation:
            self.irrigation.getRainWaterLevel()
            schedule.every(int(self.config['climate']['log_interval'])).seconds.do(self.irrigationReport)
            schedule.every().day.at("11:30").do(self.irrigateAll)

        if self.moisture:
            schedule.every(int(self.config['climate']['log_interval'])).seconds.do(self.moistureReport)

        if self.windows:
            schedule.every(int(self.config['windows']['check_interval'])).seconds.do(self.adjustWindows)

        
        jobs = schedule.get_jobs()
        print("active jobs")
        print(*jobs, sep = "\n")

    def setup_keayboard(self):
        #keypresses
        print("keyboard setup")
        keyboard.add_hotkey('1', lambda: self.windows.forceClosed())
        keyboard.add_hotkey('2', lambda: self.windows.forceOpened())
        keyboard.add_hotkey('3', lambda: self.windows.unforce())
        keyboard.add_hotkey('4', lambda: self.windows.reset())
        keyboard.add_hotkey('6', lambda: self.toggleHibernation())
        keyboard.add_hotkey('7', lambda: self.heater.heaterToggle())
        keyboard.add_hotkey('8', lambda: self.pump.pumpToggle())
            
        
    def toggleHibernation(self):
        self.hibernation_mode = not self.hibernation_mode
        print("hibernation mode is ({0})".format(self.hibernation_mode))
                
    def environmentReport(self):
        #Klimadaten speichern
        self.mqttClient.logEnvironment(self.environment.lastTemperature, self.environment.lastHumidity)


    def irrigationReport(self):
        self.irrigation.getRainWaterLevel()
        time.sleep(1)
        self.mqttClient.logIrrigation(self.irrigation.rainWaterLevel)

    def moistureReport(self):
    #Bodenfeuchtigkeit speichern
        for patch in self.moisture:
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

    def adjustWindows(self):
        #Fenster einstellen
        if self.environment.lastTemperature >= float(self.config['windows']['stage_4']): 
            self.windows.setToStage(4)
        elif self.environment.lastTemperature >= float(self.config['windows']['stage_3']): 
            self.windows.setToStage(3)
        elif self.environment.lastTemperature >= float(self.config['windows']['stage_2']): 
            self.windows.setToStage(2)
        elif self.environment.lastTemperature >= float(self.config['windows']['stage_1']): 
            self.windows.setToStage(1)
        else:
            self.windows.setToStage(0) 

    def frostProtection(self):
        #Frostschutz Heizung
        if not self.hibernation_mode:
            if not self.heating_in_progress:
                if self.environment.lastTemperature <= self.heaterStartVal: 
                    self.heater.heaterOn()
                    self.heating_in_progress = True
                    self.logger.warning("below frost threshold: " + str(self.environment.lastTemperature))
                    print("starting defrost")
            else: 
                if self.environment.lastTemperature >= self.heaterStopVal: 
                    self.heater.heaterOff()
                    self.heating_in_progress = False
                    print("stopping defrost")

    def irrigateAll(self):
        self.irrigation.getRainWaterLevel()
        time.sleep(1)
        if self.irrigation.rainWaterLevel > 30 and not self.hibernation_mode:
            startLevel = self.irrigation.rainWaterLevel
            failSafeCounter = 400
            amount = 10
            print("starting irrigation...")
            self.pump.pumpOn()

            for tick in range(failSafeCounter):
                self.irrigation.getRainWaterLevel()
                time.sleep(1)
                failSafeCounter = failSafeCounter - 1
                if self.irrigation.rainWaterLevel <= startLevel - amount:
                    break

            self.pump.pumpOff()
            print("irrigation complete ({0})".format(failSafeCounter))
        else:
            
            print("not enough water! ({0})".format(self.irrigation.rainWaterLevel))
    