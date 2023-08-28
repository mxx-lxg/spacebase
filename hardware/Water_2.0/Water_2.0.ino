#include <Adafruit_SSD1306.h>

// Define Trig and Echo pin:
#define trigPin 12
#define echoPin 13

#define FULL_VAL 20
#define EMPTY_VAL 70

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

bool isInitialized = false;
int currentLevel = 0;

void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT_PULLUP);
  pinMode(2, OUTPUT);
  Serial.begin(9600);
  Serial.println("READY:water");


  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3D for 128x64
    Serial.println(F("SSD1306 allocation failed"));
    for(;;);
  }
  delay(1000);
  display.clearDisplay();

  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 10);
  // Display static text
  display.println("SpaceBase Regenwasser");
  display.display(); 
  display.setRotation(1);
  delay(1000);
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
    
    if(command == "RAIN"){
      reportLevel();
    }
  }

  currentLevel = getLevel();
  displayStatus(currentLevel);
  delay(100);
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

int getDistance(){
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

    delayMicroseconds(10);

    return distance;
}

int getLevel(){
  int smallestDistance = 100;
  
  for(var i = 0; i < 5; i++){
    int meassured = getDistance();

    if(smallestDistance > meassured) smallestDistance = meassured;
  }

  return constrain(map(smallestDistance, FULL_VAL, EMPTY_VAL, 100, 0), 0, 100);
}

void reportLevel(){
  Serial.print("RAINLEVEL:");
  //Serial.print(distance);
  //Serial.print("_");
  Serial.println(currentLevel);
}

void openValve(int valve){
  toggleValve(valve, HIGH);
  Serial.print("VPOS:");
  Serial.println("OPEN");
}
void closeValve(int valve){
  toggleValve(valve, LOW); 
  Serial.print("VPOS:");
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


void displayStatus(int level){
  
  display.clearDisplay();
  display.setTextColor(WHITE);

  display.setTextSize(1);
  display.setCursor(25, display.height()-10);
  if(!isInitialized) {
    display.println("no con!");
  }

  int displayLevel = map(level, 0, 100, display.height(), 0);

  display.drawRect(0, 0, 21, display.height(), WHITE);
  display.fillRect(0, displayLevel, 21, display.height(), WHITE);

  display.setTextSize(2);
  display.setCursor(23, level >=15 ? displayLevel : display.height()-15);
  display.print(level);
  display.println("%");

  display.display(); 
} 
