# Example file showing a basic pygame "game loop"
import pygame
import threading





COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_OK = (0, 255, 0)
COLOR_WARNING = (255, 255, 0)
COLOR_DANGER = (255, 0, 0)

class UserInterface():
    __thread = None

    backgroundColor = (255, 255, 255)
    foregroundColor = (0, 0, 0)

    def __init__(self):
        self.__thread = threading.Thread(target=self.uiLoop, args=())
        self.__thread.start()

    
    def uiLoop(self):
        nightMode = True
        
        if nightMode:
            self.backgroundColor = (0, 0, 0)
            self.foregroundColor = (255, 255, 255)

        # pygame setup
        pygame.init()
        screen = pygame.display.set_mode((1440, 900), pygame.FULLSCREEN)
        clock = pygame.time.Clock()
        pygame.font.init()

        while True:
            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # fill the screen with a color to wipe away anything from last frame
            screen.fill(self.backgroundColor)
            self.drawGauge(screen, [0, 0, 100], "%", "Wass.", 40)
            self.drawGauge(screen, [37, 0, 100], "%", "Luftf.", 240)
            self.drawGauge(screen, [28, 0, 40], "°C", "Temp.", 440)
            self.drawWindowIndicator(screen, 2)
            self.drawStatusBool(screen, "Winterschlaf", "AUS", 40, 800, (0, 255,0))
            self.drawStatusBool(screen, "Nachtmodus", "AN", 110, 800, self.backgroundColor)

            self.drawStatus(screen, "MQTT", "verbunden", 250, 800, self.backgroundColor)
            self.drawStatus(screen, "Fenster", "Fehler!", 320, 800, (255, 0, 0))
            self.drawStatus(screen, "Wasser", "nicht verb.", 390, 800, (255, 255, 0))
            self.drawStatus(screen, "Temperatur", "verbunden", 460, 800, self.backgroundColor)
            # RENDER YOUR GAME HERE
            # flip() the display to put your work on screen
            pygame.display.flip()

            clock.tick(60)  # limits FPS to 60

        pygame.quit()

    def translate(self, value, leftMin, leftMax, rightMin, rightMax):
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)

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

    def drawWindowIndicator(self, screen, value):
        #Umrandung
        pygame.draw.rect(screen, self.foregroundColor, (640, 40, 70, 155))
        pygame.draw.rect(screen, self.foregroundColor, (640, 215, 70, 155))
        pygame.draw.rect(screen, self.foregroundColor, (640, 390, 70, 155))
        pygame.draw.rect(screen, self.foregroundColor, (640, 565, 70, 155))

        if value >= 4:
            pygame.draw.rect(screen, self.backgroundColor, (650, 50, 50, 135))        
        if value >= 3:
            pygame.draw.rect(screen, self.backgroundColor, (650, 225, 50, 135))
        if value >= 2:
            pygame.draw.rect(screen, self.backgroundColor, (650, 400, 50, 135))
        if value >= 1:
            pygame.draw.rect(screen, self.backgroundColor, (650, 575, 50, 135))
        
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

        
        pygame.draw.rect(screen, background, (left, top+50, 550, top+50))
        value_text_surface = value_font.render(value, False, textColor)
        label_text_surface = value_font.render(label, False, textColor)
        pygame.draw.line(screen, self.foregroundColor, (left, top+50), (left+550, top+50), 3)

        screen.blit(value_text_surface, (left+320, top))
        screen.blit(label_text_surface, (left+10, top))


ui = userInterface()
