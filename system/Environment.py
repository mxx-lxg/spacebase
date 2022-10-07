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
        if 1 < len(data): data[1] = float(data[1]) # value spalte zu float konvertieren

        if data[0] == "TEMP":
            self.lastTemperature = data[1]
        
        if data[0] == "HUM":
            self.lastHumidity = data[1]
            