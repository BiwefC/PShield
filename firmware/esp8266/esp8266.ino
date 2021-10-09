#include <Wire.h>
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

#include "DPS.hpp"

#include "config.hpp"

// #include <string>

#ifndef WIFI_SSID
#define WIFI_SSID             "this_is_your_wifi_ssid"
#endif

#ifndef WIFI_PASSWD
#define WIFI_PASSWD           "this_is_your_wifi_password"
#endif

#ifndef SERVER_API
#define SERVER_API            "this_is_your_server_api"
#endif


const char* ssid = WIFI_SSID;
const char* passwd = WIFI_PASSWD;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  WiFi.begin(ssid, passwd);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  Serial.println(WiFi.localIP());


  Wire.begin();
}

void loop() {
  WiFiClient client;
  HTTPClient http;

  Serial.print("[HTTP] begin...\n");
  // configure traged server and url
  http.begin(client, SERVER_API); //HTTP
  http.addHeader("Content-Type", "application/json");

  Serial.print("[HTTP] POST...\n");

  String str = "{";
  byte reg_list[15] = {REGS_FLAGS, REGS_U_IN, REGS_I_IN, REGS_P_IN,
                      REGS_U_OUT, REGS_I_OUT, REGS_P_OUT,
                      REGS_T_INTAKE, REGS_T_INTERNAL,
                      REGS_FAN_SPEED, REGS_ON_SECONDS,
                      REGS_MAX_P_IN, REGS_MIN_I_IN, REGS_MAX_I_OUT,
                      REGS_FAN_RPM_TARGET};
  for (int i =0; i < 15; i++) {
    if (i != 0) {
      str += ",";
    }
    str += "\"REG";
    str += String(reg_list[i], HEX);
    str += "\":";
    str += read_dsp_mcu(reg_list[i]);
  }
  str += "}";
  int httpCode = http.POST(str);

  // httpCode will be negative on error
  if (httpCode > 0) {
    // HTTP header has been send and Server response header has been handled
    Serial.printf("[HTTP] POST... code: %d\n", httpCode);

    // file found at server
    if (httpCode == HTTP_CODE_OK) {
      const String& payload = http.getString();
      Serial.println("received payload:\n<<");
      Serial.println(payload);
      Serial.println(">>");
    }
  } else {
    Serial.printf("[HTTP] POST... failed, error: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();

  delay(1000);
}
