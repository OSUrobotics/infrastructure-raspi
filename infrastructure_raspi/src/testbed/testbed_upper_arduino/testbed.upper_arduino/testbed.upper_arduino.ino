//Last Updated: Brody Sears - 7/22/2020

#include <AccelStepper.h>
#include <Wire.h>
int I2C_SLAVE2 = 14;
/***************************************************************************************************************************************************************/
//Variable Declarations
volatile byte received = 0;
volatile byte initial_received = 0;
int n = 10;
const int num_of_object_locations = 5;
float object_array[num_of_object_locations];
int swap_array[2];
bool data_transfer = false;
float transferred_data = 0;
int swap_data = 0;
int current_location = 0;
bool swap_data_bool = false;
int current_swap_location = 0;

//Stepper Pin Declaration
int yPUL = 8;
int yDIR = 9;
int xPUL = 13;
int xDIR = 12;
int rPUL = 7;
int rDIR = 6;
bool run_var = false;
bool run_var2 = false;

bool end_bool = false;

//Magnet pin Declaration
int magnetIn1 = 28;
int magnetIn2 = 29;
int magnetEN = 11;

//limit switch analog pins
int limitverticalpin = 37;
int limithorizontalpin = 43;
int limitrotationalpin = 47;

//Stepper Declarations
AccelStepper Vertical_Stepper(1, yPUL, yDIR);
AccelStepper Horizontal_Stepper(1, xPUL, xDIR);
AccelStepper Rotational_Stepper(1, rPUL, rDIR);

const int speed = 1000;
const int acceleration = 200;

// 1174 steps per inch for vertical
// 324 steps per inch for horizontal
// with speed = 1000, acceleration = 200

const int pos1 = 0;
const int pos2 = 1275;
const int pos3 = 2550;
const int pos4 = 3825;

const int obj1Height = 4366;
const int obj2Height = 4623;
const int obj3Height = 2201;

long firstObjectHeight = -1;
long firstObjectPos = -1;
long secondObjectHeight = -1;
long secondObjectPos = -1;

union Buffer
{
  unsigned long longNumber;
  byte longBytes[4];
};

/***************************************************************************************************************************************************************/

void setup()
{
  //initialize serial moniter
  Serial.begin(57600);
  Wire.begin(I2C_SLAVE2);
  Wire.setClock(100000L);

  pinMode(magnetEN, OUTPUT);
  pinMode(magnetIn1, OUTPUT);
  pinMode(magnetIn2, OUTPUT);

  //initialize limit input pins
  pinMode(limitverticalpin, INPUT);
  pinMode(limithorizontalpin, INPUT);
  pinMode(limitrotationalpin, INPUT);

  Horizontal_Stepper.setMaxSpeed(speed);
  Horizontal_Stepper.setAcceleration(acceleration);
  Vertical_Stepper.setMaxSpeed(speed);
  Vertical_Stepper.setAcceleration(acceleration);
  Rotational_Stepper.setMaxSpeed(speed);
  Rotational_Stepper.setAcceleration(acceleration);

  Wire.onRequest(requestEvents);
  Wire.onReceive(receiveEvents);

  Serial.println("Starting....");

  initAxis();

  /*while(1) {
    swapObjects(obj3Height, pos2, obj1Height, pos4);
    swapObjects(obj1Height, pos4, obj1Height, pos2);
    }*/

  /*turn_On_Magnet_North();
    Vertical_Stepper.setCurrentPosition(20000);
    Rotational_Stepper.setCurrentPosition(4750);
    reach_Limit_Horizontal();*/

  /*while(1){
    Vertical_Stepper.setCurrentPosition(0);
    Serial.println("Moving to position 1");
    move_stepper(&Vertical_Stepper, 10000);
    Serial.println("Moving to position 2");
    move_stepper(&Vertical_Stepper, 0);
    }*/

  /*reach_Limit_Horizontal();
    while(1) {
    move_stepper(&Horizontal_Stepper, 5000);
    move_stepper(&Horizontal_Stepper, 0);
    }*/
}

void initAxis() {
  // go up
  Vertical_Stepper.setCurrentPosition(0);
  move_stepper(&Vertical_Stepper, 5000);
  // go to home horizontal
  reach_Limit_Horizontal();
  // go to home rotational
  reach_Limit_Rotational();
  // swing arm to resting position
  move_stepper(&Rotational_Stepper, 2500);
  // go to home vertical
  reach_Limit_Vertical();
}

