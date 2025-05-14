#include "Arduino.h"
#include "par_class.h"

// Constructor, takes in the serial number
// and analog pin and assigns the correct
// calibration coefficients

PAR::PAR(const uint8_t pin, int serial_number) {

        _sensor_pin = pin;
        _serial_number = serial_number;

      // Calibration Coeffs for Serial 2143
        _a0 = 0.12824; // Voltage offset
        _a1 = 572.27579; // Scaling factor
        _Im = 1.0; //Immersion Coefficient

}

  double PAR::calculate_par() {
    uint16_t x, samples;
    uint16_t value;
    double v_avg;
    value = 0;
    v_avg = 0.0;
    samples = 50;

    for(x=0; x<samples; x++) {
      value += analogRead(_sensor_pin);
      delay(20);
    }
    v_avg = (value/samples) * (5.0 / 1023.0);
    _par_value = _Im * _a1 *(v_avg-_a0);
    
    return _par_value;
  }
