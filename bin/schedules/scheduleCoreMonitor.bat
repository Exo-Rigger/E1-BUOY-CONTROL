@echo off

SCHTASKS /CREATE /SC HOURLY /TN "E1-CoreMonitor" /TR "\"C:\software-main\bin\runCoreMonitor.bat"" /ST 06:00
