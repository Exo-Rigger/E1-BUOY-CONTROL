@echo off

SCHTASKS /CREATE /SC HOURLY /TN "E1-RunLogPAR" /TR "\"C:\software-main\bin\runLogPAR.bat"" /ST 06:04
