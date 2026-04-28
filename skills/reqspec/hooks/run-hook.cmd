@echo off & set "BASH=" & FOR %%G IN (bash.exe) DO set "BASH=%%~$PATH:G"
@IF NOT DEFINED BASH FOR %%G IN ("C:\Program Files\Git\bin\bash.exe") DO @IF EXIST %%G set "BASH=%%~G"
@IF DEFINED BASH ("%BASH%" "%~dp0%~1" %* & exit /b %ERRORLEVEL%)
@echo {"error": "bash not found"} & exit /b 1
#!/bin/bash
# polyglot: lines above handle Windows, lines below handle Unix
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec bash "$SCRIPT_DIR/$1" "${@:2}"
