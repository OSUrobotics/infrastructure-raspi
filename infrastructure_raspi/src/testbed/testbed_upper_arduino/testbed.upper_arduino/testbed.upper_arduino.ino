//Last Updated: Brody Sears - 7/22/2020

#include <AccelStepper.h>
#include <Wire.h>
int I2C_SLAVE2 = 14;

class Object{
  float height;
  int level;
  int arc_position;
  bool cone_bool;

 public:

  void set_Cone_Bool(bool bools){cone_bool = bools;}
  void set_Height(float new_height){height = new_height;}
  void set_Level(int new_level){level = new_level;}
  void set_Arc_Position(int new_Arc_Position){arc_position = new_Arc_Position;}

  int get_Arc_Position(){return arc_position;}
  int get_Level(){return level;}
  float get_Height(){return height;}
  bool get_Cone_Bool(){return cone_bool;}

  Object(float new_height,int new_level, int new_arc_position){height = new_height; level= new_level; arc_position = new_arc_position; cone_bool = false;}
  Object(float new_height, int new_level, int new_arc_position, bool new_bool){height = new_height; level= new_level; arc_position = new_arc_position; cone_bool = new_bool;}
  ~Object(){} 
};
/***************************************************************************************************************************************************************/

//Variable Declarations
volatile byte received = 0;
volatile byte initial_received = 0;
int n = 10;


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


//Height and misc variables
int vertical_level_1_position;
int vertical_level_2_position;
int vertical_level_3_position;
int bed_level;
int object_height_offset;
int inch_to_position_conversion;
int middle_horizontal_position;

//limit switch analog pins
int limitverticalpin = 37;
int limithorizontalpin = 43;
int limitrotationalpin = 47;


//Stepper Declarations
AccelStepper Vertical_Stepper(1,  yPUL, yDIR);
AccelStepper Horizontal_Stepper(1, xPUL, xDIR);
AccelStepper Rotational_Stepper(1, rPUL, rDIR); 


/***************************************************************************************************************************************************************/


void setup() {

    //initialize serial moniter
  Serial.begin(57600);
  Wire.begin(I2C_SLAVE2);
  Wire.setClock( 100000L);

   pinMode(magnetEN, OUTPUT);
  pinMode(magnetIn1, OUTPUT);
  pinMode(magnetIn2, OUTPUT); 

  //initialize limit input pins
  pinMode(limitverticalpin, INPUT);
  pinMode(limithorizontalpin, INPUT);
  pinMode(limitrotationalpin, INPUT);

  Wire.onRequest(requestEvents);
  Wire.onReceive(receiveEvents);

  Horizontal_Stepper.setMaxSpeed(300);
  Horizontal_Stepper.setAcceleration(80);
  Vertical_Stepper.setMaxSpeed(300);
  Vertical_Stepper.setAcceleration(80);
  Rotational_Stepper.setMaxSpeed(300);
  Rotational_Stepper.setAcceleration(80);
}

/***************************************************************************************************************************************************************/

void reach_Limit_Vertical(){
  Vertical_Stepper.setCurrentPosition(0);
    Vertical_Stepper.setMaxSpeed(1000);
  //Serial.println("Started Primery Vertical Shift ");
  for (int i=0; i < 2000; i++){
   Vertical_Stepper.setSpeed(500);
  delay(1);
  //Serial.println(i);
  Vertical_Stepper.runSpeed();
  }
 // Serial.println("Finished Primery Vertical Shift ");

  Vertical_Stepper.setSpeed(-500);
  while(digitalRead(limitverticalpin) == 0){
  Vertical_Stepper.runSpeed();
   }
   Vertical_Stepper.setCurrentPosition(0);

while(Vertical_Stepper.currentPosition() != 8000){
   Vertical_Stepper.setSpeed(500);
   delay(1);
    //Serial.println(Vertical_Stepper.currentPosition());
    Vertical_Stepper.runSpeed();  
  }
   
 }
