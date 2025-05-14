#ifndef PAR_CLASS_h
#define PAR_CLASS_h
#include "Arduino.h"

class PAR {
  
  public:
      PAR(const uint8_t pin, int serial_number);
      double calculate_par();

              
  private:    
      double _a0; // Voltage offset
      double _a1; // Scaling factor
      double _Im; //Immersion Coefficient

      int _sensor_pin;
      int _serial_number;
      double _voltage_signal;
      double _par_value;

};

#endif
