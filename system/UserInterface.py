# Example file showing a basic pygame "game loop"
import pygame
from pygame.locals import *
import threading
import logging


COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_OK = (0, 255, 0)
COLOR_WARNING = (255, 255, 0)
COLOR_DANGER = (255, 0, 0)

class UserInterface():
    __thread = None

    backgroundColor = (255, 255, 255)
    foregroundColor = (0, 0, 0)
    width = 1440 #1440
    height = 900 # 900
    logger = logging.getLogger(__name__)

    def __init__(self, habitat, tailLogger):
        self.__thread = threading.Thread(target=self.uiLoop, args=(habitat, tailLogger))
        self.__thread.start()

    
    def uiLoop(self, habitat, tailLogger):
        nightMode = True

        if nightMode:
            self.backgroundColor = (0, 0, 0)
            self.foregroundColor = (255, 255, 255)

        # pygame setup
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)  #pygame.FULLSCREEN
        clock = pygame.time.Clock()
        pygame.font.init()

        running = True
        while running:
            leftOffset = 40
            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False

            # fill the screen with a color to wipe away anything from last frame
            screen.fill(self.backgroundColor)

            if habitat.irrigation is not None:
                self.drawGauge(screen, [habitat.irrigation.rainWaterLevel, 0, 100], "%", "Wass.", leftOffset)
                leftOffset += 220
                self.drawStatus(screen, "Bewässerung", "verbunden", 100, 850, self.backgroundColor)
            else:
                self.drawStatus(screen, "Bewässerung", "Fehler", 100, 850, (255, 0, 0))

            if habitat.environment is not None:
                self.drawGauge(screen, [habitat.environment.lastHumidity, 0, 100], "%", "Luftf.", leftOffset)
                leftOffset += 220
                self.drawGauge(screen, [habitat.environment.lastTemperature, 0, 40], "°C", "Temp.", leftOffset)
                leftOffset += 220
                self.drawStatus(screen, "Sensoren", "verbunden", 160, 850, self.backgroundColor)
            else:
                self.drawStatus(screen, "Sensoren", "Fehler", 160, 850, (255, 0, 0))
            
            if habitat.windows is not None:
                self.drawWindowIndicator(screen, habitat.windows.currentStage, leftOffset)
                self.drawStatus(screen, "Fenster", "verbunden", 220, 850, self.backgroundColor)
                leftOffset += 220
            else:
                self.drawStatus(screen, "Fenster", "Fehler", 220, 850, (255, 0, 0))

            self.drawStatusBool(screen, "Winterschlaf", "AN" if habitat.hibernation_mode else "AUS", 340, 850, (255, 0, 0) if habitat.hibernation_mode else self.backgroundColor)
            self.drawStatusBool(screen, "Pumpe", "AN" if habitat.pump.state else "AUS", 400, 850, (255, 0, 0) if habitat.pump.state else self.backgroundColor)
            self.drawStatusBool(screen, "Heizung", "AN" if habitat.heater.state else "AUS", 460, 850, (255, 0, 0) if habitat.heater.state else self.backgroundColor)

            #self.drawStatusBool(screen, "Nachtmodus", "AN", 110, 800, self.backgroundColor)

            self.drawStatus(screen, "MQTT", "verbunden" if habitat.mqttClient.connected else "nicht ver.", 40, 850, self.backgroundColor)

            self.drawLog(screen, tailLogger)

            # flip() the display to put your work on screen
            pygame.display.flip()

            clock.tick(30)  # limits FPS to 30

        pygame.quit()

    def translate(self, value, leftMin, leftMax, rightMin, rightMax):
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)
    
    def drawLog(self, screen, tailLogger):
        value_font = pygame.font.SysFont('Consolas', 20)
        os = 730

        for log in tailLogger.contents_list():
            bg_color = (0,0,0)
            if "ERROR" in log:
                bg_color = (255,0,0)
            value_text_surface = value_font.render(log, False, (255,255,255), bg_color)
            screen.blit(value_text_surface, (10, pos))
            pos+=25

    def drawGauge(self, screen, data, unit, label, offset):  
        value = data[0]
        minVal = data[1]
        maxVal = data[2]

        
        value_font = pygame.font.SysFont('Consolas Bold', 60)
        label_font = pygame.font.SysFont('Consolas Bold', 50)

        value_text_surface = value_font.render(str(value) + str(unit), False, self.foregroundColor)
        label_text_surface = label_font.render(label, False, self.foregroundColor)

        #Umrandung                       #left, top, width, height
        pygame.draw.rect(screen, self.foregroundColor, (offset, 40, 70, 680))
        
        #Balken
        heightBar = self.translate(value, minVal, maxVal, 0, 660)
        pygame.draw.rect(screen, self.backgroundColor, (10 + offset, 710 - heightBar, 50, heightBar))

        #Strich
        pygame.draw.line(screen, self.foregroundColor, (70 + offset, 710 - heightBar), (180 + offset, 710 - heightBar), 5)

        #Beschriftung
        screen.blit(value_text_surface, (80 + offset, 670 - heightBar))
        screen.blit(label_text_surface, (80 + offset, 715 - heightBar))

    def drawWindowIndicator(self, screen, value, left):
        #Umrandung
        pygame.draw.rect(screen, self.foregroundColor, (left, 40, 70, 155))
        pygame.draw.rect(screen, self.foregroundColor, (left, 215, 70, 155))
        pygame.draw.rect(screen, self.foregroundColor, (left, 390, 70, 155))
        pygame.draw.rect(screen, self.foregroundColor, (left, 565, 70, 155))

        if value >= 4:
            pygame.draw.rect(screen, self.backgroundColor, (left+10, 50, 50, 135))        
        if value >= 3:
            pygame.draw.rect(screen, self.backgroundColor, (left+10, 225, 50, 135))
        if value >= 2:
            pygame.draw.rect(screen, self.backgroundColor, (left+10, 400, 50, 135))
        if value >= 1:
            pygame.draw.rect(screen, self.backgroundColor, (left+10, 575, 50, 135))
        
    def drawStatusBool(self, screen, label, value, top, left, background):
        value_font = pygame.font.SysFont('Consolas Bold', 60)
        
        value_text_surface = value_font.render(value, False, self.foregroundColor, background)
        label_text_surface = value_font.render(label, False, self.foregroundColor)
        pygame.draw.line(screen, self.foregroundColor, (left, top+50), (left+390, top+50), 3)

        screen.blit(value_text_surface, (left+300, top))
        screen.blit(label_text_surface, (left, top))

    def drawStatus(self, screen, label, value, top, left, background):
        textColor = self.foregroundColor


        value_font = pygame.font.SysFont('Consolas Bold', 60)

        
        pygame.draw.rect(screen, background, (left, top, 550, 57))
        value_text_surface = value_font.render(value, False, textColor)
        label_text_surface = value_font.render(label, False, textColor)
        pygame.draw.line(screen, self.foregroundColor, (left, top+57), (left+550, top+57), 3)

        screen.blit(value_text_surface, (left+320, top+8))
        screen.blit(label_text_surface, (left+10, top+8))

