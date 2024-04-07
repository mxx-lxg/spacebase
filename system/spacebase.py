from Habitat import Habitat

import logging
import os
from os.path import exists
import configparser
from UserInterface import UserInterface
import sys
import schedule
import time


#log setup
# set up logging to file
print("working directory: " + os.getcwd())
logging.basicConfig(
    filename= os.getcwd() + '/spacebase.log',
    level=logging.INFO, 
    format= '[%(asctime)s] %(name)s: %(levelname)s - %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S'
)
# set up logging to console
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
# set a format which is simpler for console use
formatter = logging.Formatter('[%(asctime)s] %(name)s: %(levelname)s %(message)s')
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)
logger = logging.getLogger(__name__)

logger.info("startup")

#Konfiguartion laden oder erstellen

if not exists(os.getcwd() + '/spacebase.conf'):
    print("No config file found. Writing new config and exiting...")
    
    newConfig = configparser.ConfigParser()
    newConfig.add_section('windows')
    newConfig.set('windows', 'stage_1', '22')
    newConfig.set('windows', 'stage_2', '24')
    newConfig.set('windows', 'stage_3', '26')
    newConfig.set('windows', 'stage_4', '28')
    newConfig.set('windows', 'check_interval', '300')
    newConfig.add_section('climate')
    newConfig.set('climate', 'log_interval', '300')
    newConfig.set('climate', 'heater_threshold', '1')
    newConfig.set('climate', 'heater_stop', '3')
    newConfig.add_section('irrigation')
    newConfig.set('irrigation', 'left_threshold', '15')
    newConfig.set('irrigation', 'right_threshold', '15')
    newConfig.add_section('mqtt')
    newConfig.set('mqtt', 'broker', 'smart.home')
    newConfig.set('mqtt', 'port', '1883')
    newConfig.set('mqtt', 'client_id', '69420')
    newConfig.set('mqtt', 'user', 'max')
    newConfig.set('mqtt', 'pw', 'public')
    with open(os.getcwd() + '/spacebase.conf', 'x') as configFile:
        newConfig.write(configFile)
        configFile.close()
        sys.exit()


print("loading config")
config = configparser.ConfigParser()
config.read(os.getcwd() + '/spacebase.conf')


#habitat code
habitat = Habitat(config)

#UI
user_interface = UserInterface(habitat = habitat)


#main job loop
while True:
    schedule.run_pending()
    time.sleep(1)
