#include <Arduino.h>
#include <SpaceBaseUtils.h>

int incomingByte = 0;    // for incoming serial data
int windowsOpen = 0;
int moveDuration = 12; //Zeit, die das Fenster zum Bewegen braucht, in Sekunden (11s für Motoren)
bool isInitialized = false;

void setup() {
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
  Serial.begin(9600);  
  Serial.println(Comms::sendReady("windows"));
}

void loop() {
  if (Serial.available() > 0)  {
    
    String query = Serial.readStringUntil('\n');

    String queryId = Comms::getValue(query, ':', 0);
    String command = Comms::getValue(query, ':', 1);
    String params = Comms::getValue(query, ':', 2);

    if(command == "INIT"){
      isInitialized = true;
    }
    
    if(command == "RESET"){
      Serial.print(queryId);
      Serial.println(":BUSY");
      resetWindows(queryId.toInt());
      Serial.print(queryId);
      Serial.println(":RESETFIN");
    }

    if(command == "STAGE"){
      int stage = params.toInt();
      Serial.print(queryId);
      Serial.println(":BUSY");

      setWindows(stage, queryId.toInt());
 
      Serial.print(queryId);
      Serial.print(":STAGEFIN:");
      Serial.println(windowsOpen);
    }
  }
}

void setWindows(int stage, int queryId) {

  //Fenster müssen geöffnet werden
  if (windowsOpen < stage) {
    for (int i = 1; i <= 4; i++)
    {
      if (i > windowsOpen && i <= stage) {
        Serial.print(queryId);
        Serial.print(":MOVING:");
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
        Serial.print(queryId);
        Serial.print(":MOVING:");
        Serial.println(i);
        closeWindow(i);
      }
    }
  }

  windowsOpen = stage;
}

void closeWindow(int window) {
  int channel = 0;
  switch (window) {
    case 1:
      channel = 3;
      break;
    case 2:
      channel = 5;
      break;
    case 3:
      channel = 7;
      break;
    case 4:
      channel = 9;
      break;
  }

  //Ablaufblock
  digitalWrite(channel, HIGH);
  delay(moveDuration * 1000);
  digitalWrite(channel, LOW);
  delay(500);
  //Ablaufblock Ende
}

void openWindow(int window) {
  int channel = 0;
  switch (window) {
    case 1:
      channel = 4;
      break;
    case 2:
      channel = 6;
      break;
    case 3:
      channel = 8;
      break;
    case 4:
      channel = 10;
      break;
  }

  //Ablaufblock
  digitalWrite(channel, HIGH);
  delay(moveDuration * 1000);
  digitalWrite(channel, LOW);
  delay(200);
  //Ablaufblock Ende
}

void resetWindows(int queryId) {
  digitalWrite(3, LOW);
  digitalWrite(4, LOW);
  digitalWrite(5, LOW);
  digitalWrite(6, LOW);
  digitalWrite(7, LOW);
  digitalWrite(8, LOW);
  digitalWrite(9, LOW);
  digitalWrite(10, LOW);
  delay(1000);
 
  Serial.print(queryId);
  Serial.print(":");
  Serial.println("MOVING:1");
  openWindow(1);
  closeWindow(1);
  
  Serial.print(queryId);
  Serial.print(":");
  Serial.println("MOVING:2");
  openWindow(2);
  closeWindow(2);
  
  Serial.print(queryId);
  Serial.print(":");
  Serial.println("MOVING:3");
  openWindow(3);
  closeWindow(3);
  
  Serial.print(queryId);
  Serial.print(":");
  Serial.println("MOVING:4");
  openWindow(4);
  closeWindow(4);
  windowsOpen = 0;
}
