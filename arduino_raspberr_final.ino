#include <DHT.h>
#include <DHT_U.h>

#define DHTTYPE1 DHT11  // Sensor DHT11
#define DHTTYPE2 DHT22  // Sensor DHT22

const byte OC1A_PIN = 9;
const byte OC1B_PIN = 10;
const word PWM_FREQ_HZ = 25000; // Frecuencia PWM en Hz (25 kHz)
const word TCNT1_TOP = 16000000 / (2 * PWM_FREQ_HZ); // Valor máximo del contador

int dhtpin1 = 7;  // Pin del sensor DHT11
int dhtpin2 = 8;  // Pin del sensor DHT22

DHT HT1(dhtpin1, DHTTYPE1);  // Sensor DHT11
DHT HT2(dhtpin2, DHTTYPE2);  // Sensor DHT22

int dt = 1000;

String t1, h1;
String t2, h2;
String velocidad_str = "0";
int velocidad_int = 0;
int T1, T2;
int s1 = 2;
int s2 = 2;
int largo;
int stream = 0;
int n = 0;
int k;
int j = 0;

String buffer = "";
String  message_from_serial = "";
String  message_to_serial = "";
bool new_message_from_serial = false;
String pos;
int numCom;
int numFan;

void setup() {
  Serial.begin(9600);
  HT1.begin();
  HT2.begin();
  
  pinMode(OC1A_PIN, OUTPUT);
  pinMode(OC1B_PIN, OUTPUT);

  // Configuración del Timer1 para PWM
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1  = 0;
  
  TCCR1A |= (1 << COM1A1) | (1 << COM1B1) | (1 << WGM11);  // Configurar PWM en OC1A y OC1B
  TCCR1B |= (1 << WGM13) | (1 << CS10);  // Seleccionar modo PWM fase correcta y reloj sin prescaler
  ICR1 = TCNT1_TOP;

  velocidad_str = "0";
  j = velocidad_str.length();
  Serial.print(velocidad_str);
  Serial.println(j);
}

void loop() {
  // Leer los sensores DHT11 y DHT22
  t1 = String(round(HT1.readTemperature()));  // Lectura de temperatura DHT11
  h1 = String(round(HT1.readHumidity()));     // Lectura de humedad DHT11
  t2 = String(round(HT2.readTemperature()));  // Lectura de temperatura DHT22
  h2 = String(round(HT2.readHumidity()));     // Lectura de humedad DHT22
  
  T1 = HT1.readTemperature();
  T2 = HT2.readTemperature();
  
  if (isnan(T1)) {
    s1 = 0;
  }
  if (isnan(T2)) {
    s2 = 0;
  }
  
  largo = s1 + s2 + 1;
  n = t1.length() + h1.length() + t2.length() + h2.length() + velocidad_str.length();
  
  // Verificar datos del puerto serial
  serialEvent();
  
  if (new_message_from_serial) {
    numCom = message_from_serial.indexOf(";");
    numFan = message_from_serial.indexOf(":");
    k = message_from_serial.indexOf("\n");
    
    if (numFan != -1) {
      n = n - j;
      velocidad_str = message_from_serial.substring(numFan + 1, k);
      j = velocidad_str.length();
      n = n + velocidad_str.length();
      
      velocidad_int = velocidad_str.toInt();  // Convertir la velocidad a número
      setPwmDuty(velocidad_int);  // Ajustar el PWM en base a la velocidad recibida
    }
    
    if (numCom == 1) {
      Serial.print("#!#" + String(largo) + "#\n");
    }
    
    if (numCom == 2) {
      stream = 1;
    }
    
    if (numCom == 3) {
      stream = 0;
    }
  }
  
  if (stream == 1 && largo >= 4) {
    Serial.print("#D#" + t1 + "#" + h1 + "#" + t2 + "#" + h2 + "#" + velocidad_str + "#" + n + "#\n");
  }
  
  delay(dt);
}

void serialEvent() {
  while (Serial.available()) {
    int inchar = Serial.read();
    buffer += (char)inchar;
    if (inchar == '\n') {
      message_from_serial = buffer;
      new_message_from_serial = true;
      buffer = "";
      break;
    }
  }
}

void setPwmDuty(byte duty) {
  word dutyCycle = (word)(duty * TCNT1_TOP) / 100;
  OCR1A = dutyCycle;  // Ajustar ciclo de trabajo en OC1A (pin 9)
  OCR1B = dutyCycle;  // Ajustar ciclo de trabajo en OC1B (pin 10)
}
