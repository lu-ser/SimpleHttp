#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// Configurazione WiFi
const char* ssid = "N10";          // Sostituisci con il nome della tua rete WiFi
const char* password = "12345678";   // Sostituisci con la password della tua rete WiFi

// Configurazione MQTT
const char* mqtt_server = "broker.mqttdashboard.com";
const int mqtt_port = 1883;
const char* mqtt_user = "";                 // Lascia vuoto per broker pubblico
const char* mqtt_password = "";             // Lascia vuoto per broker pubblico

// Topic MQTT
const char* temp_topic = "esp8266_test_lab_telecomunicazioni/temperatura";
const char* hum_topic = "esp8266_test_lab_telecomunicazioni/umidita";

// Client WiFi e MQTT
WiFiClient espClient;
PubSubClient client(espClient);

// Variabili per i dati
float temperatura;
float umidita;
unsigned long ultimoInvio = 0;
const long intervallo = 5000;  // Invia dati ogni 5 secondi

void setup() {
  Serial.begin(115200);
  delay(10);
  
  // Connessione WiFi
  Serial.println();
  Serial.print("Connessione a ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.println("WiFi connesso!");
  Serial.print("Indirizzo IP: ");
  Serial.println(WiFi.localIP());
  
  // Configurazione MQTT
  client.setServer(mqtt_server, mqtt_port);
  
  // Inizializza il generatore random
  randomSeed(analogRead(0));
}

void reconnectMQTT() {
  while (!client.connected()) {
    Serial.print("Tentativo connessione MQTT...");
    
    // Crea un client ID casuale
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str(), mqtt_user, mqtt_password)) {
      Serial.println("connesso!");
    } else {
      Serial.print("fallito, rc=");
      Serial.print(client.state());
      Serial.println(" riprovo tra 5 secondi");
      delay(5000);
    }
  }
}

void inviaDati() {
  // Genera dati random
  temperatura = random(150, 350) / 10.0;  // Temperatura tra 15.0 e 35.0 °C
  umidita = random(300, 800) / 10.0;      // Umidità tra 30.0 e 80.0 %
  
  // Converti in stringhe
  String tempString = String(temperatura, 1);
  String humString = String(umidita, 1);
  
  // Pubblica i dati
  if (client.publish(temp_topic, tempString.c_str())) {
    Serial.print("Temperatura inviata: ");
    Serial.print(temperatura);
    Serial.println(" °C");
  }
  
  if (client.publish(hum_topic, humString.c_str())) {
    Serial.print("Umidità inviata: ");
    Serial.print(umidita);
    Serial.println(" %");
  }
  
  Serial.println("---");
}

void loop() {
  // Verifica connessione MQTT
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();
  
  // Invia dati ogni 5 secondi
  unsigned long adesso = millis();
  if (adesso - ultimoInvio > intervallo) {
    ultimoInvio = adesso;
    inviaDati();
  }
  
  delay(100);
}