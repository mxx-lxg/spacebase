#include "DHT.h"
#define DHTPIN 13
#define DHTTYPE DHT11
bool isInitialized = false;

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  // put your setup code here, to run once:
  dht.begin();
  Serial.begin(9600);
  Serial.println("READY:environment");
}

void loop() {
  // put your main code here, to run repeatedly:

  if (Serial.available() > 0)  {
    
    String query = Serial.readStringUntil('\n');

    String queryId = getValue(query, ':', 0);
    String command = getValue(query, ':', 1);
    String params = getValue(query, ':', 2);

    if(command == "INIT"){
      isInitialized = true;
    }
    
    //erst daten spamen, wenn server bereit
    if(isInitialized) {
      float t = dht.readTemperature();
      float h = dht.readHumidity();
      
      Serial.print("000:TEMP:");
      Serial.println(t);   
      Serial.print("000:HUM:");
      Serial.println(h);
      delay(1000); 
    }
  }
}

String getValue(String data, char separator, int index)
{
    int found = 0;
    int strIndex[] = { 0, -1 };
    int maxIndex = data.length() - 1;

    for (int i = 0; i <= maxIndex && found <= index; i++) {
        if (data.charAt(i) == separator || i == maxIndex) {
            found++;
            strIndex[0] = strIndex[1] + 1;
            strIndex[1] = (i == maxIndex) ? i+1 : i;
        }
    }
    return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}
