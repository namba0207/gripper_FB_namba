// 把持力フィードバック//1205
#include <RotaryEncoder.h>
// ロードセル
volatile int loadcell_rec = 0;
volatile int loadcell = 0;
volatile int received = 0;
// アナログピン34,13 モーター->マイコン エンコーダー用
const int ENCODER_PIN_3 = 34;
const int ENCODER_PIN_4 = 35;
// アナログピン25,26 マイコン->モータ モータ制御用
const int DAC_PIN_1 = 26;
const int DAC_PIN_2 = 25;
// ESP32並列処理
volatile int vol1_int = 127;
volatile int vol2_int = 127;
// PID
volatile float newpos1 = 0;
volatile float newpos2 = 0;
volatile int newpos1_int = 0;
volatile int newpos2_int = 0;

float pretime = 0;
float preP2 = 0;
float Kp2 = 0.1; // PIDをゆるく
float Kd2 = 0.005;
float dt = 0.002; // delayとの積が1000
float P2;
float D2;

float a = 0.9;           // Lowpass-filter用
volatile float volt = 0; // Lowpass-fft用
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
            received = Serial.read();
            while (received == 255)
            {
                received = Serial.read();
                loadcell_rec += 255;
            }
            loadcell = loadcell_rec + received;
            loadcell_rec = 0;
        }
        volt = a * volt + (1 - a) * loadcell;
        newpos2 = encoder2.getPosition();
        //    newpos1_int = int(-loadcell*2600/510);
        newpos1_int = int(-volt * 2600 / 510);
        newpos2_int = int(newpos2);
        P2 = newpos1_int - newpos2_int;
        D2 = (P2 - preP2) / dt;
        preP2 = P2;
        vol1_int = 127;
        vol2_int = int(Kp2 * P2 + Kd2 * D2 + 127);
        if (vol2_int > 200)
        {
            vol2_int = 200;
        }
        else if (vol2_int < 54)
        {
            vol2_int = 54;
        }
        dacWrite(DAC_PIN_1, vol1_int);
        dacWrite(DAC_PIN_2, vol2_int);
        delay(1);
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
    Serial.print(loadcell_rec);
    Serial.print(',');
    Serial.println(vol2_int);
    delay(5); // 200Hz
}
// エンコーダリセットすると一回目は不都合になる
