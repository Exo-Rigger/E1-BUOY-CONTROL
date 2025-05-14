#!/usr/bin/env python3

# ================================================================
# Wrapper scrpt for overwatching core control of PML E1 Buoy
# Power management and data acquisition systems
# ================================================================

import threading
from time import sleep
import sys
import datetime
from lib.systemControl.logger import Logger
from lib.powerControl.powerInterface import IMCPowerInterface
from lib.payloadControl.payloadInterface import IMCPayloadInterface

# =====================================================================
# This class creates logging objects for power control and data
# acquisition and contains asynchonous threadded control loops for
# power and payload control
# =====================================================================


class Core:

    def __init__(self, log_dir, data_dir):
        # Define attached payloads
        self.payloads = {
            1: "PAYLOAD_PC",
            2: "STEATITE_MMCU",
            3: "WETLABS_WQM",
            4: "SEABIRD_PAR",
        }
        # Setup logging and collection of data
        self.sys_log_dir = log_dir
        self.pyl_data_dir = data_dir
        self.initLogging()

    def initLogging(self):
        self.sys_log = Logger("core_logger", self.sys_log_dir + "\\core", "core_log")
        self.sys_log.log.info(f"[+] (Core Control) INITIALIZED")

    def runCore(self):
        try:
            self.sys_log.log.info(f"[o] (Core Control) ACTIVE")
            imc_thread = threading.Thread(target=self.runImcControl)
            pyl_thread = threading.Thread(target=self.runPayloadControl)

            imc_thread.start()
            pyl_thread.start()

            imc_thread.join()
            pyl_thread.join()

            self.sys_log.log.info(f"[o] (Core Control) END")
            return 0

        except Exception as error:
            self.sys_log.log.error(error)
            return 1

    # =====================================================================
    # Spin up two separate threads to govern power control and data logging
    # =====================================================================
    # TODO: Give IMCPowerInterface the list of sensor;channel allocations
    def runImcControl(self):
        self.core_ctl = IMCPowerInterface(
            "COM38", 115200, self.sys_log_dir, self.pyl_data_dir, self.payloads
        )
        self.core_ctl.sampleImc()

    def runPayloadControl(self):
        self.pyl_ctl = IMCPayloadInterface(self.sys_log_dir, self.pyl_data_dir)
        self.pyl_ctl.samplePyl()


# =====================================================================


# Directory location for the supevisor logs


def imcCoreMonitor():
    core_mon_logger = Logger(
        "core_mon_log", LOG_DIR + "\\core_monitor", "imc_core_monitor"
    )
    core_mon_logger.log.info(f"[o] (Core Monitor) INITIALIZED")
    e1_core = Core(LOG_DIR, DATA_DIR)

    try:
        core_mon_logger.log.info(f"[o] (Core Monitor) ACTIVE")
        core_return_status = e1_core.runCore()
        if core_return_status == 0:
            core_mon_logger.log.info(f"[+] (Core Monitor) END")

        elif core_return_status == 1:
            sys.exit()

    except Exception as E:
        core_mon_logger.log.error(f"[-] (Core Monitor) CORE FAILURE: {E}")


if __name__ == "__main__":
    # Directory locations for input configuration files & output log and data files
    LOG_DIR = "C:\\E1_InstrumentControl\\system_logs"
    DATA_DIR = "C:\\E1_InstrumentControl\\payload_data"

    imcCoreMonitor()
