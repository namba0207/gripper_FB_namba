// 把持力フィードバック//1205
#include <RotaryEncoder.h>
// アナログピン34,13 モーター->マイコン エンコーダー用
const int ENCODER_PIN_1 = 32;
const int ENCODER_PIN_2 = 33;
const int ENCODER_PIN_3 = 34;
const int ENCODER_PIN_4 = 35;
// PID
volatile int newpos1_int = 0;
volatile int newpos2_int = 0;

RotaryEncoder encoder1(ENCODER_PIN_1, ENCODER_PIN_2, RotaryEncoder::LatchMode::TWO03);
RotaryEncoder encoder2(ENCODER_PIN_3, ENCODER_PIN_4, RotaryEncoder::LatchMode::TWO03);

void IRAM_ATTR ISR()
{
  encoder1.tick();
  encoder2.tick();
}

void subProcess(void *pvParameters)
{ // 並列処理の関数
  while (1)
  {
    newpos1_int = (int)encoder1.getPosition();
    newpos2_int = (int)encoder2.getPosition();
    delay(5);
  }
}

void setup()
{
  pinMode(ENCODER_PIN_1, INPUT_PULLUP);
  pinMode(ENCODER_PIN_2, INPUT_PULLUP);
  pinMode(ENCODER_PIN_3, INPUT_PULLUP);
  pinMode(ENCODER_PIN_4, INPUT_PULLUP);
  Serial.begin(115200);
  Serial.println("SimplePollRotator example for the RotaryEncoder library.");
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_1), ISR, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_2), ISR, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_3), ISR, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_4), ISR, CHANGE);
  xTaskCreatePinnedToCore(subProcess, "subProcess", 4096, NULL, 1, NULL, 0); // 並列処理
}

void loop()
{
  Serial.print(-newpos1_int);
  Serial.print(',');
  Serial.println(-newpos2_int);
  delay(5); // 200Hz
}
