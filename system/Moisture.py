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
        if data[1] == "MOIST":
            self.lastMoisture = float(data[2])

        if data[1] == "IDENT":
            self.patchId = data[2]
            