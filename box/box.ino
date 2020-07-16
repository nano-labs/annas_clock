#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <SPI.h>
#include "epd4in2.h"
#include "imagedata.h"
#include "epdpaint.h"

#define COLORED     0
#define UNCOLORED   1

const char* ssid = "Bartcaverna";
const char* password = "bartholomeu";
const String server = "http://10.0.1.4:8000/";
int last_timestamp = 2;
unsigned char IMAGE[15000];

Epd epd;


void setup() {
  Serial.begin(115200);
  if (epd.Init() != 0) {
    Serial.print("e-Paper init failed");
    return;
  }

  epd.ClearFrame();
  WiFi.begin(ssid, password);

}

void get_image() {
  unsigned int image_index = 0;
  for (uint8 lines = 0; lines < 50; lines++) {
    HTTPClient http_image;
    http_image.begin(server + "doodles/image/" + String(lines));
    int httpCode = http_image.GET();
    Serial.println(httpCode);
    if (httpCode > 0) {     
      String payload = http_image.getString();
//      Serial.println(payload);

      int previous_index = -1;
      int next_index = payload.indexOf(",", 0);
      while (next_index != -1) {
        String pix = payload.substring(previous_index + 1, next_index);
        IMAGE[image_index] = pix.toInt();
        image_index++;
        previous_index = next_index;
        next_index = payload.indexOf(",", previous_index + 1);
      }
    
    
    }
    http_image.end();
  }

}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.print("Connecting..");
    }
  }

  HTTPClient http;
  http.begin(server + "doodles/");
  int httpCode = http.GET();
  Serial.println(httpCode);
  if (httpCode > 0) {     
    String payload = http.getString();
    Serial.println(payload);
    if (payload.toInt() > last_timestamp) {
      // download image here
      get_image();
      last_timestamp = payload.toInt();
    }
  }
  http.end();
  Serial.println(last_timestamp);
  delay(5000);

//  // put your main code here, to run repeatedly:
  epd.ClearFrame();
  epd.DisplayFrame(IMAGE);
////  epd.Sleep();
  delay(15000);

}
