#include <Wire.h>
#define SLAVE 15 // 0x0f
#define hall_effect_pin 10
#define cone_button_pin 5
#define limit_switch_pin 11
#define encoder_pin 3

/*
 * Author: Ryan Roberts
 * 
 * Turns arduino nano into i2c slave device for the lower reset of grasping mechanism.
 * 
 * Read:
 *  - sends two 8-bit data frames to master in MSB order
 *  - information sent depends on arduino mode (see valid data frame values)
 *  
 *  - possible modes:
 *    - default mode      : doesn't send any data frames to data line ([])
 *    - limit switch mode : sends value of limit switch (0 or 1)
 *    - cone button mode  : sends value of cone button (0 or 1)
 *    - hall effect mode  : sends value of hall effect sensor (0 or 1)
 *    - counting mode     : sends value of encoder counter (0 through 65535)
 * 
 * Write:
 *  - Reads one 8-bit data frame from master
 *  
 *  - valid data frame values:
 *    - 00000011 : sets arduino to limit switch mode  
 *    - 00000100 : sets arduino to cone button mode
 *    - 00000101 : sets arduino to hall effect mode
 *    - 00000110 : sets arduino to counting mode and starts encoder counter
 *    - 00000111 : sets arduino to default mode and resets encoder counter
 *    
 *    - Note: any other data frame value will put arduino in default mode
 */


volatile byte received = 0;
byte data[2];

bool counting = false;
int current_steps = 0;
bool varl = 0;
bool varb = 0;
bool varh = 0;

void setup() {
  Serial.begin(57600);

  pinMode(encoder_pin, INPUT);
  pinMode(limit_switch_pin, INPUT);
  pinMode(cone_button_pin, INPUT);
  pinMode(hall_effect_pin, INPUT);
  
  Wire.begin(SLAVE);
  delay(1000);
  Wire.setClock(100000);
  Wire.onRequest(requestEventHandler);
  Wire.onReceive(receiveEventHandler);

  attachInterrupt(digitalPinToInterrupt(encoder_pin), stepCounter, CHANGE);
}

void loop() {}

void stepCounter(){
  if (counting == true){
    current_steps++;
  }
}

void requestEventHandler(){
  switch(received){
    case 3:
      data[0] = 0;
      data[1] = digitalRead(limit_switch_pin);
      Wire.write(data, 2);
      break;
    case 4:
      data[0] = 0;
      data[1] = digitalRead(cone_button_pin);
      Wire.write(data, 2);
      break;
    case 5: 
      data[0] = 0;
      data[1] = digitalRead(hall_effect_pin);
      Wire.write(data, 2);
      break;
    case 6:
      data[0] = highByte(current_steps);
      data[1] = lowByte(current_steps);
      Wire.write(data, 2);
      break;
    default:
      break;
  }
}

void receiveEventHandler(int num_bytes){
  received = Wire.read();
  if(received == 6){
    counting = true;  
  }
  else if(received == 7){
    counting = false;
    current_steps = 0;
  }
}
