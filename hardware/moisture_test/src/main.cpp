#include <Arduino.h>

/*
minimum is 415
maximum is 815
*/
#define WET_A 430
#define DRY_A 815


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  //Serial.println("ready");
}

void loop() {
  // put your main code here, to run repeatedly:
  int sensorValueA = analogRead(A0);
  int sensorValueB = analogRead(A1);

  int percentageA = map(sensorValueA, DRY_A, WET_A, 0, 100);
  int percentageB = map(sensorValueB, DRY_A, WET_A, 0, 100);

  Serial.print(sensorValueA);
  Serial.print(" ");
  Serial.print(percentageA);
  Serial.print(" ");
  Serial.print(sensorValueB);
  Serial.print(" ");
  Serial.println(percentageB);
  
  delay(1000);
}