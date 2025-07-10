#include <WiFi.h>
#include <WebServer.h>
#include <Preferences.h>
#include <PubSubClient.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ================== OLED Config ==================
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

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
const char* topic_temp = "tank/temperature";
const char* topic_ph = "tank/ph";
const char* topic_anomaly = "tank/anomaly";

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

// ================== OLED Drawing ==================
void drawDisplay() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Smart Fish Tank");

  display.setCursor(0, 16);
  display.print("Temp: ");
  display.print(temperature);
  display.println(" C");

  display.setCursor(0, 28);
  display.print("pH:   ");
  display.println(ph);

  display.setCursor(0, 40);
  display.print("Anomaly: ");
  display.println(anomaly);

  display.display();
}

// ================== Setup ==================
void setup() {
  pinMode(LED_PIN, OUTPUT);
  pinMode(RESET_BUTTON, INPUT_PULLUP);
  digitalWrite(LED_PIN, LOW);

  Serial.begin(115200);
  delay(1000);
  Serial.println("ESP32 Booting...");

  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
  display.display();
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
