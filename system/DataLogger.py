import datetime
from tinydb import TinyDB, Query
import json

#databases and logging handler
class DataLogger():
    atmosLog = None
    mqttClient = None
    def __init__(self, mqttClient=None):
        self.atmosLog = TinyDB('/home/pi/greenhouse/atmos_db.json')
        self.mqttClient = mqttClient

    #log temperature and humidity
    def logEnvironment(self, temp, hum):

        log = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "temp": temp, 
            "hum": hum
        }

        self.atmosLog.insert(log)
        if self.mqttClient: self.mqttClient.publish( "SENSORS", json.dumps(log))