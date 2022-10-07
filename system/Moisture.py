from Device import Device

class Moisture(Device):
    lastMoisture = 0
    patchId = None

    def __init__(self, comDir):
        Device.__init__(self, comDir, "moisture", self.receiver)
        self.init()

    def init(self):
        self.sendCommand("INIT")

    def getMoisture(self):
        self.sendCommand("MOIST")


    def receiver(self, data):
        if data[0] == "MOIST":
            self.lastMoisture = float(data[1])

        if data[0] == "IDENT":
            self.patchId = data[1]
            