/***************************************************************************************************************************************************************/

 
void reach_Limit_Horizontal(){
  Horizontal_Stepper.setSpeed(-500);
  while(digitalRead(limithorizontalpin)== 0){
  Horizontal_Stepper.runSpeed();
  }
    Serial.println("Finished contact with Limit Switch");
    Serial.println("Setting Position");

  Horizontal_Stepper.setCurrentPosition(0);
//Serial.println("Moving to Offset");
  while (Horizontal_Stepper.currentPosition() != 450) {
  Horizontal_Stepper.setSpeed(500);
  delay(1);
 // Serial.println(Horizontal_Stepper.currentPosition());
  Horizontal_Stepper.runSpeed();
  }
 }
/***************************************************************************************************************************************************************/

void reach_Limit_Rotational(){
     // Serial.println("Starting Rotation");
  Rotational_Stepper.setSpeed(-400);
  while(digitalRead(limitrotationalpin)==0){
  Rotational_Stepper.runSpeed();
  }
  Rotational_Stepper.setCurrentPosition(0);
}
/********************************************************************/
void go_To_Horizontal_Middle(){
  while (Horizontal_Stepper.currentPosition() != 2400) {
  Horizontal_Stepper.setSpeed(500);
  delay(1);
      Horizontal_Stepper.runSpeed();
 // Serial.println(Horizontal_Stepper.currentPosition());
 }
}
/***************************************************************************************************************************************************************/
int object_Height_To_Position(float height){ return (height * inch_to_position_conversion);}

/***************************************************************************************************************************************************************/
void go_To_Object(Object current_object){
//int height = current_object.get_Height();
//Vertical_Stepper.moveTo(bed_level - object_Height_To_Position(height));
while(Vertical_Stepper.currentPosition() != 6150){
   Vertical_Stepper.setSpeed(-500);
   delay(1);
    //Serial.println(Vertical_Stepper.currentPosition());
    Vertical_Stepper.runSpeed();  
  }
}
/***************************************************************************************************************************************************************/
  void turn_On_Magnet_North(){
  digitalWrite(magnetEN,HIGH);
  digitalWrite(magnetIn1, HIGH);
  digitalWrite(magnetIn2, LOW);
  delay(2000);
  }
/***************************************************************************************************************************************************************/
void go_To_Vertical_Level(Object current_object){
//int level = current_object.get_Level();
//if(level == 1){Vertical_Stepper.moveTo(vertical_level_1_position);}
//else if(level == 2){Vertical_Stepper.moveTo(vertical_level_2_position);}
//else {Vertical_Stepper.moveTo(vertical_level_3_position);}
//
while(Vertical_Stepper.currentPosition() != 16000){
   Vertical_Stepper.setSpeed(500);
   delay(1);
    //Serial.println(Vertical_Stepper.currentPosition());
    Vertical_Stepper.runSpeed();  
  }
}

/***************************************************************************************************************************************************************/
void go_To_Arc(Object current_object){
  int arc_position = current_object.get_Arc_Position();
  Rotational_Stepper.moveTo(arc_position);
}

/***************************************************************************************************************************************************************/
void go_To_Level_Object_Height(Object current_object){
int level = current_object.get_Level();
float height = current_object.get_Height();
if(level==1){Vertical_Stepper.moveTo(vertical_level_1_position + object_height_offset - object_Height_To_Position(height));}
else if(level == 2){Vertical_Stepper.moveTo(vertical_level_2_position + object_height_offset - object_Height_To_Position(height));}
else {Vertical_Stepper.moveTo(vertical_level_3_position + object_height_offset - object_Height_To_Position(height));}


}
/***************************************************************************************************************************************************************/
void turn_On_Magnet_South(){
  digitalWrite(magnetEN,HIGH);
digitalWrite(magnetIn1, LOW);
digitalWrite(magnetIn2, HIGH);
delay(2000);
}

