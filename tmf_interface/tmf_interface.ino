

int speed = 20;
int repetition = 40;
int PIN_START = 3;
int PIN_CLOCK = 2;
int PIN_READY = 4;



void readTMF() {

  //trigger the TMF that we are ready to receive parallel data
  digitalWrite(PIN_START, LOW);
  delay(1);

  Serial.write("|");
  
  //generate the pulse signals. The data frame is always 41 byte long
  for(int i=0; i!=repetition; i++) {
    
    digitalWrite(PIN_CLOCK, HIGH);
    while(digitalRead(PIN_READY != 0));
    digitalWrite(PIN_CLOCK, LOW);
    while(digitalRead(PIN_READY != 1));

       
    int val = PINB;
    val = val + 32;
    Serial.write(val);
      
    delayMicroseconds(speed);
  }
  Serial.write("|\n");
  
  digitalWrite(PIN_CLOCK, HIGH);
  digitalWrite(PIN_START, HIGH);
}

void setup() {
  
  pinMode(PIN_CLOCK, OUTPUT);
  pinMode(PIN_START, OUTPUT);
  pinMode(PIN_READY, INPUT_PULLUP);

  //Set input mode on pins 8-13
  DDRB = B11100000;

  //turn on pullup 
   PORTB = PORTB |
      (
        (1 << PORTB0) |  
        (1 << PORTB1) |  
        (1 << PORTB2) |  
        (1 << PORTB3) |
        (1 << PORTB4) 
      );
  
  Serial.begin(115200);
  Serial.println("Starting");
}


void loop() {

  while (Serial.available() > 0) {
    String incomingString = Serial.readString();

    if (incomingString == "r\n") {
      readTMF();
    }    
  }  
}
