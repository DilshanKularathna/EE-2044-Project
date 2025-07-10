// IN1 to D8, IN2 to GND
#define IN1 8
#define IN2 9

void setup() {
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
}

void loop() {
  digitalWrite(IN1, HIGH); // Pump ON
  digitalWrite(IN2, HIGH); // Pump ON
  delay(5000);
  digitalWrite(IN1, LOW);  // Pump OFF
  digitalWrite(IN2, LOW);  // Pump OFF
  delay(5000);
}
