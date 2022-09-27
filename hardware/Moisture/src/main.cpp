#include <Arduino.h>

bool isInitialized = false;
String patchId = "left";

String getValue(String data, char separator, int index){
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

String sendReady(String deviceType){
    return "READY:" + deviceType;
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.println(sendReady("moisture"));
}

void loop() {
  // put your main code here, to run repeatedly:

  if (Serial.available() > 0)  {
    
    String query = Serial.readStringUntil('\n');

    String queryId = getValue(query, ':', 0);
    String command = getValue(query, ':', 1);
    String params = getValue(query, ':', 2);

    if(command == "INIT"){
      Serial.print("000:IDENT:");
      Serial.println(patchId);
      isInitialized = true;
    }
    
    //erst daten spamen, wenn server bereit
    if(isInitialized) {
      float m = 69;
      
      Serial.print("000:MOIST:");
      Serial.println(m);   
      delay(1000); 
    }
  }
}