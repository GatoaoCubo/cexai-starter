@echo off
REM CEXAI run wrapper (Windows) -- same zero-friction pattern as cex.cmd:
REM .cmd files have no PowerShell execution policy and ignore Mark-of-the-Web.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1" %*
