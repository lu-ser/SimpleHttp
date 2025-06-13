#include <ESP8266WiFi.h> 

#define SSID "my_ssd" 
#define PASSWORD "my_password" 

void setup() { 
	Serial.begin(9600); 	
	Serial.print("Connecting"); 	
	WiFi.begin(SSID, PASSWORD); 
	while (WiFi.status() != WL_CONNECTED) 
	{ 
		delay(500); 
		Serial.print("."); 
	} 
	Serial.println(" connected"); 
	Serial.print("My IP is: "); 
	Serial.println(WiFi.localIP());
} 

void loop() { } 
