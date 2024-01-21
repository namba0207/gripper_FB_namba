const int vol_pin = 0;   // 圧力センサ用アナログピン

void setup() {
  Serial.begin(115200);
}

int force=0;
int A;
void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    force=analogRead(vol_pin);
    A = 1023 - force;
    //Serial.print("You sent me: ");
    Serial.println(A);
  }
}
