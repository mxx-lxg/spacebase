#include <Arduino.h>

bool isInitialized = false;

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

void openValve(int id){
  delay(500);
  Serial.println("OPENED:" + id);
}

void closeValves(){
  delay(500);
  Serial.println("CLOSED");
}

void sendRainLevel(){
  float rainLevel = 69.42;
  delay(500);
  Serial.println("RAIN:" + String(rainLevel, 1));
}

void sendBufferStatus(){
  delay(500);
  Serial.print("BUFFER:"); //FULL, EMPTY, PARTIAL
  Serial.println("PARTIAL");
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.println(sendReady("irrigation"));
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0)  {
    
    String query = Serial.readStringUntil('\n');

    String command = getValue(query, ':', 0);
    String params = getValue(query, ':', 1);

    if(command == "INIT"){
      isInitialized = true;
    }
    
    //erst daten spamen, wenn server bereit
    if(isInitialized) {
      //Send
      //RAIN:[PERCENT] - Regentonne Füllstand in %
      //OPENED:[valve] - Ventil geöffnet
      //BUFFER:[FULL/EMPTY/PARTIAL] - Buffer Status

      //gebraucht?
      //REFBEGIN - Refill hat begonnen
      //REFEND - Refill beendet


      //Receive
      //OPEN:[valve] - Ventil öffnen
      if(command == "OPEN"){
        openValve(params.toInt());
      }

      //CLOSE - alle Ventile schließen
      if(command == "CLOSE"){
        closeValves();
      }

      //REFILL - Buffer auffüllen
      //if(command == "REFILL"){}

      //RAIN - Regentonne Füllstand melden
      if(command == "RAIN"){
        sendRainLevel();
      }

      //BUFFER - Buffer Status melden
      if(command == "BUFFER"){
        sendBufferStatus();
      }
    }
  }
}