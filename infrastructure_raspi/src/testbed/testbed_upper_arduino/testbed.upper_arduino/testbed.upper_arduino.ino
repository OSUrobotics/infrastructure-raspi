//Last Updated: Kyle DuFrene - 8/29/2022

#include <AccelStepper.h>
#include <Wire.h>
int I2C_SLAVE2 = 14;

int serialIncomingByte = 0;

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
int xPUL = 2;
int xDIR = 3;
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
int limitverticalpin = A4;
int limithorizontalpin = A0;
int limitrotationalpin = A8;

//Stepper Declarations
AccelStepper Vertical_Stepper(1, yPUL, yDIR);
AccelStepper Horizontal_Stepper(1, xPUL, xDIR);
AccelStepper Rotational_Stepper(1, rPUL, rDIR);

const int speed = 1000;
const int acceleration = 350;

const int vert_speed = 9000;
const int vert_acceleration = 1000;

// 1174 steps per inch for vertical
// 324 steps per inch for horizontal
// with speed = 1000, acceleration = 200

int pos1 = 300; //was 0
const int pos2 = 1635;
const int pos3 = 2800;
const int pos4 = 3800;

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


  pinMode(magnetEN, OUTPUT);
  pinMode(magnetIn1, OUTPUT);
  pinMode(magnetIn2, OUTPUT);

  //initialize limit input pins
  pinMode(limitverticalpin, INPUT_PULLUP);
  pinMode(limithorizontalpin, INPUT_PULLUP);
  pinMode(limitrotationalpin, INPUT_PULLUP);

  Horizontal_Stepper.setMaxSpeed(speed);
  Horizontal_Stepper.setAcceleration(acceleration);
  Vertical_Stepper.setMaxSpeed(vert_speed);
  Vertical_Stepper.setAcceleration(vert_acceleration);
  Rotational_Stepper.setMaxSpeed(speed);
  Rotational_Stepper.setAcceleration(acceleration);
  Serial.println("Prei2c dne");
  Wire.begin(I2C_SLAVE2);
  Wire.setClock( 100000L);
  Wire.onRequest(requestEvents);
  Wire.onReceive(receiveEvents);

  Serial.println("Starting....");
  
  
  initAxis();

  // Uncomment this block to run repeated object swaps
  /*
  while (1) {
      swapObjects(46, 1, 95, 2);
      swapObjects(95, 2, 46, 1);
  }
  */

  // Uncomment this block to run repeated initialization trials
  /*
  while (true){
    initAxis();
  }
  */
  
}

void initAxis() {
  // This function finds the home (0) of each axis.
  
  // go up
  Vertical_Stepper.setCurrentPosition(0);
  move_stepper(&Vertical_Stepper, 5000);

  // Go to home horizontal
  reach_Limit_Horizontal();
  
  // Go to home rotational
  reach_Limit_Rotational();
  
  // Rotation back to resting position
  move_stepper(&Rotational_Stepper, 2500);
  
  // Go to home vertical
  reach_Limit_Vertical();
}

void swapObjects(int object1Height, int position1, int object2Height, int position2) {
  // INPUTS
  // object1Height - height of the object on the cone in mm as an integer
  // position1 - Position to place first object (1-3)
  // object2Height - height of the object on the back to be swapped in mm as an integer
  // position2 - Position to grab the second object (1-3)
  
   
  // Convert object height from mm to stepper steps
  // .032 mm/step
  object1Height = object1Height/.023; //was .032
  object2Height = object2Height/.023;
  
  
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
  move_stepper(&Vertical_Stepper, 8000);
  // go to home horizontal
  move_stepper(&Horizontal_Stepper, 0);
  // go to home rotational
  move_stepper(&Rotational_Stepper, 0);

  // center horizontal 
  move_stepper(&Horizontal_Stepper, 2375);
  // turn on magnet
  turn_On_Magnet_North();
  // go down
  // Distance table to "0" of upper is 34 mm or -1,062
  // Add 100 as safety margin
  move_stepper(&Vertical_Stepper, object1Height - 1730);
  // go up
  move_stepper(&Vertical_Stepper, 15000);

  // go to home horizontal
  move_stepper(&Horizontal_Stepper, 0);
  // swing arm to back
  move_stepper(&Rotational_Stepper, 4770);

  //////////////////////////////////////////////////////////////////////// placeObjectToBack
  // move horizontal to position
  move_stepper(&Horizontal_Stepper, position1);
  // go down
  move_stepper(&Vertical_Stepper, 3000 + object1Height);
  // turn off magnet
  turn_On_Magnet_South();
  // go up
  move_stepper(&Vertical_Stepper, 15000);
  //move_stepper(&Rotational_Stepper, 4770);

  //////////////////////////////////////////////////////////////////////// pickUpObjectFromBack
  // move horizontal to position
  move_stepper(&Horizontal_Stepper, position2);
  // go down
  turn_On_Magnet_North();
  move_stepper(&Vertical_Stepper, 3000 + object2Height);
  // turn on magnet
  
  // go up
  move_stepper(&Vertical_Stepper, 15000);
  //move_stepper(&Rotational_Stepper, 4770);

  // move horizontal to home
  move_stepper(&Horizontal_Stepper, 0);
  // move rotational to home
  move_stepper(&Rotational_Stepper, 0);

  //////////////////////////////////////////////////////////////////////// putObjectBackHome
  // center horizontal
  move_stepper(&Horizontal_Stepper, 2375);
  // go down
  move_stepper(&Vertical_Stepper, object2Height - 1730);
  // turn on magnet
  turn_On_Magnet_South();

  //////////////////////////////////////////////////////////////////////// get out of the way arm
  // go up
  move_stepper(&Vertical_Stepper, 8000);
  turn_Off_Magnet();
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
  int move_speed = -speed;
  stepper->setSpeed(move_speed);
  int readval = analogRead(limitpin);
  // Using analog pin because of previous issues with interferenece 
  while (readval>25){
    stepper->runSpeed();
    readval = analogRead(limitpin);
  }
  stepper->setCurrentPosition(0);
}
/***************************************************************************************************************************************************************/
void reach_Limit_Vertical()
{
  move_To_Limit(&Vertical_Stepper, limitverticalpin);
  Vertical_Stepper.setSpeed(vert_speed);
}
void reach_Limit_Horizontal()
{
  move_To_Limit(&Horizontal_Stepper, limithorizontalpin);
  //Horizontal_Stepper.setSpeed(speed);
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
  analogWrite(magnetEN, 600);
  //digitalWrite(magnetEN, HIGH);
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
