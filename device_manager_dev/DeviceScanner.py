from os import walk
import serial

class DeviceScanner():
    def findDevices():
        deviceList = dict()

        print("scanning for devices")

        #alles aus dev holen
        for (dirpath, dirnames, filenames) in walk("/dev/"):
            #USB verbindungen filtern
            filtered_filenames = [filename for filename in filenames if filename.startswith("tty")]

            #USB verbindungen durchgehen
            for filename in filtered_filenames:
                #print("trying " + filename)
                try:
                    connection = serial.Serial(port="/dev/" + filename, baudrate=9600, timeout=5)
                    line = connection.readline()
                    comString = line.rstrip()
                    data = comString.decode().split(":")
                    print(data)

                    if data[0] == "READY":
                        #print(data[1] + " found")
                        deviceList["/dev/" + filename] = data[1]
                    
                    connection.close()
                
                except:
                    continue
                    #print("\rscanning", end="\r") 

        print("scan completed")
        print(deviceList)

        return deviceList