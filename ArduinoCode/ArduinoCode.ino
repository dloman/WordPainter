
#include <Servo.h>

int ledPin = 13; // select the pin for the LED
int TriggerPin = 2;
int ThetaServo,PhiServo, Trigger;
Servo Theta, Phi;
String readString;

int ThetaPos=0,PhiPos=0;

void setup() {
 Serial.begin(9600); // connect to the serial port
 Theta.attach(9);
 Phi.attach(3);
 pinMode(TriggerPin,OUTPUT);
}
  
void loop () 
{
  while (Serial.available()) 
  {
    delay(10);  
    if (Serial.available() >0) 
      {
        char c = Serial.read();
        readString += c;
      }
          
    if (readString.length() >1) 
    {
      ThetaServo = int(readString[0]);
      PhiServo   = int(readString[1]);
      Trigger    = int(readString[2]);
      Theta.write(ThetaServo);
      Phi.write(PhiServo);
      if (Trigger == 0)
      {
        digitalWrite(TriggerPin, LOW);
      }
      if (Trigger == 1)
      {
        digitalWrite(TriggerPin, HIGH);
      }
      delay(15);
      readString="";
      Serial.write('*');
    }
  } 
}
