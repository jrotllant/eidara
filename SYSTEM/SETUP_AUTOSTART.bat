@echo off
echo ========================================
echo  DARA Watcher - Auto-start Setup
echo ========================================
echo.
echo This will make DARA Watcher start automatically
echo when you log in to Windows. It runs silently in
echo the background (no console window).
echo.
echo Press any key to set up, or close this window to cancel.
pause >nul

:: Strategy: create a shortcut in the Windows Startup folder
:: that points to watcher_silent.vbs in its original location.
:: The VBS uses its own directory to find watcher.py, so it
:: MUST stay in the DARA folder. The shortcut just triggers it.

set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "VBS_SOURCE=%~dp0watcher_silent.vbs"
set "SHORTCUT=%STARTUP%\DARA_Watcher.lnk"

:: Check source exists
if not exist "%VBS_SOURCE%" (
    echo.
    echo ERROR: watcher_silent.vbs not found in DARA folder.
    echo Make sure it exists next to this .bat file.
    echo.
    pause
    exit /b 1
)

:: Create shortcut using PowerShell (available on all modern Windows)
set "ICO_PATH=%~dp0dara.ico"
powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = 'wscript.exe'; $s.Arguments = '\"%VBS_SOURCE%\"'; $s.WorkingDirectory = '%~dp0'; $s.Description = 'DARA Watcher - Auto-compile on VAULT changes'; if (Test-Path '%ICO_PATH%') { $s.IconLocation = '%ICO_PATH%' }; $s.Save()"

if exist "%SHORTCUT%" (
    echo.
    echo ========================================
    echo  SUCCESS
    echo ========================================
    echo.
    echo DARA Watcher will start automatically on every login.
    echo.
    echo What happened:
    echo   Created shortcut in Windows Startup folder.
    echo   Shortcut: %SHORTCUT%
    echo   Target:   %VBS_SOURCE%
    echo.
    echo To remove later:
    echo   Delete DARA_Watcher.lnk from your Startup folder
    echo.
    echo NOTE: The watcher is NOT running right now.
    echo   It will start on your next login, or you can
    echo   double-click START_WATCHER.bat to start it now.
) else (
    echo.
    echo ========================================
    echo  SETUP FAILED
    echo ========================================
    echo Could not create shortcut in Startup folder.
    echo.
    echo Manual alternative:
    echo   1. Press Win+R, type: shell:startup
    echo   2. Create a shortcut to: %VBS_SOURCE%
)
echo.
pause
