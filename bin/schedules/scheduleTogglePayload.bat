@echo off

SCHTASKS /CREATE /SC HOURLY /MO 1 /TN "E1-TogglePayload" /TR "\"C:\software-main\bin\runTogglePayload.bat"" /ST 07:00
