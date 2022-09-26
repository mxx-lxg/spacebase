from Device import Device
import logging

class Windows(Device):
    moving = None
    resetInProgress = False
    locked = False
    currentStage = 0
    lastTemperature = 10
    lastHumidity = 10
    logger = logging.getLogger(__name__)

    def __init__(self, comDir):
        Device.__init__(self, comDir, "windows", self.receiver)
        self.init()

    def reset(self):
        self.logger.info("windows reset")
        self.sendCommand("RESET")
        self.resetInProgress = True
        self.locked = False

    def init(self):
        self.sendCommand("INIT")

    def forceClosed(self):
        self.logger.info("windows forced closed")
        self.locked = False
        self.setToStage(0)
        self.locked = True

    def forceOpened(self):
        self.logger.info("windows forced opened")
        self.locked = False
        self.setToStage(4)
        self.locked = True

    def unforce(self):
        self.logger.info("windows set to auto")
        self.locked = False
        
    def setToStage(self, stage):
        if not(self.locked):
            print("setting windows to stage: " + str(stage), end="\r\n")
            self.sendCommand("STAGE:" + str(stage))
        else:
            print("window position locked. No action. \r\n")

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

                for i in range(1, 5):
                    if i == self.moving:
                        moveIllustration = moveIllustration + "X"
                    else:
                        moveIllustration = moveIllustration + "-"

                print("resetting window "+str(int(self.moving))+" " + moveIllustration)

        if data[1] == "STAGEFIN":
            self.currentStage = data[2]
            self.moving = None
            print("finished adjusting windows")


        if data[1] == "RESETFIN":
            self.currentStage = 0
            self.moving = None
            self.resetInProgress = False
            print("finished resetting windows")

            