/***************************************************************************************************************************************************************/
void raise_Offset(Object current_object){
  int level = current_object.get_Level();
  if(level == 1){Vertical_Stepper.moveTo(vertical_level_1_position);}
  else if (level == 2){Vertical_Stepper.moveTo(vertical_level_2_position);}
  else{Vertical_Stepper.moveTo(vertical_level_3_position);}
}
/***************************************************************************************************************************************************************/
void turn_Off_Magnet(){
  digitalWrite(magnetEN,HIGH);
digitalWrite(magnetIn1, LOW);
digitalWrite(magnetIn2, LOW);

}
/***************************************************************************************************************************************************************/

void grab_Object(){
Object current_object(4, 1, 1, true);
Serial.println("Attempting Vertical Limit ");
reach_Limit_Vertical();
Serial.println("Reached Vertical Limit ");

Serial.println("Attempting Horizontal Limit ");
reach_Limit_Horizontal();
Serial.println("Reached Horizontal Limit ");

Serial.println("Attempting Rotational Limit ");
reach_Limit_Rotational();
Serial.println("Finished Horizontal Limit ");

Serial.println("Aligning Arm to Center ");
go_To_Horizontal_Middle();
Serial.println("Going to Object");
turn_On_Magnet_North();
go_To_Object(current_object);
Serial.println("Turning on Magnet");
Serial.println("Raising object up");
go_To_Vertical_Level(current_object);
Serial.println("Made it to end of grabObject");
//Horizontal_Stepper.moveTo(0);
//go_To_Arc(current_object);
//go_To_Level_Object_Height(current_object);
//turn_On_Magnet_South();
//raise_Offset(current_object);
//turn_Off_Magnet();

}
/***************************************************************************************************************************************************************/
void go_To_Rotation_Location(){
while (Horizontal_Stepper.currentPosition() != 450) {
  Horizontal_Stepper.setSpeed(-500);
  delay(1);
 // Serial.println(Horizontal_Stepper.currentPosition());
  Horizontal_Stepper.runSpeed();
}
}
/***************************************************************************************************************************************************************/
void go_To_Rotation_Angle(){
while (Rotational_Stepper.currentPosition() != 4675) {
  Rotational_Stepper.setSpeed(500);
  delay(1);
 // Serial.println(Horizontal_Stepper.currentPosition());
  Rotational_Stepper.runSpeed();
}
}
/***************************************************************************************************************************************************************/
void go_To_Horizontal_Position(){
while (Horizontal_Stepper.currentPosition() != 0) {
  Horizontal_Stepper.setSpeed(-500);
  delay(1);
 // Serial.println(Horizontal_Stepper.currentPosition());
  Horizontal_Stepper.runSpeed();
}
}
/***************************************************************************************************************************************************************/
void go_To_Vertical_Position1(){
while (Vertical_Stepper.currentPosition() != 10950) {
  Vertical_Stepper.setSpeed(-500);
  delay(1);
 // Serial.println(Horizontal_Stepper.currentPosition());
  Vertical_Stepper.runSpeed();
}
}
/***************************************************************************************************************************************************************/
void go_To_Vertical_Position2(){
while (Vertical_Stepper.currentPosition() != 15000) {
  Vertical_Stepper.setSpeed(500);
  delay(1);
 // Serial.println(Horizontal_Stepper.currentPosition());
  Vertical_Stepper.runSpeed();
}
}
/***************************************************************************************************************************************************************/
void go_To_Horizontal_Position2(){
while (Horizontal_Stepper.currentPosition() != 1275) {
  Horizontal_Stepper.setSpeed(500);
  delay(1);
 // Serial.println(Horizontal_Stepper.currentPosition());
  Horizontal_Stepper.runSpeed();
}
}
/***************************************************************************************************************************************************************/
void go_To_Rotation_Angle2(){
while (Rotational_Stepper.currentPosition() != 2750) {
  Rotational_Stepper.setSpeed(500);
  delay(1);
 // Serial.println(Horizontal_Stepper.currentPosition());
  Rotational_Stepper.runSpeed();
}
}
/***************************************************************************************************************************************************************/

