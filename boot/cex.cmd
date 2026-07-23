@echo off
REM CEXAI boot wrapper (Windows) -- starts the N07 orchestrator with zero
REM PowerShell friction. Fresh Windows ships ExecutionPolicy=Restricted, and
REM ZIP-downloaded files carry the Mark of the Web -- both block .ps1 scripts
REM ("not digitally signed"). A .cmd file has no execution policy, so this
REM works everywhere: double-click it or run  boot\cex.cmd  from a terminal.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0cex.ps1" %*
