// 把持すると相方PID
#include <RotaryEncoder.h>
// ロードセル
volatile int loadcell_rec = 127;
// アナログピン34,13 モーター->マイコン エンコーダー用
const int ENCODER_PIN_1 = 32;
const int ENCODER_PIN_2 = 33;
const int ENCODER_PIN_3 = 34;
const int ENCODER_PIN_4 = 35;
// アナログピン25,26 マイコン->モータ モータ制御用
const int DAC_PIN_1 = 26;
const int DAC_PIN_2 = 25;
// ESP32並列処理
volatile int vol1_int = 127;
volatile int vol2_int = 127;
volatile float volt = 127; // Lowpass-fft用
// PID
volatile float newpos1 = 0;
volatile float newpos2 = 0;
volatile int newpos1_int = 0;
volatile int newpos2_int = 0;
// newpos1把持位置
volatile int grippos_int = 0;
volatile int flag = 0;

float preP1 = 0;
float preP2 = 0;
float Kd1 = 0.005; // 発振用ダンパ係数
float Kp2 = 0.08;  // PIDをゆるく
float Kd2 = 0.005;
float dt = 0.005;
float P1;
float P2;
float D1;
float D2;
float a = 0.9; // Lowpass-filter用
// float a = 1;//反力127固定
// float a = 0;//filter無し
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
    newpos1 = encoder1.getPosition();
    newpos2 = encoder2.getPosition();
    newpos1_int = int(newpos1 * 2800 / 2300);
    newpos2_int = int(newpos2);
    if (Serial.available())
    {
      loadcell_rec = Serial.read();
    }
    // 掴み始めの位置記録・離し始めのフラグ回収130は要調整
    if (loadcell_rec >= 130 && flag == 0)
    {
      grippos_int = newpos1_int;
      flag = 1;
    }
    if (loadcell_rec < 130)
    {
      flag = 0;
    }
    // PID
    D1 = (preP1 - newpos1_int) / dt;
    preP1 = newpos1_int;
    if (flag == 0)
    {
      P2 = 0 - newpos2_int;
      D2 = (P2 - preP2) / dt;
      preP2 = P2;
    }
    else
    {
      P2 = (newpos1_int - grippos_int) * (2800 - 0) / (2800 - grippos_int) - newpos2_int; // かっこ後二つは傾き
      D2 = (P2 - preP2) / dt;
      preP2 = P2;
    }
    // lowpassfft
    volt = a * volt + (1 - a) * loadcell_rec;
    vol1_int = int(volt + Kd1 * D1);
    vol2_int = int(Kp2 * P2 + Kd2 * D2 + 127);
    if (vol1_int > 255)
    {
      vol1_int = 255;
    }
    else if (vol1_int < 0)
    {
      vol1_int = 0;
    }
    if (vol2_int > 255)
    {
      vol2_int = 255;
    }
    else if (vol2_int < 0)
    {
      vol2_int = 0;
    }
    dacWrite(DAC_PIN_1, vol1_int);
    dacWrite(DAC_PIN_2, vol2_int);
    delay(5);
  }
}

void setup()
{
  pinMode(ENCODER_PIN_1, INPUT_PULLUP);
  pinMode(ENCODER_PIN_2, INPUT_PULLUP);
  pinMode(ENCODER_PIN_3, INPUT_PULLUP);
  pinMode(ENCODER_PIN_4, INPUT_PULLUP);
  pinMode(DAC_PIN_1, OUTPUT);
  pinMode(DAC_PIN_2, OUTPUT);
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
  Serial.print(-newpos2_int);
  Serial.print(',');
  Serial.print(vol1_int);
  Serial.print(',');
  Serial.println(vol2_int);
  delay(5); // 200Hz
}
