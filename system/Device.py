import serial
import threading
import sys
import random
import logging

# Standartklasse für USB-Geräte
# benötigt: comDir, deviceType, receiver

class Device():
    __thread = False
    logger = logging.getLogger(__name__)

    def __init__(self, comDir, deviceType, receiver):
        self.connection = serial.Serial(comDir, 9600)

        line = self.connection.readline()
        comString = line.rstrip()
        data = comString.decode().split(":")

        #print("DEBUG COMS: " + comString.decode())

        if data[0] == "READY" and data[1] == deviceType:
            print(deviceType + " found", end="\r\n")
            self.logger.info(deviceType + " found")
            self.__thread = threading.Thread(target=self.receiverThread, args=(self.connection, receiver))
            self.__thread.start()
        else:
            self.logger.info("no devices connected")
            sys.exit("no devices connected")
        
    #Daten von Gerät empfangen und an Receiver Methode übergeben
    def receiverThread(self, ser, receiver):
        while True:
            reading = ser.readline().rstrip().decode()
            #print("received: " + reading)
            data = reading.split(":")
            receiver(data)

    #Befehl an Gerät senden
    def sendCommand(self, command):
        if self.__thread:
            package = str(command)
            #print("sending : " + package)
            self.connection.write((package  + "\n").encode())
        else:
            sys.exit('no device')
    