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
    mqttClient = None

    def __init__(self, comDir, mqttClient=None):
        Device.__init__(self, comDir, "windows", self.receiver)
        self.mqttClient = mqttClient
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
            self.logger.info("setting windows to stage: " + str(stage))
            print("setting windows to stage: " + str(stage), end="\r\n")
            self.sendCommand("STAGE:" + str(stage))
            if self.mqttClient: self.mqttClient.publish("WINDOWS", stage)
        else:
            print("window position locked. No action. \r\n")

    def receiver(self, data):
        if 1 < len(data): data[1] = float(data[1]) # value spalte zu float konvertieren
        if data[0] == "MOVING":
            self.moving = data[1]
            if not(self.resetInProgress):
                self.currentStage = data[1] - 1

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

        if data[0] == "STAGEFIN":
            self.currentStage = data[1]
            self.moving = None
            print("finished adjusting windows")
            self.logger.info("finished adjusting windows")


        if data[0] == "RESETFIN":
            self.currentStage = 0
            self.moving = None
            self.resetInProgress = False
            print("finished resetting windows")
            self.logger.info("finished resetting windows")
