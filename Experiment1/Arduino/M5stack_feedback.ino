#include <M5Stack.h>
#include <GoPlus2.h>
#include <math.h>

GoPlus2 goPlus;
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
}
void loop(){
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');      
    data_f = data.substring(0, data.indexOf(',')).toInt();
    data_s = data.substring(data.indexOf(',') + 1).toInt();
  }

  if (val_f > 250){
    val_f = 250;
  }
  else if (val_f < 5){
    val_f = 5;
  }
  angle_f = map(val_f,5,250,0,180);

  if (val_s > 250){
    val_s = 250;
  }
  else if (val_s < 5){
    val_s = 5;
  }
  angle_s = map(val_s,5,250,0,180);

  goPlus.Servo_write_angle(SERVO_NUM0,angle_f);
  goPlus.Servo_write_angle(SERVO_NUM1,angle_f);
  goPlus.Servo_write_angle(SERVO_NUM2,angle_s);
  goPlus.Servo_write_angle(SERVO_NUM3,angle_s);
  delay(30);
  M5.Lcd.setCursor(0, 0);
  {
      M5.Lcd.setTextColor(WHITE, BLACK);
      M5.Lcd.printf("  data_f  |  %0.4d  |\n",val_f);
      M5.Lcd.printf("   angle_f   |  %0.4d  |\n",angle_f);
  }
}