void swapObjects(int object1Height, int position1, int object2Height, int position2) {
  // map positions 1-4 to the actual position steps
  if(position1 == 1) {
    position1 = pos1;
  } else if(position1 == 2) {
    position1 = pos2;
  } else if(position1 == 3) {
    position1 = pos3;
  } else if(position1 == 4) {
    position1 = pos4;
  }

  if(position2 == 1) {
    position2 = pos1;
  } else if(position2 == 2) {
    position2 = pos2;
  } else if(position2 == 3) {
    position2 = pos3;
  } else if(position2 == 4) {
    position2 = pos4;
  }
  
  turn_On_Magnet_North();

  //////////////////////////////////////////////////////////////////////// pickUpObjectFromHome
  // initial positions
  // go up
  move_stepper(&Vertical_Stepper, 10000);
  // go to home horizontal
  move_stepper(&Horizontal_Stepper, 0);
  // go to home rotational
  move_stepper(&Rotational_Stepper, 0);

  // center horizontal
  move_stepper(&Horizontal_Stepper, 2800);
  // turn on magnet
  turn_On_Magnet_North();
  // go down
  move_stepper(&Vertical_Stepper, 3598 + object1Height);
  // go up
  move_stepper(&Vertical_Stepper, 20000);

  // go to home horizontal
  move_stepper(&Horizontal_Stepper, 0);
  // swing arm to back
  move_stepper(&Rotational_Stepper, 4770);

  //////////////////////////////////////////////////////////////////////// placeObjectToBack
  // move horizontal to position
  move_stepper(&Horizontal_Stepper, position1);
  // go down
  move_stepper(&Vertical_Stepper, 8600 + object1Height);
  // turn off magnet
  turn_On_Magnet_South();
  // go up
  move_stepper(&Vertical_Stepper, 20000);

  //////////////////////////////////////////////////////////////////////// pickUpObjectFromBack
  // move horizontal to position
  move_stepper(&Horizontal_Stepper, position2);
  // go down
  move_stepper(&Vertical_Stepper, 8600 + object2Height);
  // turn on magnet
  turn_On_Magnet_North();
  // go up
  move_stepper(&Vertical_Stepper, 20000);

  // move horizontal to home
  move_stepper(&Horizontal_Stepper, 0);
  // move rotational to home
  move_stepper(&Rotational_Stepper, 0);

  //////////////////////////////////////////////////////////////////////// putObjectBackHome
  // center horizontal
  move_stepper(&Horizontal_Stepper, 2800);
  // go down
  move_stepper(&Vertical_Stepper, 3598 + object2Height);
  // turn on magnet
  turn_On_Magnet_South();

  //////////////////////////////////////////////////////////////////////// get out of the way arm
  // go up
  move_stepper(&Vertical_Stepper, 10000);
  // move horizontal to home
  move_stepper(&Horizontal_Stepper, 0);
  // swing arm to resting position
  move_stepper(&Rotational_Stepper, 2500);
}

/***************************************************************************************************************************************************************/
void move_stepper(AccelStepper *stepper, int position_val)
{
  stepper->moveTo(position_val);
  while (stepper->distanceToGo())
  {
    stepper->moveTo(position_val);
    stepper->run();
  }
  stepper->setCurrentPosition(position_val);
}
void move_To_Limit(AccelStepper *stepper, int limitpin)
{
  stepper->setSpeed(-speed);
  while (digitalRead(limitpin) == 0)
    stepper->runSpeed();
  stepper->setCurrentPosition(0);
}
/***************************************************************************************************************************************************************/
void reach_Limit_Vertical()
{
  move_To_Limit(&Vertical_Stepper, limitverticalpin);
  Vertical_Stepper.setSpeed(speed);
}
void reach_Limit_Horizontal()
{
  move_To_Limit(&Horizontal_Stepper, limithorizontalpin);
  Horizontal_Stepper.setSpeed(speed);
  move_stepper(&Horizontal_Stepper, 250);
}
void reach_Limit_Rotational()
{
  move_To_Limit(&Rotational_Stepper, limitrotationalpin);
}
/***************************************************************************************************************************************************************/
void turn_On_Magnet_North()
{
  digitalWrite(magnetEN, HIGH);
  digitalWrite(magnetIn1, HIGH);
  digitalWrite(magnetIn2, LOW);
}
void turn_On_Magnet_South()
{
  digitalWrite(magnetEN, HIGH);
  digitalWrite(magnetIn1, LOW);
  digitalWrite(magnetIn2, HIGH);
}
void turn_Off_Magnet()
{
  digitalWrite(magnetEN, HIGH);
  digitalWrite(magnetIn1, LOW);
  digitalWrite(magnetIn2, LOW);
}


