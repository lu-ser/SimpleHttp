/*
 * NodeMCU ESP8266 - Temperatura Semplice
 * Invia temperatura simulata ogni 10 secondi
 */

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>

// CONFIGURAZIONE - CAMBIA QUESTI VALORI
const char* ssid = "TUO_WIFI";
const char* password = "TUA_PASSWORD";
const char* server = "https://simplehttp-server.onrender.com/temperature";

void setup() {
  Serial.begin(115200);
  
  // Connetti WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  
  Serial.println("\nWiFi connesso!");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Temperatura simulata (20-30 gradi)
  float temp = 20 + random(0, 100) / 10.0;
  
  // Invia al server
  WiFiClient client;
  HTTPClient http;
  
  http.begin(client, server);
  http.addHeader("Content-Type", "application/json");
  
  String json = "{\"valore\":" + String(temp) + 
                ",\"sensore\":\"ESP8266_01\"" +
                ",\"posizione\":\"Aula\"}";
  
  int response = http.POST(json);
  
  Serial.println("Temp: " + String(temp) + "°C - Risposta: " + String(response));
  
  http.end();
  
  // Aspetta 10 secondi
  delay(10000);
}