//E-paper setup:
//VCC  -> 3V
//GND  -> G
//DIN  -> D7
//CLK  -> D5
//CS   -> D8
//DC   -> D2
//RST  -> D3
//BUSY -> D1


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
const unsigned char Passive_buzzer = D6;
unsigned int server_tries = 0;

Epd epd;


void setup() {
  Serial.begin(115200);
  Serial.print("Starting");
  pinMode (Passive_buzzer, OUTPUT) ;
  noTone(Passive_buzzer);
  beep();
//  if (epd.Init() != 0) {
//    Serial.print("e-Paper init failed");
//    return;
//  }

  epd.ClearFrame();
  WiFi.begin(ssid, password);
}

void beep() {
  tone(Passive_buzzer, 3000);
  delay(100);
  noTone(Passive_buzzer);
  delay(100);
  tone(Passive_buzzer, 4000);
  delay(100);
  noTone(Passive_buzzer);
  delay(100);
  tone(Passive_buzzer, 5000);
  delay(100);
  noTone(Passive_buzzer);
  delay(100);
  noTone(Passive_buzzer);
  delay(5000);
}

void tweet() {
  tone(Passive_buzzer, 2000);
  delay(20);
  for (uint i = 2300; i < 2900; i = i + 4) {
    tone(Passive_buzzer, i);
    delay(1);
  }
  noTone(Passive_buzzer);
  delay(50);
  for (uint i = 2700; i > 2400; i = i - 2) {
    tone(Passive_buzzer, i);
    delay(1);
  }
  tone(Passive_buzzer, 2400);
  delay (100);
  noTone(Passive_buzzer);
}

void get_image() {
  unsigned int image_index = 0;
  for (uint8 lines = 0; lines < 25; lines++) {
    HTTPClient http_image;
    http_image.begin(server + "doodles/image/" + String(lines));
    int httpCode = http_image.GET();
    Serial.println(httpCode);
    if (httpCode > 0) {     
      String payload = http_image.getString();
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
  epd.Reset();
  epd.Init();
  epd.ClearFrame();
  epd.DisplayFrame(IMAGE);
  epd.Sleep();
  tweet();
}

void connection_failed() {
  epd.Reset();
  epd.Init();
  epd.ClearFrame();
  unsigned char image[1500];
  Paint paint(image, 400, 28);    //width should be the multiple of 8 

  paint.Clear(UNCOLORED);
  paint.DrawStringAt(0, 0, "Failed to connect to wifi", &Font12, COLORED);
  epd.SetPartialWindow(paint.GetImage(), 10, 40, paint.GetWidth(), paint.GetHeight());
  epd.DisplayFrame();
}

void server_failed() {
  epd.Reset();
  epd.Init();
  epd.ClearFrame();
  unsigned char image[1500];
  Paint paint(image, 400, 28);    //width should be the multiple of 8 

  paint.Clear(UNCOLORED);
  paint.DrawStringAt(0, 0, "Failed to connect to server", &Font12, COLORED);
  epd.SetPartialWindow(paint.GetImage(), 10, 40, paint.GetWidth(), paint.GetHeight());
  epd.DisplayFrame();
}

void loop() {
  while (WiFi.status() != WL_CONNECTED) {
    WiFi.begin(ssid, password);
    uint8 timeout = 0;
    while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.println("Connecting..");
      if (timeout > 30) {
        Serial.println("Timeout");
        connection_failed();
        break;
      }
      timeout++;
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
  } else {
    if (server_tries >= 3) {
      server_failed();
      server_tries = 0;
    } else {
      server_tries++;
    }
  }
  http.end();
  Serial.println(last_timestamp);

  delay(15000);

}
