#include <M5Stack.h>
#include <GoPlus2.h>
#include <math.h>

GoPlus2 goPlus;
volatile float sensorValue_init = 0;
volatile int val_h = 0;
volatile int val = 0;
volatile int angle_h = 0;
volatile int angle = 0;

void setup(){
  Serial.begin(115200);
  M5.begin();
  goPlus.begin();
  M5.Power.begin();
  M5.Lcd.setTextSize(2);//画面表示の大きさ
  xTaskCreatePinnedToCore(subProcess, "subProcess", 4096, NULL, 1, NULL, 0); // 並列処理
  sensorValue_init = goPlus.hub1_a_read_value(HUB_READ_ANALOG);
}
void subProcess(void *pvParameters)
{ // 並列処理の関数
  while (1)
    {
    if (Serial.available()) {
        val_h = Serial.read();
    }
    if (val_h > 255){
      val_h = 255;
    }
    else if (val_h < 0){
      val_h = 0;
    }
    angle_h = map(val_h,0,255,0,180);
    goPlus.Servo_write_angle(SERVO_NUM2,angle_h);
    Serial.println(val_h);
    delay(10);
    }
}
void loop(){
  val = goPlus.hub1_a_read_value(HUB_READ_ANALOG)-sensorValue_init;
  if (val > 250){
    val = 250;
  }
  else if (val < 5){
    val = 5;
  }
  angle = map(val,5,250,0,180);
  goPlus.Servo_write_angle(SERVO_NUM0,angle);
  delay(30);
  M5.Lcd.setCursor(0, 0);
  {
      M5.Lcd.setTextColor(WHITE, BLACK);
      M5.Lcd.printf("  raw data |  %0.4d  |\n",val);
      M5.Lcd.printf("   angle   |  %0.4d  |\n",angle);
  }
  
}