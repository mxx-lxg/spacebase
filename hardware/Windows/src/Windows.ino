#include <Arduino.h>

#include "AFMotor.h"

int incomingByte = 0;    // for incoming serial data
int windowsOpen = 0;
int moveDuration = 13; //Zeit, die das Fenster zum Bewegen braucht, in Sekunden (11s für Motoren)
bool isInitialized = false;

AF_DCMotor window1(1);
AF_DCMotor window2(2);
AF_DCMotor window3(3);
AF_DCMotor window4(4);

void setup() {
  window1.setSpeed(255);
  window1.run(RELEASE);
  window2.setSpeed(255);
  window2.run(RELEASE);
  window3.setSpeed(255);
  window3.run(RELEASE);
  window4.setSpeed(255);
  window4.run(RELEASE);

  Serial.begin(9600);  
  Serial.println("READY:windows");
}

void loop() {
  if (Serial.available() > 0)  {
    
    String query = Serial.readStringUntil('\n');

    String command = getValue(query, ':', 0);
    String params = getValue(query, ':', 1);

    if(command == "INIT"){
      isInitialized = true;
    }
    
    if(command == "RESET"){
      Serial.println("BUSY");
      resetWindows();
      Serial.println("RESETFIN");
    }

    if(command == "STAGE"){
      int stage = params.toInt();
      Serial.println("BUSY");

      setWindows(stage);

      Serial.print("STAGEFIN:");
      Serial.println(windowsOpen);
    }
  }
}

void setWindows(int stage) {

  //Fenster müssen geöffnet werden
  if (windowsOpen < stage) {
    for (int i = 1; i <= 4; i++)
    {
      if (i > windowsOpen && i <= stage) {
        Serial.print("MOVING:");
        Serial.println(i);
        openWindow(i);
      }
    }
  }

  //Fenster müssen geschlossen werden
  if (windowsOpen > stage) {
    for (int i = 1; i <= 4; i++)
    {
      if (i <= windowsOpen && i > stage) {
        Serial.print("MOVING:");
        Serial.println(i);
        closeWindow(i);
      }
    }
  }

  windowsOpen = stage;
}

void closeWindow(int window) {
  switch (window) {
    case 1:
      window1.run(BACKWARD);
      delay(moveDuration * 1000);
      window1.run(RELEASE);
      delay(200);
      break;
    case 2:
      window2.run(BACKWARD);
      delay(moveDuration * 1000);
      window2.run(RELEASE);
      delay(200);
      break;
    case 3:
      window3.run(BACKWARD);
      delay(moveDuration * 1000);
      window3.run(RELEASE);
      delay(200);
      break;
    case 4:
      window4.run(BACKWARD);
      delay(moveDuration * 1000);
      window4.run(RELEASE);
      delay(200);
      break;
  }
}

void openWindow(int window) {
  switch (window) {
    case 1:
      window1.run(FORWARD);
      delay(moveDuration * 1000);
      window1.run(RELEASE);
      delay(200);
      break;
    case 2:
      window2.run(FORWARD);
      delay(moveDuration * 1000);
      window2.run(RELEASE);
      delay(200);
      break;
    case 3:
      window3.run(FORWARD);
      delay(moveDuration * 1000);
      window3.run(RELEASE);
      delay(200);
      break;
    case 4:
      window4.run(FORWARD);
      delay(moveDuration * 1000);
      window4.run(RELEASE);
      delay(200);
      break;
  }
}

void resetWindows() {
  delay(1000);
  
  Serial.println("MOVING:1");
  openWindow(1);
  closeWindow(1);
  
  Serial.println("MOVING:2");
  openWindow(2);
  closeWindow(2);
  
  Serial.println("MOVING:3");
  openWindow(3);
  closeWindow(3);
  
  Serial.println("MOVING:4");
  openWindow(4);
  closeWindow(4);
  windowsOpen = 0;
}

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
