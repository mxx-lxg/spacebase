import datetime
from tinydb import TinyDB, Query


#databases and logging handler
class DataLogger():
    atmosLog = None
    def __init__(self):
        self.atmosLog = TinyDB('/home/pi/greenhouse/atmos_db.json')

    #log temperature and humidity
    def logEnvironment(self, temp, hum):
        self.atmosLog.insert({
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'temp': temp, 
            'hum': hum
        })