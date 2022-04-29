#include "DHT.h"
#include "SpaceBaseUtils.h"

#define DHTPIN 13
#define DHTTYPE DHT11
bool isInitialized = false;

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  // put your setup code here, to run once:
  dht.begin();
  Serial.begin(9600);
  Serial.println(Comms::sendReady("environment"));
}

void loop() {
  // put your main code here, to run repeatedly:

  if (Serial.available() > 0)  {
    
    String query = Serial.readStringUntil('\n');

    String queryId = Comms::getValue(query, ':', 0);
    String command = Comms::getValue(query, ':', 1);
    String params = Comms::getValue(query, ':', 2);

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
