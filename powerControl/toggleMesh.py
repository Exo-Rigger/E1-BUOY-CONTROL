#!/usr/bin/env python
import serial
from time import sleep
import sys


# Toggle Steatite Mesh Radio on / off through Power Management API

IMC_SERIAL_PORT = "COM38"
IMC_BAUD_RATE = 115200
MESH_PWR_CH = 2


def sendData(data):
    with serial.Serial(
        port=IMC_SERIAL_PORT, baudrate=IMC_BAUD_RATE, timeout=1, writeTimeout=1
    ) as imc:
        imc.reset_output_buffer()
        imc.reset_input_buffer()

        imc.write(data.encode())
        while imc.inWaiting():
            ack = imc.readline().decode()
            print(f"[+] RX: {ack}")


def toggleMesh():
    sendData("t\r")
    sendData(f"{MESH_PWR_CH}\r")
    print(f"[+] TOGGLE MESH OK")


if __name__ == "__main__":

    toggleMesh()
