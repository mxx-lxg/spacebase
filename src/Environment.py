from Device import Device

class Environment(Device):
    lastTemperature = 10
    lastHumidity = 10

    def __init__(self, comDir):
        Device.__init__(self, comDir, "environment", self.receiver)
        self.init()

    def init(self):
        self.sendCommand("INIT")

    def getAtmospherics(self):
        self.sendCommand("ATMOS")


    def receiver(self, data):
        if 2 < len(data): data[2] = float(data[2]) # value spalte zu float konvertieren

        if data[1] == "TEMP":
            self.lastTemperature = data[2]
        
        if data[1] == "HUM":
            self.lastHumidity = data[2]
            