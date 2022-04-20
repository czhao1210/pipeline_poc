@echo off
setlocal EnableDelayedExpansion

set port=""
set /p port=[SUTAgent Serial Port Configuration] port:
if %port%=="" (echo pass) else (python3 change_win_setting.py --port %port%)

for %%i in (%0) do set src=%%~dpi
set src=%src:~0,-1%
set PYTHONPATH=%src%\..
set PROJECTPATH=%src%

goto PY3

:PY3
REM clean original startup in case exist
reg delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "startagent" /f 2> nul
echo. > %src%\..\common2\lib\__init__.py

REM register auto startup
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "startagent" /t REG_SZ /d "%src%\run.bat" /f

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
echo on
