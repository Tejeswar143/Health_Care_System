#include <ESP8266WiFi.h>
#include <WiFiClientSecure.h>
#include <Wire.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include "MAX30100_PulseOximeter.h"

// WiFi credentials
#define WIFI_SSID "SSID"
#define WIFI_PASSWORD "Password"

// API server
const char* HOST = "update-data-firebase.onrender.com";
const int PORT = 443;

// API endpoints
const char* ECG_URL = "/ecg-data/";
const char* SPO2_URL = "/sensor-data/";
const char* TEMP_URL = "/temp-data/";

WiFiClientSecure client;

// MAX30100 (Heart Rate & SpO2)
PulseOximeter pox;
uint32_t lastSpo2Time = 0;
#define SPO2_INTERVAL_MS 1 // Reduced interval for more frequent checks
bool spo2DataAvailable = false;
float heartRate = 0.0;
float spo2Value = 0.0;

// ECG
#define ECG_PIN A0
uint32_t lastECGTime = 0;
#define ECG_INTERVAL_MS 1  // Reduced interval for more frequent checks
bool ecgDataAvailable = false;
int ecgValue = 0;

// Temperature (DS18B20 on GPIO0 = D3)
#define ONE_WIRE_BUS 0
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
uint32_t lastTempTime = 0;
#define TEMP_INTERVAL_MS 60000 // 10-second interval
bool tempDataAvailable = false;
float tempC = 0.0;

// Forward declarations
void sendECGData();
void sendSpo2Data();
void sendTemperatureData();
void readECG();
void readSpo2();
void readTemperature();

void onBeatDetected() {
  Serial.println("Beat detected!");
}

void setup() {
  Serial.begin(9600);
  delay(1000);

  pinMode(ECG_PIN, INPUT);
  sensors.begin();

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" connected");

  client.setInsecure();  // Use only for testing HTTPS

  if (!pox.begin()) {
    Serial.println("MAX30100 init failed. Check wiring.");
    while (1);
  }
  pox.setOnBeatDetectedCallback(onBeatDetected);
}

void loop() {
  uint32_t now = millis();

  // Regularly read sensors
  readECG();
  readSpo2();
  readTemperature();

  // Send data to the API as it becomes available
  sendECGData();
  sendSpo2Data();
  sendTemperatureData();
}

void readECG() {
  uint32_t now = millis();
  if (now - lastECGTime >= ECG_INTERVAL_MS) {
    lastECGTime = now;
    ecgValue = analogRead(ECG_PIN);
    ecgDataAvailable = true;
  }
}

void readSpo2() {
  uint32_t now = millis();
  if (now - lastSpo2Time >= SPO2_INTERVAL_MS) {
    lastSpo2Time = now;
    pox.update(); // MUST call pox.update() frequently
    heartRate = pox.getHeartRate();
    spo2Value = pox.getSpO2();
    spo2DataAvailable = true;
  }
}

void readTemperature() {
  uint32_t now = millis();
  if (now - lastTempTime >= TEMP_INTERVAL_MS) {
    lastTempTime = now;
    sensors.requestTemperatures();
    tempC = sensors.getTempCByIndex(0);
    tempDataAvailable = true;
  }
}

void sendECGData() {
  if (ecgDataAvailable) {
    Serial.print("ECG: ");
    Serial.println(ecgValue);
    String payload = "{\"ecg\":" + String(ecgValue) + "}";
    sendToAPI(ECG_URL, payload);
    ecgDataAvailable = false; // Reset flag after sending
  }
}

void sendSpo2Data() {
  if (spo2DataAvailable) {
    Serial.print("HR: ");
    Serial.print(heartRate);
    Serial.print(" / SpO2: ");
    Serial.println(spo2Value);
    if(heartRate > 0 && spo2Value > 0){
      String payload = "{\"heartRate\":" + String(heartRate, 1) + ",\"spo2\":" + String(spo2Value, 1) + "}";
      sendToAPI(SPO2_URL, payload);
    }
    spo2DataAvailable = false; // Reset flag after sending
  }
}

void sendTemperatureData() {
  if (tempDataAvailable) {
    Serial.print("Temperature: ");
    Serial.println(tempC);
    String payload = "{\"temp\":" + String(tempC, 1) + "}";
    sendToAPI(TEMP_URL, payload);
    tempDataAvailable = false; // Reset flag after sending
  }
}

void sendToAPI(String url, String payload) {
  if (client.connect(HOST, PORT)) {
    // client.println("POST " + url + " HTTP/1.1");
    // client.println("Host: " + String(HOST));
    // client.println("Content-Type: application/json");
    // client.println("Connection: close");
    // client.print("Content-Length: ");
    // client.println(payload.length());
    // client.println();
    // client.println(payload);

    // Serial.println("Sent to " + url + ": " + payload);

    while (client.connected()) {
      String line = client.readStringUntil('\n');
      if (line == "\r" || line.length() == 0) break;
    }

    String response = "";
    while (client.available()) {
      response += client.readString();
    }
    // Serial.println("Response:");
    // Serial.println(response);

    client.stop();
  } else {
    Serial.println("Connection to " + url + " failed");
  }
}
