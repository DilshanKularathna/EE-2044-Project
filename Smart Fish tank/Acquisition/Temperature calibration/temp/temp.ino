#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 2
#define PWM_PIN 9  // Must be a PWM capable pin

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(9600);
  sensors.begin();
  pinMode(PWM_PIN, OUTPUT);
}

void loop() {
  sensors.requestTemperatures();
  float tempC = sensors.getTempCByIndex(0);

  if (tempC == DEVICE_DISCONNECTED_C) {
    Serial.println("ERROR: Could not read temperature data");
    return;
  }

  // Convert to voltage (0–5V for 0–100°C)
  float voltage = (tempC * 5.0) / 100.0;
  int pwm_value = voltage * 255.0 / 5.0;

  // Write PWM signal
  analogWrite(PWM_PIN, pwm_value);

  // Display info
  Serial.print("Temp: ");
  Serial.print(tempC, 2);
  Serial.print(" °C | Voltage: ");
  Serial.print(voltage, 2);
  Serial.print(" V | PWM: ");
  Serial.println(pwm_value);

  delay(1000);
}