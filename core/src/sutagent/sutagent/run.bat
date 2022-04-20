@echo off
setlocal EnableDelayedExpansion

for %%i in (%0) do set src=%%~dpi
set src=%src:~0,-1%
echo %src%
set PYTHONPATH=%src%\..
set PROJECTPATH=%src%

goto PY3

:PY3
cd %PROJECTPATH%
REM kill python.exe
for /f "tokens=1,2" %%A in ('tasklist') do (
    if /I "%%A"=="python.exe" (
        set curpid=%%B
        taskkill /f /pid !curpid! /t
        )
    )
	
REM kill ServerManager.exe
for /f "tokens=1,2" %%A in ('tasklist') do (
    if /I "%%A"=="ServerManager.exe" (
        set curpid=%%B
        taskkill /f /pid !curpid! /t
        )
    )
	
start "start sutagent" python3 %src%\sut_agent.py

:END
@echo on