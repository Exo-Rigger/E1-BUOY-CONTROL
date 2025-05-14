#!/usr/bin/env python3

# =====================================================================
# This class is an interface for managing supply power to attached
# payloads via the IMC microcontroller and logs
# power control actions and power information of each payload streamed
# from the MCU.
# =====================================================================

import serial
from time import sleep, strftime
from logger import (
    Logger,
)  # You also changed this but this file should be removed anyway after it's properly setup
from pathlib import Path
import subprocess

PAYLOADS = {
    "01": "WQM",
    "02": "PAR",
    "03": "WR Radio",
    "04": "Payload PC",
}


class IMCPowerInterface:
    # The constructor initializes MCU communication parameters and
    # creates a logging object to store system activity
    #   Constructor inputs:
    #    serial_port: Serial port of MCU
    #    baudrate:    Telemetry baudrate of MCU
    def __init__(self, serial_port, baudrate, log_dir, data_dir, payloads):
        self.payloads = payloads
        self.device = serial_port
        self.baudrate = baudrate
        self.log_dir = log_dir + "\\imc"
        self.data_dir = data_dir
        self.payloads = payloads
        self.imc_control_logger = Logger(
            "IMC System Logger", f"{self.log_dir}", "imc_control_log"
        )

        self.imc_power_logger = Logger(
            "IMC Power Logger", f"{self.log_dir}" + "\\power_logs", "imc_power_log"
        )

        # Hide data streams from std_out
        #       self.imc_power_logger.stream_handler.setLevel(100)

        self.imc_power_logger.log.info(f"DEVICE,CHANNEL,STATE,VOLTAGE(V),CURRENT(mA)")

        self.imc_control_logger.log.info(f"[o] (IMC Control) INITIALIZED")

    # Initiate a telemetry session with the MCU to send a command
    #   Function inputs:
    #     cmd:

    def resetMCU(self):
        mcu_reset_path = (
            r"C:\l4-buoy-main\Instrument Management and Control\firmware\resetTC275.exe"
        )
        self.imc_control_logger.log.info(f"[+] (IMC Control) CORE RESET")

    def sendData(self, cmd, return_handle=False):
        handle = serial.Serial(self.device, self.baudrate, timeout=0.1, writeTimeout=3)
        handle.set_buffer_size(rx_size=12800, tx_size=12800)
        handle.reset_output_buffer()
        handle.reset_input_buffer()
        handle.write(cmd.encode() + b"\n")
        self.imc_control_logger.log.info(f"[+] (IMC Control) TX: {cmd}")
        ack = handle.readline().decode()
        self.imc_control_logger.log.info(f"[+] (IMC Control) RX: {ack}")
        if return_handle:
            return handle
        else:
            handle.close()

    def logData(self, data):
        ch_array = data.split(";")

        for ch_data in ch_array:
            try:
                log_entry = self.payloads[int(ch_data[0])] + "," + ch_data
                self.imc_power_logger.log.info(log_entry)
            except Exception as error:
                # self.imc_control_logger.log.error(f"[-] (IMC Control) ERR: {error}")
                continue

    # ================================================================
    # Abstracted IMC Commands to reduce direct access to MCU interface
    # ================================================================

    def setCh(self, ch, state):
        device = self.payloads[ch]
        self.imc_control_logger.log.info(f"[o] (IMC Control) SET: {device} {state}")
        cmd = f"set {ch} {state}\r"
        self.sendData(cmd)
        self.imc_control_logger.log.info(f"[+] (IMC Control) SET: {device} {state}")

    def cycleCh(self, ch):
        device = self.payloads[ch]
        self.imc_control_logger.log.info(f"[o] (IMC Control) CYCLE: {device}")
        cmd = f"cycle {ch}\r"
        self.sendData(cmd)
        self.imc_control_logger.log.info(f"[+] (IMC Control) CYCLE: {device}")

    def toggleCh(self, ch):
        device = self.payloads[ch]
        self.imc_control_logger.log.info(f"[o] (IMC Control) TOGGLE: {device}")
        cmd = f"toggle {ch}"
        self.sendData(cmd)
        self.imc_control_logger.log.info(f"[+] (IMC Control) TOGGLE: {device}")

    # Set logging mode (0 = poll, 1 = stream)
    def setMode(self, mode):
        self.imc_control_logger.log.info(f"[o] (IMC Control) MODE: {mode}")
        cmd = f"mode {mode}\r"
        self.sendData(cmd)
        self.imc_control_logger.log.info(f"[+] (IMC Control) MODE: {mode}")

    # Power on CTD and PAR
    def activatePyl(self):
        #       self.setCh(2,1)
        #       self.setCh(3,1)
        #       self.setCh(4,1)
        self.imc_control_logger.log.info(f"[+] (IMC Control) PYL ACTIVE")
        self.toggleCh("01")
        self.toggleCh("02")

    # Power off CTD and PAR
    def deactivatePyl(self):
        #       self.setCh(2,0)
        #       self.setCh(3,0)
        #       self.setCh(4,0)
        self.imc_control_logger.log.info(f"[+] (IMC Control) PYL DISABLED")
        self.toggleCh("01")
        self.toggleCh("02")

    # Activates payload, takes 200 samples at 5Hz default, stops logging, deactivates payload
    # Method now detects if no data is received, the function is repeated
    def sampleImc(self, samples=200, frequency=5):
        dt = 1 / frequency
        self.imc_control_logger.log.info(f"[o] (IMC Control) ACTIVE")
        self.imc_control_logger.log.info(f"[o] (IMC Control) SAMPLE IMC")
        self.activatePyl()
        self.setMode(1)
        restart_sampling = False
        with serial.Serial(port=self.device, baudrate=self.baudrate, timeout=1) as imcs:
            for i in range(samples):
                try:
                    sleep(dt)
                    status_string = imcs.readline().decode()
                    if not len(status_string):
                        self.imc_control_logger.log.info(
                            "[-] (IMC Control) NO DATA FROM IMC"
                        )
                        restart_sampling = True
                        break
                    else:
                        self.logData(status_string)
                except Exception as Err:
                    self.imc_control_logger.log.info(
                        f"[-] (IMC Control) SAMPLE IMC \n{Err}"
                    )
        self.deactivatePyl()
        self.setMode(0)
        self.imc_control_logger.log.info(f"[+] (IMC Control) SAMPLE IMC")
        self.imc_control_logger.log.info(f"[o] (IMC Control) END")

        if restart_sampling:
            self.imc_control_logger.log.info("[x] (IMC Control) RESTART SAMPLING")
            sleep(2)
            self.sampleImc(samples, frequency)


# ================================================================

if __name__ == "__main__":
    g = IMCPowerInterface("COM38", 115200, ".\\", ".\\", PAYLOADS)  # Change this
    #   g.sampleImc()
    g.toggleCh("01")
    g.toggleCh("02")
