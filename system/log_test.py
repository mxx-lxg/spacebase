
from TailLog import TailLogger
import sys
import logging
import os
from os.path import exists
import pygame
import itertools

# set up logging to file
print("working directory: " + os.getcwd())
logging.basicConfig(
    filename= os.getcwd() + '/test.log',
    level=logging.INFO, 
    format= '[%(asctime)s] %(name)s: %(levelname)s - %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S'
)
# set up logging to console
console = logging.StreamHandler()
console.setLevel(logging.ERROR)# set up logging to UI
tailLogger = TailLogger(5)
log_ui_handler = tailLogger.log_handler

# set a format which is simpler for console use
formatter = logging.Formatter('[%(asctime)s] %(name)s: %(levelname)s %(message)s')
console.setFormatter(formatter)
log_ui_handler.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)
logging.getLogger('').addHandler(log_ui_handler)

logger = logging.getLogger(__name__)

logger.info("startup")
logger.info("lala")
logger.info("lolo")
logger.info("lili")
logger.info("lulu")
logger.info("lele")


print("tail log")
print(tailLogger.contents())





# pygame setup
pygame.init()
screen = pygame.display.set_mode((800, 800))  #pygame.FULLSCREEN
clock = pygame.time.Clock()
pygame.font.init()

logger.error("test error")

logger.info("done")


value_font = pygame.font.SysFont('Consolas', 20)

print(tailLogger.contents_list())
timer = 0
while True:
    pos = 10

    for log in tailLogger.contents_list():
        bg_color = (0,0,0)
        if "ERROR" in log:
            bg_color = (255,0,0)
        value_text_surface = value_font.render(log, False, (255,255,255), bg_color)
        screen.blit(value_text_surface, (10, pos))
        pos+=25
    
    if timer > 90:
        logger.info("timed log")

    timer+=1
    clock.tick(30)  # limits FPS to 30
    pygame.display.flip()