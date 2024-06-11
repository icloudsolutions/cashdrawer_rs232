@echo off

rem Relative path to the installation directory
set "install_dir=%~dp0"

rem Relative path to nssm.exe
set "nssm_path=%install_dir%nssm.exe"

rem Service name
set "service_name=cashdrawer"

rem Check if the service exists
"%nssm_path%" status %service_name% >nul 2>&1
if %errorlevel% neq 0 (
    echo The service %service_name% does not exist.
    pause
    exit /b
)

rem Stop the service if it is running
"%nssm_path%" stop %service_name%

rem Remove the service
"%nssm_path%" remove %service_name% confirm

echo The service %service_name% has been successfully uninstalled.
pause
