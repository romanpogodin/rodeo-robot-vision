#include <Servo.h>

const int kDelay = 10;
const int kMaxSearchShift = 150;
const int kMaxRoundShift = 50;
const int kMaxDistance = 500;

Servo myservoLeft;  // create servo object to control a servo
Servo myservoRight;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int sensorPinLeft = A0;    // select the input pin for the potentiometer
int sensorPinRight = A1;
int sensorPinGround = A2;
int sensorPinTopLeft = A3;
int sensorPinTopRight = A4;
int sensorDistance = A5;

int sensorValueLeft = 0;  // variable to store the value coming from the sensor
int sensorValueRight = 0;
int sensorValueGround = 0;
int sensorValueTopLeft = 0;
int sensorValueTopRight = 0;
int distance = 0;

int leftSpeed = 0;    // variable to store the servo position
int rightSpeed = 0;

int searchShift = 0;

void setup() {
  myservoLeft.attach(9);  // attaches the servo on pin 9 to the servo object
  myservoRight.attach(8);  // attaches the servo on pin 8 to the servo object
  pinMode(5, OUTPUT); // lightsource dectector
  pinMode(4, OUTPUT); // wall detector
  Serial.begin(9600);
}

void loop() {
  myservoLeft.attach(9);
  myservoRight.attach(8);

  // Actual input
  sensorValueLeft = analogRead(sensorPinLeft);
  sensorValueRight = analogRead(sensorPinRight);
  sensorValueGround = analogRead(sensorPinGround);
  
  // Baseline values
  sensorValueTopLeft = analogRead(sensorPinTopLeft);
  sensorValueTopRight = analogRead(sensorPinTopRight);

  distance = analogRead(sensorDistance);

  int baseline = min(sensorValueTopRight, sensorValueTopLeft);
  
  leftSpeed = 180;
  rightSpeed = 0;

  if (sensorValueGround < (baseline / 10)) {
      Serial.println("STOP");
      myservoLeft.detach();
      myservoRight.detach(); 
  } else if ((sensorValueRight > baseline - 400 && 
      sensorValueLeft > baseline - 400) 
      || distance > kMaxDistance) {
    digitalWrite(5, LOW);
    ++searchShift;

    if (distance <= kMaxDistance) { 
      digitalWrite(4, LOW);
      if (searchShift > kMaxSearchShift) {
        leftSpeed = 0;
        Serial.println("SEARCH, TURNING AROUND");
      } else {
        Serial.println("SEARCH, FORWARD");
      }
    } else {
      digitalWrite(4, HIGH);
      if (searchShift < kMaxSearchShift) {
        leftSpeed = 0;
        rightSpeed = 180;
        Serial.println("SEARCH, MOVING BACKWARD");
      } else {
        leftSpeed = 0;
        Serial.println("SEARCH, TURNING AROUND");
      }
    }
    
    searchShift = searchShift % (kMaxSearchShift + kMaxRoundShift);
    Serial.println(searchShift);
  } else {
    digitalWrite(4, LOW);
    digitalWrite(5, HIGH);

    if ((sensorValueLeft > sensorValueRight + 100) ||
        (sensorValueLeft > sensorValueRight + 50 && 
        sensorValueLeft > sensorValueGround + 50)) {
      Serial.println("TURN RIGHT");
      myservoLeft.detach();
    } else if ((sensorValueRight > sensorValueLeft + 100) ||
        (sensorValueRight > sensorValueLeft + 50 && 
        sensorValueRight > sensorValueGround + 50)) {
      Serial.println("TURN LEFT");
      myservoRight.detach();
    } else if ((sensorValueGround < sensorValueLeft - 50) &&
          (sensorValueGround < sensorValueRight - 50)) {
      leftSpeed = 0;
      rightSpeed = 180;
      Serial.println("MOVING BACKWARD");
    } else {
      Serial.println("MOVING FORWARD");
    }
  }
  
  myservoLeft.write(leftSpeed);
  myservoRight.write(rightSpeed);   

  Serial.println("New round");
  Serial.print("L ");
  Serial.print(sensorValueLeft);
  Serial.print("\tR ");
  Serial.print(sensorValueRight);
  Serial.print("\tG ");
  Serial.print(sensorValueGround);
  Serial.print("\tTL ");
  Serial.print(sensorValueTopLeft);
  Serial.print("\tTR ");
  Serial.print(sensorValueTopRight);
  Serial.print("\tD ");
  Serial.print(distance);
  Serial.print("\tB ");
  Serial.println(baseline);

  
  delay(kDelay);
}

