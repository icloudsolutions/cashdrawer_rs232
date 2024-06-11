@echo off
set "install_dir=%~dp0"
set "service_name=cashdrawer"
set "exe_path=%install_dir%cashdrawer_rs232.exe"
set "nssm_path=%install_dir%nssm.exe"

rem Check if the service already exists
%nssm_path% status %service_name% >nul 2>&1
if %errorlevel% equ 0 (
    rem Service exists: stopping and removing it
    %nssm_path% stop %service_name%
    %nssm_path% remove %service_name%
)

rem Register the service with nssm
%nssm_path% install %service_name% %exe_path%

rem Start the service
net start %service_name%

echo Service installed and started successfully.
pause
