#include <WiFi.h>
#include <WebServer.h>
#include <Preferences.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>  // Add this library

// ================== LCD Config ==================
LiquidCrystal_I2C lcd(0x27, 16, 2); // Adjust address (0x27 or 0x3F) and size (16x2 or 20x4)

// ================== Pin Config ==================
#define LED_PIN 2
#define RESET_BUTTON 0

// ================== Wi-Fi Config ==================
Preferences preferences;
WebServer server(80);
const char* ap_ssid = "ESP32_Config";
const char* ap_password = "12345678";
bool apMode = false;

// ================== MQTT Config ==================
WiFiClient espClient;
PubSubClient client(espClient);
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;

// ================== MQTT Topics ==================
const char* topic_temp = "tank/temperature/EE2044/g11";
const char* topic_ph = "tank/ph/EE2044/g11";
const char* topic_anomaly = "tank/anomaly/EE2044/g11";

// ================== Data Variables ==================
String temperature = "--";
String ph = "--";
String anomaly = "Unknown";

// ================== Function Prototypes ==================
void drawDisplay();
void connectToMQTT();
bool connectToWiFi();
void startAPMode();
void checkForReset();

// ================== MQTT Callback ==================
void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) message += (char)payload[i];

  if (String(topic) == topic_temp) {
    temperature = message;
  } else if (String(topic) == topic_ph) {
    ph = message;
  } else if (String(topic) == topic_anomaly) {
    anomaly = (message == "true") ? "YES" : "NO";
  }

  drawDisplay();
}

// ================== LCD Drawing ==================
void drawDisplay() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("T:");
  lcd.print(temperature);
  lcd.print("C ");

  lcd.print("pH:");
  lcd.print(ph);

  lcd.setCursor(0, 1);
  lcd.print("Anomaly:");
  lcd.print(anomaly);
}

// ================== Setup ==================
void setup() {
  pinMode(LED_PIN, OUTPUT);
  pinMode(RESET_BUTTON, INPUT_PULLUP);
  digitalWrite(LED_PIN, LOW);

  Serial.begin(115200);
  delay(1000);
  Serial.println("ESP32 Booting...");

  lcd.init();
  lcd.backlight();
  drawDisplay();

  checkForReset();

  if (!connectToWiFi()) {
    startAPMode();
  }

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

// ================== Loop ==================
void loop() {
  // Handle blinking LED
  static unsigned long lastBlink = 0;
  static bool ledState = false;
  if (millis() - lastBlink >= 1000) {
    ledState = !ledState;
    digitalWrite(LED_PIN, ledState);
    lastBlink = millis();
  }

  // Handle web config in AP mode
  if (apMode) {
    server.handleClient();
    return;
  }

  // Wi-Fi check
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi Lost. Restarting...");
    ESP.restart();
  }

  // MQTT check
  if (!client.connected()) {
    connectToMQTT();
  }

  client.loop();
}

// ================== Connect to MQTT ==================
void connectToMQTT() {
  while (!client.connected()) {
    Serial.println("Connecting to MQTT...");
    if (client.connect("ESP32FishTank")) {
      Serial.println("Connected to MQTT broker.");
      client.subscribe(topic_temp);
      client.subscribe(topic_ph);
      client.subscribe(topic_anomaly);
    } else {
      Serial.print("MQTT failed. Retry in 2s. Code: ");
      Serial.println(client.state());
      delay(2000);
    }
  }
}

// ================== Wi-Fi Functions ==================
bool connectToWiFi() {
  preferences.begin("wifi", true);
  String ssid = preferences.getString("ssid", "");
  String password = preferences.getString("password", "");
  preferences.end();

  Serial.print("Connecting to SSID: ");
  Serial.println(ssid);

  if (ssid.length() < 1) return false;

  WiFi.begin(ssid.c_str(), password.c_str());

  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 10000) {
    Serial.print(".");
    delay(500);
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConnected to Wi-Fi");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
    return true;
  } else {
    Serial.println("\nWi-Fi connection failed.");
    return false;
  }
}

void startAPMode() {
  apMode = true;
  WiFi.softAP(ap_ssid, ap_password);
  Serial.print("AP IP address: ");
  Serial.println(WiFi.softAPIP());

  server.on("/", HTTP_GET, []() {
    String html = "<h2>ESP32 Wi-Fi Config</h2><form method='POST' action='/save'>"
                  "SSID: <input name='ssid'><br>"
                  "Password: <input name='password' type='password'><br>"
                  "<input type='submit' value='Save'></form>";
    server.send(200, "text/html", html);
  });

  server.on("/save", HTTP_POST, []() {
    String ssid = server.arg("ssid");
    String password = server.arg("password");

    preferences.begin("wifi", false);
    preferences.putString("ssid", ssid);
    preferences.putString("password", password);
    preferences.end();

    server.send(200, "text/html", "Saved! Rebooting...");
    delay(2000);
    ESP.restart();
  });

  server.begin();
}

void checkForReset() {
  if (digitalRead(RESET_BUTTON) == LOW) {
    Serial.println("Reset button pressed. Clearing Wi-Fi...");
    preferences.begin("wifi", false);
    preferences.clear();
    preferences.end();
    delay(1000);
    ESP.restart();
  }
}
