// step1B用
#include <RotaryEncoder.h>
// ロードセル
volatile int loadcell_rec = 0;
// アナログピン34,13 モーター->マイコン エンコーダー用
const int ENCODER_PIN_3 = 34;
const int ENCODER_PIN_4 = 35;
// アナログピン25,26 マイコン->モータ モータ制御用
const int DAC_PIN_1 = 26;
const int DAC_PIN_2 = 25;
// ESP32並列処理
volatile int vol1_int = 127;
volatile int vol2_int = 127;
volatile float volt = 0; // Lowpass-fft用
// PID
volatile float newpos2 = 0;
volatile int newpos1_int = 0;
volatile int newpos2_int = 0;
// newpos1把持位置
volatile int grippos_int = 0;
volatile int flag = 0;

float preP2 = 0;
float Kp2 = 0.15; // PIDをゆるく
float Kd2 = 0.005;
float dt = 0.005;
float P2 = 0;
float D2 = 0;
float a = 0.96; // Lowpass-filter用

RotaryEncoder encoder2(ENCODER_PIN_3, ENCODER_PIN_4, RotaryEncoder::LatchMode::TWO03);

void IRAM_ATTR ISR()
{
  encoder2.tick();
}

void subProcess(void *pvParameters)
{ // 並列処理の関数
  while (1)
  {
    if (Serial.available())
    {
      //      loadcell_rec = Serial.read();
      String data = Serial.readStringUntil('\n');
      if (data.toInt() >= 100)
      {
        loadcell_rec = data.toInt() - 100;
      }
    }

    volt = a * volt + (1 - a) * loadcell_rec;
    newpos2 = encoder2.getPosition();
    newpos1_int = int(-volt * 2300 / 255);
    newpos2_int = int(newpos2 * 2300 / 2800);
    P2 = newpos1_int - newpos2_int;
    D2 = (P2 - preP2) / dt;
    preP2 = P2;
    vol1_int = 127;
    vol2_int = int(Kp2 * P2 + Kd2 * D2 + 127);
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
  pinMode(ENCODER_PIN_3, INPUT_PULLUP);
  pinMode(ENCODER_PIN_4, INPUT_PULLUP);
  pinMode(DAC_PIN_1, OUTPUT);
  pinMode(DAC_PIN_2, OUTPUT);
  Serial.begin(115200);
  Serial.println("SimplePollRotator example for the RotaryEncoder library.");
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
  Serial.println(vol2_int);
  delay(5); // 200Hz
}
// エンコーダリセットすると一回目は不都合になる

// // step1B用
// #include <RotaryEncoder.h>
// // ロードセル
// volatile int loadcell_rec = 0;
// // アナログピン34,13 モーター->マイコン エンコーダー用
// const int ENCODER_PIN_3 = 34;
// const int ENCODER_PIN_4 = 35;
// // アナログピン25,26 マイコン->モータ モータ制御用
// const int DAC_PIN_1 = 26;
// const int DAC_PIN_2 = 25;
// // ESP32並列処理
// volatile int vol1_int = 127;
// volatile int vol2_int = 127;
// volatile float volt = 0; // Lowpass-fft用
// // PID
// volatile float newpos2 = 0;
// volatile int newpos1_int = 0;
// volatile int newpos2_int = 0;
// // newpos1把持位置
// volatile int grippos_int = 0;
// volatile int flag = 0;

// float preP2 = 0;
// float Kp2 = 0.15; // PIDをゆるく
// float Kd2 = 0.005;
// float dt = 0.01;
// float P2 = 0;
// float D2 = 0;
// float a = 0.96; // Lowpass-filter用

// RotaryEncoder encoder2(ENCODER_PIN_3, ENCODER_PIN_4, RotaryEncoder::LatchMode::TWO03);

// void IRAM_ATTR ISR()
// {
//   encoder2.tick();
// }

// void subProcess(void *pvParameters)
// { // 並列処理の関数
//   while (1)
//   {
//     if (Serial.available())
//     {
//       loadcell_rec = Serial.read();
//     }

//     volt = a * volt + (1 - a) * loadcell_rec;
//     newpos2 = encoder2.getPosition();
//     newpos1_int = int(-volt * 2300 / 255);
//     newpos2_int = int(newpos2 * 2300 / 2800);
//     P2 = newpos1_int - newpos2_int;
//     D2 = (P2 - preP2) / dt;
//     preP2 = P2;
//     vol1_int = 127;
//     vol2_int = int(Kp2 * P2 + Kd2 * D2 + 127);
//     if (vol2_int > 255)
//     {
//       vol2_int = 255;
//     }
//     else if (vol2_int < 0)
//     {
//       vol2_int = 0;
//     }
//     dacWrite(DAC_PIN_1, vol1_int);
//     dacWrite(DAC_PIN_2, vol2_int);
//     delay(10);
//   }
// }

// void setup()
// {
//   pinMode(ENCODER_PIN_3, INPUT_PULLUP);
//   pinMode(ENCODER_PIN_4, INPUT_PULLUP);
//   pinMode(DAC_PIN_1, OUTPUT);
//   pinMode(DAC_PIN_2, OUTPUT);
//   Serial.begin(115200);
//   Serial.println("SimplePollRotator example for the RotaryEncoder library.");
//   attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_3), ISR, CHANGE);
//   attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_4), ISR, CHANGE);
//   xTaskCreatePinnedToCore(subProcess, "subProcess", 4096, NULL, 1, NULL, 0); // 並列処理
// }

// void loop()
// {
//   Serial.print(-newpos1_int);
//   Serial.print(',');
//   Serial.print(-newpos2_int);
//   Serial.print(',');
//   Serial.println(vol2_int);
//   delay(10); // 200Hz
// }
// // エンコーダリセットすると一回目は不都合になる
