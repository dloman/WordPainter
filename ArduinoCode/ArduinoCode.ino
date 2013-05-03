// Arduino Code:
// Below, 'character' types are defined:  They hold 1 byte of data, 256 values.
// A char can be interpreted as a small number (0-255) or as a member of the
// ASCII set (which is what we deal with below).  Characters expressed as
// ASCII are surrounded in single-quotes, like '5'.
// Thus each char has a corresponding numeric value can thus be tested against.

int ledPin = 13; // select the pin for the LED
int TestPin = 2;
int ThetaServo,PhiServo, Trigger;
Servo Theta, Phi;
String readString;

int ThetaPos=0,PhiPos=0;

void setup() {
 pinMode(ledPin,OUTPUT);   // declare the LED's pin as output
 pinMode(TestPin,OUTPUT); 
 Serial.begin(9600);        // connect to the serial port
}


void WriteTheta(int Theta)
{
  

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
      delay(15);
      readString="";
      Serial.write('*')
    }
  } 
}