/***************************************************************************************************************************************************************/
bool swap = false;
void loop()
{
  if (swap) {    
    swapObjects(firstObjectHeight, firstObjectPos, secondObjectHeight, secondObjectPos);
    swap = false;
  }
}

/***************************************************************************************************************************************************************/
//// Register a function to be called when a master requests data from this slave device.
//void requestEvents(){
//  switch(initial_received){
//    case 2:
//      Wire.write(0);
//      run_var = true;
//      initial_received = 0;
//      break;
//    case 3:
//      if (end_bool)
//        Wire.write(3);
//      else
//        Wire.write(0);
//      break;
//    case 4:
//      Wire.write(0);
//      run_var2 = true;
//      initial_received = 0;
//      break;
//    case 5:
//      if(end_bool)
//        Wire.write(5);
//      else
//        Wire.write(0);
//      break;
//    case 6:
//      data_transfer = true;
//      break;
//    case 7:
//      current_location++;
//      data_transfer = false;
//      break;
//    case 8:
//      data_transfer = false;
//      break;
//    case 9:
//      transferred_data = 0;
//      break;
//    case 10:
//      swap_data_bool = true;
//    case 11:
//      current_swap_location++;
//      swap_data_bool = false;
//      break;
//    default:
//      break;
//  }
//}

void requestEvents() {
  if(!swap) {
    Wire.write(0xF0);
  } else {
    Wire.write(0);
  }
}

/***************************************************************************************************************************************************************/
// Registers a function to be called when a slave device receives a transmission from a master.
void receiveEvents(int numBytes) {
  Serial.println("Received something");
  Buffer buffer;

  int x = -1;
  while (Wire.available()) { // loop through all
    if (x == -1) {
      x++;
      Wire.read();  // the first byte is always 0, read it so we can skip and read the next byte
      continue;
    }

    byte b = Wire.read(); // receive byte as a integer
    if (b == 0xAA) { // start comand
      Serial.println("Received start command");
      
      firstObjectHeight = -1;
      firstObjectPos = -1;
      secondObjectHeight = -1;
      secondObjectPos = -1;
    } else if (b == 0xFF) { // end command
      Serial.println("Received end command");
      
      Serial.print("firstObjectHeight: ");
      Serial.println(firstObjectHeight);
      Serial.print("firstObjectPos: ");
      Serial.println(firstObjectPos);
      Serial.print("secondObjectHeight: ");
      Serial.println(secondObjectHeight);
      Serial.print("secondObjectPos: ");
      Serial.println(secondObjectPos);

      swap = true;
    } else if (x == 1) {
      Buffer buffer;
      buffer.longBytes[0] = b;
      buffer.longBytes[1] = Wire.read();
      buffer.longBytes[2] = Wire.read();
      buffer.longBytes[3] = Wire.read();
      firstObjectHeight = buffer.longNumber;
    } else if (x == 2) {
      firstObjectPos = b;
    } else if (x == 3) {
      Buffer buffer;
      buffer.longBytes[0] = b;
      buffer.longBytes[1] = Wire.read();
      buffer.longBytes[2] = Wire.read();
      buffer.longBytes[3] = Wire.read();
      secondObjectHeight = buffer.longNumber;
    } else if (x == 4) {
      secondObjectPos = b;
    }

    //      buffer.longBytes[3] = Wire.read();
    //      Serial.println(buffer.longBytes[3], HEX);
    //      buffer.longBytes[2] = Wire.read();
    //      Serial.println(buffer.longBytes[2], HEX);
    //      buffer.longBytes[1] = Wire.read();
    //      Serial.println(buffer.longBytes[1], HEX);
    //      buffer.longBytes[0] = Wire.read();
    //      Serial.println(buffer.longBytes[0], HEX);
    //
    //      Serial.println(buffer.longNumber, HEX);
    //      Serial.println(buffer.longNumber);

    x++;
  }
}