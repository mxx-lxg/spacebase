from os import walk
from serial import Serial

class DeviceScanner():
    def findDevices():
        deviceList = dict()

        print("scanning for serial devices\r")

        #alles aus dev holen
        for (dirpath, dirnames, filenames) in walk("/dev/"):
            #USB verbindungen filtern
            filtered_filenames = [filename for filename in filenames if filename.startswith(("ttyS", "ttyA"))]

            #USB verbindungen durchgehen
            for filename in filtered_filenames:
                #print("trying " + filename)
                try:
                    connection = Serial(port="/dev/" + filename, baudrate=9600, timeout=5)
                    line = connection.readline()
                    comString = line.rstrip()
                    data = comString.decode().split(":")
                    print(data, end="\r\n")

                    if data[0] == "READY":
                        #print(data[1] + " found")
                        deviceList["/dev/" + filename] = data[1]
                    
                    connection.close()
                
                except Exception as e:
                    print(e)
                    continue
                    #print("\rscanning", end="\r") 

        print("scan completed\r\n")
        print(deviceList, end="\r\n")

        return deviceList