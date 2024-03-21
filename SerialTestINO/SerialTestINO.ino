#include "M5Stack.h"

void setup() {
  M5.begin();

  Serial.begin(9600);

  M5.Lcd.setTextSize(1);
  M5.Lcd.setTextDatum(4);
  M5.Lcd.println("Initialize");
}

void loop() {
  static String receivedData = "";

  while (Serial.available() > 0) {
    char receivedChar = Serial.read();
    if (receivedChar == '\n') {
      int commmaIndex = receivedData.indexOf(',');
      if (commmaIndex != -1) {
        int data_1 = receivedData.substring(0, commmaIndex).toInt();
        int data_2 = receivedData.substring(commmaIndex, +1).toInt();

        if (data_1 == 1) {
          M5.Lcd.clear(BLUE);
        } else {
          M5.Lcd.clear(BLACK);
        }
      }
      receivedData = "";
    } else {
      receivedData += receivedChar;
    }
  }
}
