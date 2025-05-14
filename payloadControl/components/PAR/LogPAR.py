#!/usr/bin/env python3

from logger import Logger
from time import sleep
import serial

# -----------------------------------------------------------------------------
# Class Definition of PAR Payload Instrument
# -----------------------------------------------------------------------------

# Inputs:
#  > Hardware port for logging (COMXX)
#  > Communication settings
#  > Path to log data files to


class PAR:

    par_logger = Logger(
        "E1-PAR", "C:\E1_InstrumentControl\payload_data\PAR", "BYE1_PAR"
    )
    par_ctl_logger = Logger(
        "E1-PAR-CTL", "C:\E1_InstrumentControl\system_logs\PAR", "BYE1-PAR-CTL"
    )

    def __init__(self, PORT_PHY="COM37", BAUDRATE=9600):

        # Additional settings if required
        self.buf = bytearray()
        self.s = serial.Serial(PORT_PHY, BAUDRATE)
        self.par_ctl_logger.log.info(
            f"[+] (Payload Control) PAR PASSIVE LOGGING INITIALIZED"
        )

    # This looks funky, but is a leading example of reliable, low latency data acquisition code that doesn't hammeR the CPU
    # benchmarked at approx 790kB/sec compared to pyserial's at 170kB/sec.
    def readLine(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            r = self.buf[: i + 1]
            self.buf = self.buf[i + 1 :]
            return r
        while True:
            i = max(1, min(2048, self.s.in_waiting))
            data = self.s.read(i)
            i = data.find(b"\n")
            if i >= 0:
                r = self.buf + data[: i + 1]
                self.buf[0:] = data[i + 1 :]
                return r
            else:
                self.buf.extend(data)

    def run(self):
        self.par_ctl_logger.log.info(f"[+](Payload Control) PAR PASSIVE LOGGING START")
        for i in range(10):
            data = self.readLine().decode()
            self.par_logger.log.info(data)
            sleep(10)
        self.par_ctl_logger.log.info(f"[+](Payload Control) PAR PASSIVE LOGGING END")


def testPAR():
    attempts = 0
    while attempts < 3:
        try:
            test_par = PAR()
            test_par.run()
            break
        except Exception as err:
            attempts += 1
            # Log error to sys log
            test_par.par_ctl_logger.log.info(
                f"[-] (Payload Control) ERROR LOGGING PAR: {err}"
            )
            test_par.s.close()


if __name__ == "__main__":
    testPAR()
