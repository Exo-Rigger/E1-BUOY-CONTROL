#include "par_class.h"



// PAR Sensor In Use
PAR PAR_2142(A0,2142);

void setup() {
        Serial.begin(9600);
}

void loop() {
  
  Serial.println(PAR_2142.calculate_par());
  
}
