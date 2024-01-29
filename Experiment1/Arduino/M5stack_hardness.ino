#include <M5Stack.h>
#include <GoPlus2.h>
#include <math.h>

GoPlus2 goPlus;
float sensorValue_init = 0;
int val = 0;
int angle = 0;

void setup()
{
  Serial.begin(115200);
  M5.begin();
  goPlus.begin();
  M5.Power.begin();
  M5.Lcd.setTextSize(2); // 画面表示の大きさ
}
void loop()
{
  if (Serial.available())
  {
    val = Serial.read();
  }
  if (val > 250)
  {
    val = 250;
  }
  else if (val < 5)
  {
    val = 5;
  }
  Serial.println(val);
  angle = map(val, 5, 250, 0, 180);
  goPlus.Servo_write_angle(SERVO_NUM0, angle);
  delay(30);
  M5.Lcd.setCursor(0, 0);
  {
    M5.Lcd.setTextColor(WHITE, BLACK);
    M5.Lcd.printf("  raw data |  %0.4d  |\n", val);
    M5.Lcd.printf("   angle   |  %0.4d  |\n", angle);
  }
}
