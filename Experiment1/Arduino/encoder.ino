//エンコーダ割り込み処理
#include <RotaryEncoder.h>

RotaryEncoder encoder(34, 35);
int newpos = 0;//volatileで定義、グローバル関数に近い
void IRAM_ATTR ISR() {
  encoder.tick(); // just call tick() to check the state.
}
void setup() {
  Serial.begin(115200);
  attachInterrupt(34, ISR, CHANGE);
  attachInterrupt(35, ISR, CHANGE);
}

void loop() {
  float newPos = encoder.getPosition();
  Serial.println(newPos);
}