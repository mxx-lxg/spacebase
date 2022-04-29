#include <Arduino.h>

bool isInitialized = false;
// Define Trig and Echo pin:
#define trigPin 12
#define echoPin 13


void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(2, OUTPUT);
  Serial.begin(9600);
  Serial.println("READY:water");
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

    //OPEN [valve] - Ventil öffnen
    //CLOSE [valve] - Ventil schließen
    //LEVEL - Wasserstand Regentonne abfragen
    if(command == "OPEN"){
      int valve = params.toInt();
      openValve(valve);
    }

    if(command == "CLOSE"){
      int valve = params.toInt();
      closeValve(valve);
    }
    
    if(command == "LEVEL"){
      getLevel();
    }
  }
}

//coole splitter klasse
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

void getLevel(){
    // Clear the trigPin by setting it LOW:
  digitalWrite(trigPin, LOW);
  
  delayMicroseconds(10);

 // Trigger the sensor by setting the trigPin high for 10 microseconds:
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(20);
  digitalWrite(trigPin, LOW);
  
  // Read the echoPin. pulseIn() returns the duration (length of the pulse) in microseconds:
  int duration = pulseIn(echoPin, HIGH);
  
  // Calculate the distance:
  int distance = duration*0.034/2;
  
  // Print the distance on the Serial Monitor (Ctrl+Shift+M):

  Serial.print("000");
  Serial.print(":MLEVEL:");
  Serial.println(distance);
}

void openValve(int valve){
  toggleValve(valve, HIGH);
  Serial.print("000");
  Serial.print(":VPOS:");
  Serial.println("OPEN");
}
void closeValve(int valve){
  toggleValve(valve, LOW); 
  Serial.print("000");
  Serial.print(":VPOS:");
  Serial.println("CLOSED");
}

void toggleValve(int valve, int state){
    int vId = 0;
    switch (valve) {
      case 0:
        vId = 2;
        break;
      default:
        // Statement(s)
        break;
    }
    digitalWrite(vId, state);
}
