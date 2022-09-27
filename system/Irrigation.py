from Device import Device
import logging

class Irrigation(Device):
    bufferRefillInProgress = True
    bufferFull= False
    bufferEmpty= False
    rainWaterLevel = 0
    logger = logging.getLogger(__name__)

    def __init__(self, comDir):
        Device.__init__(self, comDir, "water", self.receiver)
        self.init()

    def init(self):
        self.sendCommand("INIT")
        
    def openValve(self, valveId):
        print("Irrigation On: " + str(valveId), end="\r\n")
        self.sendCommand("OPEN:" + str(valveId))

    def closeValves(self):
        print("Irrigation Off", end="\r\n")
        self.sendCommand("CLOSE")

    def refillBuffer(self):
        print("refilling buffer", end="\r\n")
        self.sendCommand("REFILL")
        self.bufferRefillInProgress=True

    def getRainWaterLevel(self):
        self.sendCommand("RAIN")

    def getBufferStatus(self):
        self.sendCommand("BUFFER")

    def receiver(self, data):
        if data[1] == "REFBEGIN":
            self.bufferRefillInProgress=True

        if data[1] == "REFEND":
            self.bufferRefillInProgress=False
        
        if data[1] == "RAIN":
            self.rainWaterLevel = float(data[2])
            
        if data[1] == "OPENED":
            print("Valve Open: " + str(data[2]), end="\r\n")

        if data[1] == "BUFFER":
            if data[2] == "FULL":
                self.bufferFull = True
                self.bufferEmpty = False
            if data[2] == "EMPTY":
                self.bufferFull = False
                self.bufferEmpty = True
            if data[2] == "PARTIAL":
                self.bufferFull = False
                self.bufferEmpty = False
