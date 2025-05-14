@echo off

SCHTASKS /CREATE /SC HOURLY /MO 12 /TN "E1-ToggleMesh" /TR "\"C:\software-main\bin\runToggleMesh.bat"" /ST 07:00
