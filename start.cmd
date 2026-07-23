@echo off
REM CEXAI start wrapper (Windows) -- launches the 3 local apps with zero
REM PowerShell friction (fresh Windows ships ExecutionPolicy=Restricted, and
REM ZIP-downloaded files carry the Mark of the Web -- both block .ps1).
REM Double-click this file or run  start.cmd  from a terminal.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1" %*
