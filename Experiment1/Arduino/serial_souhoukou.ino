int A = 1;
int B = 1;
void setup()
{
  Serial.begin(115200);
}

void loop()
{
  if (Serial.available() > 0)
  {
    String data1 = Serial.readStringUntil('\n');
    String data2 = Serial.readStringUntil('\n');
    A = data1.toInt() * 2;
    B = data2.toInt() * 2;
  }
  Serial.print(A);
  Serial.print(',');
  Serial.println(B);
}