void go_To_Vertical_Position3(){
while (Vertical_Stepper.currentPosition() != 13100) {
  Vertical_Stepper.setSpeed(-500);
  delay(1);
 // Serial.println(Horizontal_Stepper.currentPosition());
  Vertical_Stepper.runSpeed();
}
}
/***************************************************************************************************************************************************************/
void go_To_Vertical_Position4(){
while (Vertical_Stepper.currentPosition() != 16000) {
  Vertical_Stepper.setSpeed(500);
  delay(1);
 // Serial.println(Horizontal_Stepper.currentPosition());
  Vertical_Stepper.runSpeed();
}
}
/***************************************************************************************************************************************************************/
void go_To_Vertical_Position5(){
while (Vertical_Stepper.currentPosition() != 8050) {
  Vertical_Stepper.setSpeed(-500);
  delay(1);
 // Serial.println(Horizontal_Stepper.currentPosition());
  Vertical_Stepper.runSpeed();
}
}
/***************************************************************************************************************************************************************/
void go_To_Vertical_Position6(){
while (Vertical_Stepper.currentPosition() != 10000) {
  Vertical_Stepper.setSpeed(500);
  delay(1);
 // Serial.println(Horizontal_Stepper.currentPosition());
  Vertical_Stepper.runSpeed();
}
}
/***************************************************************************************************************************************************************/
void go_To_Vertical_Position7(){
while (Vertical_Stepper.currentPosition() != 0) {
  Vertical_Stepper.setSpeed(-500);
  delay(1);
 // Serial.println(Horizontal_Stepper.currentPosition());
  Vertical_Stepper.runSpeed();
}
 }
/***************************************************************************************************************************************************************/
void swap_Object(){

go_To_Rotation_Location();
go_To_Rotation_Angle();
go_To_Horizontal_Position();
go_To_Vertical_Position1();
turn_On_Magnet_South();
delay(2000);
go_To_Vertical_Position2();
go_To_Horizontal_Position2();
turn_On_Magnet_North();
go_To_Vertical_Position3();
delay(2000);
go_To_Vertical_Position4();

go_To_Rotation_Location();
reach_Limit_Rotational();
go_To_Horizontal_Middle();
go_To_Vertical_Position5();
turn_On_Magnet_South();
delay(2000);
go_To_Vertical_Position6();
turn_Off_Magnet();
go_To_Rotation_Location();
go_To_Rotation_Angle2();
go_To_Vertical_Position7();

delay(2000);

}


/***************************************************************************************************************************************************************/

void loop() {
  if(run_var){
    grab_Object();
    delay(50);
    run_var = false;
    end_bool = true;
    //Serial.println("Finished grab object loop");
  }
  if(run_var2){  
    //Serial.println("Entered run_var2") ;
    end_bool = false;
    swap_Object();
    run_var2 = false;
    end_bool = true;
  }
  if (received != 255){
    initial_received = received;
  }
}
/***************************************************************************************************************************************************************/
void requestEvents(){
  switch(initial_received){
    case 2:
      Wire.write(0);
      run_var = true;
      initial_received = 0;
      break;
      
    case 3:
      if (end_bool)
        Wire.write(3);
      else
        Wire.write(0);
      break;
      
    case 4:
      Wire.write(0);
      run_var2 = true;
      initial_received = 0;
      break;
      
    case 5:
      if(end_bool)
        Wire.write(5);
      else
        Wire.write(0);
    break;
    
    default:
      break;
  }
}
/***************************************************************************************************************************************************************/

void receiveEvents(int numBytes){
    Wire.read();
    received = Wire.read();
}
