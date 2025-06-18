#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// Configurazione WiFi
const char* ssid = "N10";
const char* password = "12345678";

// Configurazione MQTT
const char* mqtt_server = "broker.mqttdashboard.com";

// Topic MQTT
const char* temp_topic = "esp8266_test_lab_telecomunicazioni/temperatura";
const char* hum_topic = "esp8266_test_lab_telecomunicazioni/umidita";

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  
  // Connessione WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connesso");
  
  // Configurazione MQTT
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void callback(char* topic, byte* payload, unsigned int length) {
  String messaggio = "";
  for (int i = 0; i < length; i++) {
    messaggio += (char)payload[i];
  }
  
  if (String(topic) == temp_topic) {
    Serial.print("Temperatura: ");
    Serial.println(messaggio);
  } 
  else if (String(topic) == hum_topic) {
    Serial.print("Umidita: ");
    Serial.println(messaggio);
  }
}

void reconnectMQTT() {
  while (!client.connected()) {
    if (client.connect("ESP8266Subscriber")) {
      client.subscribe(temp_topic);
      client.subscribe(hum_topic);
      Serial.println("MQTT connesso");
    } else {
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();
}