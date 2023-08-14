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
        #TODO Refill übernimmt Pumpe an Relais
        self.sendCommand("REFILL")
        self.bufferRefillInProgress=True

    def getRainWaterLevel(self):
        self.sendCommand("RAIN")

    def getBufferStatus(self):
        self.sendCommand("BUFFER")

    def receiver(self, data):
        if 1 < len(data): data[1] = float(data[1])
        if data[0] == "RAINLEVEL":
            self.rainWaterLevel=data[1]

        if data[0] == "REFBEGIN":
            self.bufferRefillInProgress=True

        if data[0] == "REFEND":
            self.bufferRefillInProgress=False
        
        if data[0] == "RAIN":
            self.rainWaterLevel = float(data[1])
            
        if data[0] == "OPENED":
            print("Valve Open: " + str(data[1]), end="\r\n")

        if data[0] == "CLOSED":
            print("Irrigation valves closed", end="\r\n")

        if data[0] == "BUFFER":
            if data[1] == "FULL":
                self.bufferFull = True
                self.bufferEmpty = False
            if data[1] == "EMPTY":
                self.bufferFull = False
                self.bufferEmpty = True
            if data[1] == "PARTIAL":
                self.bufferFull = False
                self.bufferEmpty = False
