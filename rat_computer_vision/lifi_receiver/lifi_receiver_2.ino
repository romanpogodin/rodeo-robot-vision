#include <Servo.h>  //motor program
#include <SPI.h>    // Serial Peripheral Interface bus library
#include "RF24.h"   // Library for nRF24L01s

bool radioNumber = 0;
RF24 radio(2, 3);  // For Arduino Micro
byte addresses[][6] = {"1Node", "2Node"};
bool role = 0; // Local state variable that controls whether this node is sending 1 or receiving 0

const int kDelay = 20;

Servo myservoLeft;  // create servo object to control a servo
Servo myservoRight;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int leftSpeed = 0;    // variable to store the servo position
int rightSpeed = 0;
int go = 0;

void setup() {
  myservoLeft.attach(9);  // attaches the servo on pin 9 to the servo object
  myservoRight.attach(8);  // attaches the servo on pin 8 to the servo object
  pinMode(12, OUTPUT); // lightsource dectector
  pinMode(10, OUTPUT); // wall detector
  Serial.begin(115200);

  radio.begin();
  radio.setPALevel(RF24_PA_LOW); // Set the Power Level low
  radio.setDataRate(RF24_250KBPS); // Set radio rate and channel
  radio.setChannel(100);  // Set the channel (Frequency): 108 = 2.508 GHz (above WiFi)
  radio.setPayloadSize(8);
  // Open a writing and reading pipe on each radio, with opposite addresses
  radio.openWritingPipe(addresses[0]);
  radio.openReadingPipe(1, addresses[1]);

  delay(1000);  // Pause briefly to let everything "settle"

  radio.startListening();  // Start the radio listening for data

  
  digitalWrite(12, LOW);
  digitalWrite(10, LOW);
}

void loop() {
  /****************** Receiving of Radio Transmission ***************************/
  byte received_signal = 0;

  radio.startListening();  // Start the radio listening for data
//  if (radio.available()) {                // Variable for the received timestamp
    while (!radio.available()) {
      delay(1);
   }
   radio.read(&received_signal, sizeof(byte));  // Get the payload
   Serial.println((received_signal));
//  }
//  radio.stopListening();  // Start the radio listening for data

  leftSpeed = 180;
  rightSpeed = 0;
  myservoLeft.attach(9);
  myservoRight.attach(8);

  if (received_signal == 0) {
    myservoLeft.detach();
    myservoRight.detach();
    digitalWrite(12, HIGH);
    digitalWrite(10, LOW);
    go = 0;
    Serial.println("STOP");
  } else if (received_signal == 1) {
      Serial.println("Forward");
      leftSpeed = 180;
      rightSpeed = 0;
      digitalWrite(12, LOW);
      digitalWrite(10, HIGH);
      go = 1;
   } else if (received_signal == 2) {
      Serial.println("Backward");
      leftSpeed = 0;
      rightSpeed = 180;
      digitalWrite(12, HIGH);
      digitalWrite(10, HIGH);
      go = 1;
    } else if (received_signal == 3) {
      Serial.println("Turn Left");
      leftSpeed = 0;
      rightSpeed = 0;
      digitalWrite(12, LOW);
      digitalWrite(10, LOW);
      go = 1;
    } else if (received_signal == 4) {
      Serial.println("Turn Right");
      rightSpeed = 180;
      leftSpeed = 180;
      digitalWrite(12, LOW);
      digitalWrite(10, LOW);
      go = 1;
    } else {
      Serial.println("No Signal Received");
    }
    myservoLeft.write(leftSpeed);
    myservoRight.write(rightSpeed);

  Serial.println("------------New round----------");

  delay(kDelay);
}
