from Windows import Windows
from DeviceScanner import DeviceScanner
import os
import configparser
import time
from tinydb import TinyDB, Query
import datetime

#monitoring pipe
#TODO piping in einem Datenformat für externes Dashboard programm
PIPE_PATH = "/tmp/greenhouse_pipe"
if not os.path.exists(PIPE_PATH):
    os.mkfifo(PIPE_PATH)

#Geräte suchen und initialisieren
scannedDevices = DeviceScanner.findDevices()
windows = None

for path in scannedDevices:
    device = scannedDevices[path]
    if device == "windows":
        windows = Windows(path)
        windows.reset()

#Konfiguartion laden
config = configparser.ConfigParser()
config.read('spacebase.conf')

#DB
atmosDb = TinyDB('atmos_db.json')

#Sonnenauf- und untergang
sunrise = 0
sunset = 0

#main Loop
lastWindowCheck = int(time.time())
lastClimateUpdate = int(time.time())
lastPass = int(time.time())
while True:
    currentPass = int(time.time())
    windowInterval = int(config['windows']['check_interval'])
    climateLogInterval = int(config['climate']['log_interval'])

    #Klima (aus Window Klasse abspalten)
    if windows and currentPass >= lastClimateUpdate + climateLogInterval:
        #Klimadaten speichern
        print("{0} | Temperatur: {1} °C | Humidity: {2} %".format(
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            windows.lastTemperature,
            windows.lastHumidity
        ))

        atmosDb.insert({
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'temp': windows.lastTemperature, 
            'hum': windows.lastHumidity
        })
        lastClimateUpdate = currentPass

    #Fenster
    if windows and currentPass >= lastWindowCheck + windowInterval:

        #Fenster Positionen
        stage1 = float(config['windows']['stage_1'])
        stage2 = float(config['windows']['stage_2'])
        stage3 = float(config['windows']['stage_3'])
        stage4 = float(config['windows']['stage_4'])
        
        if windows.lastTemperature >= stage4: 
            windows.setToStage(4)
        elif windows.lastTemperature >= stage3: 
            windows.setToStage(3)
        elif windows.lastTemperature >= stage2: 
            windows.setToStage(2)
        elif windows.lastTemperature >= stage1: 
            windows.setToStage(1)
        else:
            windows.setToStage(0)
    
        lastWindowCheck = currentPass
    
    #Sekundentakt
    if currentPass >= lastPass + 1 and windows:
        #Monitor Pipe
        moveIllustration = ""
        for i in range(4):
            if i+1 == windows.moving:
                moveIllustration = moveIllustration + "▄"
            elif i+1 <= windows.currentStage:
                moveIllustration = moveIllustration + "█"
            else:
                moveIllustration = moveIllustration + "-"
        with open(PIPE_PATH, "w") as p:
            p.write("{0} | Temperatur: {1} °C | Humidity: {2} % | {3} \r".format(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                windows.lastTemperature,
                windows.lastHumidity,
                moveIllustration
            ))
        lastPass = currentPass