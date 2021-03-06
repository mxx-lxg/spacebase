import serial
import threading
import sys
import random

# Standartklasse für USB-Geräte
# benötigt: comDir, deviceType, receiver

class Device():
    __thread = False

    def __init__(self, comDir, deviceType, receiver):
        self.connection = serial.Serial(comDir, 9600)

        line = self.connection.readline()
        comString = line.rstrip()
        data = comString.decode().split(":")

        if data[0] == "READY" and data[1] == deviceType:
            print(deviceType + " found", end="\r\n")
            self.__thread = threading.Thread(target=self.receiverThread, args=(self.connection, receiver))
            self.__thread.start()
        else:
            sys.exit('no connected device')
        
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
            comId = random.randint(100,999)
            package = str(comId) + ":" + str(command)
            #print("sending : " + package)
            self.connection.write((package  + "\n").encode())
        else:
            sys.exit('no device')
    