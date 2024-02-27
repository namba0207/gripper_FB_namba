const int vol_pin = 14; // 圧力センサ用アナログピン//constは値変更不可
float sensorValue_init;
float sensorValue;
// the setup routine runs once when you press reset:
void setup()
{
  Serial.begin(115200);
  sensorValue_init = analogRead(vol_pin);
}

// the loop function runs over and over again forever
void loop()
{
  // アナログピンの入力値を読み込み。
  sensorValue = analogRead(vol_pin) - sensorValue_init;
  // 読み込んだ状態をシリアルモニターに表示する文。
  Serial.println(sensorValue);
  delay(10);
}
