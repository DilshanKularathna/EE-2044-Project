const int trigPin = 9;
const int echoPin = 10;

long duration;
float distance_cm;

void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  Serial.begin(9600);
}

void loop() {
  // Clear the TRIG pin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  
  // Send 10µs HIGH pulse to trigger the sensor
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // Read the echo time
  duration = pulseIn(echoPin, HIGH);
  
  // Calculate distance (duration / 2 because of round trip, 0.0343 cm/µs is sound speed)
  distance_cm = duration * 0.0343 / 2;
  
  // Print the result
  Serial.print("Distance: ");
  Serial.print(distance_cm);
  Serial.println(" cm");

  delay(500);
}
