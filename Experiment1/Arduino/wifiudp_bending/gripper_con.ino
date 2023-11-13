//把持力フィードバック//
#include <RotaryEncoder.h>
#include <math.h>

//ロードセル
int loadcell_rec = 127;

//アナログピン34,13 モーター->マイコン エンコーダー用
const int ENCODER_PIN_1 = 34;
const int ENCODER_PIN_2 = 35;
const int ENCODER_PIN_3 = 32;
const int ENCODER_PIN_4 = 33;

//アナログピン25,26 マイコン->モータ モータ制御用
const int DAC_PIN_1 = 25;
const int DAC_PIN_2 = 26;

int vol1_int = 127;
int vol2_int = 127;
//PID
int newpos1_int = 0;
int newpos2_int = 0;

float pretime = 0;
float preP1 = 0;
float preP2 = 0;
float Kd1 = 0.008;  //発振用ダンパ係数
float Kp2 = 0.05;   //PIDをゆるく
float Kd2 = 0.008;
float dt;
float P1;
float P2;
float D1;
float D2;
RotaryEncoder encoder1(ENCODER_PIN_1, ENCODER_PIN_2);    
RotaryEncoder encoder2(ENCODER_PIN_3, ENCODER_PIN_4); 

void IRAM_ATTR ISR() {
  encoder1.tick(); 
  encoder2.tick();
}

void setup(){
  pinMode(DAC_PIN_1, OUTPUT);
  pinMode(DAC_PIN_2, OUTPUT);
  Serial.begin(115200);
  Serial.println("SimplePollRotator example for the RotaryEncoder library.");
  attachInterrupt(ENCODER_PIN_1, ISR, CHANGE);
  attachInterrupt(ENCODER_PIN_2, ISR, CHANGE);
  attachInterrupt(ENCODER_PIN_3, ISR, CHANGE);
  attachInterrupt(ENCODER_PIN_4, ISR, CHANGE); //割り込み処理いる？loop()内にISR()の内容書いても動きそう
}

void loop(){
  newpos1_int = (int)encoder1.getPosition();  //元々のgetPositionはintで拾う？ → 確認したらlong型でした．実機で動かしてから修正したい．
  newpos2_int = (int)encoder2.getPosition();  //腹を括って並列処理を削除．動かなかったら戻す．

  if (Serial.available()) 
  {
    loadcell_rec = Serial.read();
  }

  dt = 0.01;
  D1 = (preP1 - newpos1_int) / dt;
  preP1 = newpos1_int;
  P2 = newpos1_int - newpos2_int;
  D2 = (P2 - preP2) / dt;
  preP2 = P2;

  vol1_int = int(loadcell_rec + Kd1*D1); // コントロール側は今まで通り反力くる
  vol2_int = int(Kp2*P2 + Kd2*D2 + 127); // サポート側はスクイーズで反力くる

  if(vol1_int>255){
    vol1_int = 255;
  }
  else if(vol1_int<0){
    vol1_int = 0;
  }
  if(vol2_int>255){
    vol2_int = 255;
  }
  else if(vol2_int<0){
    vol2_int = 0;
  }
  
  dacWrite(DAC_PIN_1,vol1_int);
  dacWrite(DAC_PIN_2,vol2_int);
  Serial.print(newpos1_int);
  Serial.print(',');
  Serial.print(newpos2_int);
  Serial.print(',');
  Serial.print(vol1_int);
  Serial.print(',');
  Serial.println(vol2_int);

  delay(10);//100Hz
}