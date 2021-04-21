from Device import Device

class Windows(Device):
    moving = None
    resetInProgress = False
    currentStage = 0
    lastTemperature = 0
    lastHumidity = 0

    def __init__(self, comDir):
        Device.__init__(self, comDir, "windows", self.receiver)
        self.init()

    def reset(self):
        self.sendCommand("RESET")
        self.resetInProgress = True

    def init(self):
        self.sendCommand("INIT")
        
    def setToStage(self, stage):
        print(str(self.lastTemperature)+"°C -> setting windows to stage: " + str(stage))
        self.sendCommand("STAGE:" + str(stage))

    def getAtmospherics(self):
        self.sendCommand("ATMOS")

    def receiver(self, data):
        if 2 < len(data): data[2] = float(data[2]) # value spalte zu float konvertieren

        if data[1] == "MOVING":
            self.moving = data[2]
            if not(self.resetInProgress):
                self.currentStage = data[2] - 1

                moveIllustration = ""

                for i in range(4):
                    if i+1 == self.moving:
                        moveIllustration = moveIllustration + "▄"
                    elif i+1 <= self.currentStage:
                        moveIllustration = moveIllustration + "█"
                    else:
                        moveIllustration = moveIllustration + "-"

                print("adjusting window "+str(int(self.moving))+" " + moveIllustration, end="\r")
            else:
                moveIllustration = ""

                for i in range(4):
                    if i == self.moving:
                        moveIllustration = moveIllustration + "X"
                    else:
                        moveIllustration = moveIllustration + "-"

                print("calibrating windows - " + moveIllustration, end="\r")

        if data[1] == "STAGEFIN":
            self.currentStage = data[2]
            self.moving = None
            print("finished adjusting windows")


        if data[1] == "RESETFIN":
            self.currentStage = 0
            self.moving = None
            self.resetInProgress = False

        if data[1] == "TEMP":
            self.lastTemperature = data[2]
        
        if data[1] == "HUM":
            self.lastHumidity = data[2]
            