/*
* First RF sketch using nRF24L01+ radios and Arduino (Uno or Micro)
*/

#include <SPI.h>    // Serial Peripheral Interface bus library
#include "RF24.h"   // Library for nRF24L01s

/****************** User Config ***************************/

/***      Set this radio as radio number 0 or 1         ***/
bool radioNumber = 1;

/* Hardware configuration: Set up nRF24L01 radio on SPI bus pins and pins 7 & 8 */

// RF24 radio(7,8);  // For Arduino UNO
RF24 radio(2, 3);  // For Arduino Micro

/* Create a binary address for read/write pipes */
byte addresses[][6] = {"1Node", "2Node"};


bool role = 1; // Local state variable that controls whether this node is sending 1 or receiving 0

void setup() {
//  radio.powerDown();
  Serial.begin(115200);
  radio.begin();

  // Set the Power Level low
  radio.setPALevel(RF24_PA_LOW);

  // Set radio rate and channel
  radio.setDataRate(RF24_250KBPS);

  // Set the channel (Frequency): 108 = 2.508 GHz (above WiFi)
  radio.setChannel(100);

  // Open a writing and reading pipe on each radio, with opposite addresses
  if (radioNumber) {

    radio.openWritingPipe(addresses[1]);
    radio.openReadingPipe(1, addresses[0]);

  } else {

    radio.openWritingPipe(addresses[0]);
    radio.openReadingPipe(1, addresses[1]);

  }

  // Pause briefly to let everything "settle"

  delay(1000);
  Serial.println(F("RF24/examples/GettingStarted"));
  Serial.println(F("*** PRESS 'T' to begin transmitting to the other node"));

  // Start the radio listening for data
  radio.startListening();
}

unsigned long transmitted_signal;

void loop() {
  /****************** Transmitting Role ***************************/
  radio.stopListening();                                    // First, stop listening so we can talk.

  Serial.println(F("Now sending"));

  //if (!radio.write( &start_time, sizeof(unsigned long) )){
  //  Serial.println(F("failed"));
  char inByte = ' ';
  if (Serial.available()) { // only send data back if data has been sent
    char inByte = Serial.read();
    if (inByte == 'w') {
      transmitted_signal = 1; //forward
    } else if (inByte == 'a') {
      transmitted_signal = 3; //left
    } else if (inByte == 's') {
      transmitted_signal = 2; //back
    } else if (inByte == 'd') {
      transmitted_signal = 4; //right
    } else if (inByte == 'c') {
      transmitted_signal = 0;
    }
  }
  Serial.println(transmitted_signal);

  if (!radio.write(&transmitted_signal, sizeof(unsigned long))) {
    Serial.println(F("failed"));
  }

//
//  radio.startListening();                                    // Now, continue listening
//  unsigned long started_waiting_at = micros();               // Set up a timeout period, get the current microseconds
//  boolean timeout = false;                                   // Set up a variable to indicate if a response was received or not

//  while (!radio.available()) {                            // While nothing is received
//    if (micros() - started_waiting_at > 100000 ) {            // If waited longer than 200ms, indicate timeout and exit while loop
//        timeout = true;
//        break;
//    }      
//  }
//
//   
//  if ( timeout ) {                                             // Describe the results
//      Serial.println(F("Failed, response timed out."));
//  } else {
//      unsigned long got_time;                                 // Grab the response, compare, and send to debugging spew
//      radio.read( &got_time, sizeof(unsigned long) );
//      unsigned long end_time = micros();
//
//      // Send to serial port
//      Serial.print(F("Sent "));
//      Serial.print(start_time);
//      Serial.print(F(", Got response "));
//      Serial.print(got_time);
//      Serial.print(F(", Round-trip delay "));
//      Serial.print(end_time-start_time);
//      Serial.println(F(" microseconds"));
//  }

  // Try again 100 ms later

  delay(10);


} // End of Loop


// FIN
