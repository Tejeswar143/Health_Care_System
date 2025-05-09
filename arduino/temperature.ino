#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ESP8266WiFi.h>
#include <FirebaseESP8266.h>
#include "MAX30100_PulseOximeter.h"
#include <OneWire.h>
#include <DallasTemperature.h>

// WiFi credentials
const char* ssid = "Slayer";
const char* password = "Haseeb@1999";

// Firebase credentials
#define FIREBASE_HOST "your-project-id.firebaseio.com"
#define FIREBASE_AUTH "your-database-secret-or-token"

FirebaseData firebaseData;

// Pins and Objects
#define BUZZER  16
#define ONE_WIRE_BUS 2
#define ECG_PIN A0

LiquidCrystal_I2C lcd(0x27, 16, 2);
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
PulseOximeter pox;

// Timing
unsigned long lastSendTime = 0;
const unsigned long sendInterval = 16000;
const unsigned long lcdUpdateInterval = 1000;
unsigned long lastLcdUpdate = 0;

// Variables
float temperature;
float heartRate;
float spo2;
int ecgValue;

// Function to handle abnormal values
void handleAbnormal() {
  digitalWrite(BUZZER, HIGH);
  Serial.println("Abnormal Condition Detected!");
}

// Function to handle normal values
void handleNormal() {
  digitalWrite(BUZZER, LOW);
  Serial.println("Normal Condition");
}

// WiFi connection check
void checkWiFi() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi Disconnected!");
  }
}

void setup() {
  // Initialize serial and peripherals
  Serial.begin(9600);
  lcd.begin();
  lcd.backlight();
  pinMode(BUZZER, OUTPUT);
  digitalWrite(BUZZER, LOW);

  // Display WiFi connecting message on LCD
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Connecting to");
  lcd.setCursor(0, 1);
  lcd.print("WiFi...");

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");

  // Clear LCD and display connection status
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("WiFi Connected");
  delay(2000);
  lcd.clear();

  // Initialize Firebase
  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);
  Firebase.reconnectWiFi(true);

  // Initialize sensors
  sensors.begin();
  pox.begin();
}

void loop() {
  // Check WiFi status
  checkWiFi();

  // Read heart rate and SpO2 from MAX30100
  pox.update();

  // Read temperature from DS18B20
  sensors.setWaitForConversion(true);
  sensors.requestTemperatures();
  temperature = sensors.getTempCByIndex(0);
  sensors.setWaitForConversion(false);

  // Read heart rate and SpO2
  heartRate = pox.getHeartRate();
  spo2 = pox.getSpO2();

  // Read ECG sensor
  ecgValue = analogRead(ECG_PIN);

  // Check for abnormal conditions
  if (temperature > 40.1 || temperature < 35.2 || heartRate < 60 || heartRate > 100 || spo2 < 93) {
    handleAbnormal();
  } else {
    handleNormal();
  }

  // Update LCD periodically
  if (millis() - lastLcdUpdate >= lcdUpdateInterval) {
    lastLcdUpdate = millis();
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("T:");
    lcd.print(temperature, 1);
    lcd.print(" S:");
    lcd.print(spo2, 0);
    lcd.print("%");

    lcd.setCursor(0, 1);
    lcd.print("H:");
    lcd.print(heartRate, 1);
    lcd.print(" EC:");
    lcd.print(ecgValue);
  }

  // Send data to Firebase periodically
  if (millis() - lastSendTime >= sendInterval && WiFi.status() == WL_CONNECTED) {
    lastSendTime = millis();

    String path = "/HealthData";
    
    Firebase.setFloat(firebaseData, path + "/temperature", temperature);
    Firebase.setFloat(firebaseData, path + "/heartRate", heartRate);
    Firebase.setFloat(firebaseData, path + "/spo2", spo2);
    Firebase.setInt(firebaseData, path + "/ecg", ecgValue);

    if (firebaseData.httpCode() != 200) {
      Serial.print("Error sending data: ");
      Serial.println(firebaseData.errorReason());
    }
  }
}
