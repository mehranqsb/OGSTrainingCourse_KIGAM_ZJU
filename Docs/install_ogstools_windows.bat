@echo off
setlocal EnableExtensions

rem OpenGeoSys course installer for 64-bit Windows and Python 3.13.
rem Double-click for online installation, or run: install_ogstools_windows.bat offline
rem Offline mode expects a wheelhouse_windows folder beside this batch file.

set "VENV=%~dp0.venv_ogs"
set "WHEELS=%~dp0wheelhouse_windows"
set "OGS_VERSION=6.5.9"
set "OGSTOOLS_VERSION=0.8.2"

if "%~1"=="" goto mode_online
if /I "%~1"=="online" goto mode_online
if /I "%~1"=="offline" goto mode_offline
echo Usage: %~nx0 [online^|offline]
goto fail

:mode_online
set "INSTALL_MODE=online"
goto start

:mode_offline
set "INSTALL_MODE=offline"
if not exist "%WHEELS%\*.whl" (
    echo ERROR: No wheel files found in "%WHEELS%".
    echo Prepare the complete Windows Python 3.13 wheelhouse on a connected computer.
    goto fail
)
goto start

:start
echo Installing OGS %OGS_VERSION% and OGSTools %OGSTOOLS_VERSION% in %INSTALL_MODE% mode.
py -3.13 --version
if errorlevel 1 (
    echo ERROR: Install 64-bit Python 3.13 with the Python launcher and pip.
    goto fail
)

if not exist "%VENV%\Scripts\python.exe" (
    py -3.13 -m venv "%VENV%"
    if errorlevel 1 goto fail
)

set "PY=%VENV%\Scripts\python.exe"
if /I "%INSTALL_MODE%"=="offline" goto install_offline

"%PY%" -m pip install --upgrade "ogs==%OGS_VERSION%" "ogstools[all]==%OGSTOOLS_VERSION%" "notebook" "jupyterlab"
if errorlevel 1 goto fail
goto verify

:install_offline
"%PY%" -m pip install --upgrade --no-index --find-links "%WHEELS%" "ogs==%OGS_VERSION%" "ogstools[all]==%OGSTOOLS_VERSION%" "notebook" "jupyterlab"
if errorlevel 1 goto fail

:verify
"%PY%" -c "from importlib.metadata import version; print('OGS package:', version('ogs')); print('OGSTools:', version('ogstools'))"
if errorlevel 1 goto fail
"%PY%" -c "import ogstools as ot; assert ot.status(verbose=True)"
if errorlevel 1 goto fail
if not exist "%VENV%\Scripts\ogs.exe" (
    echo ERROR: ogs.exe was not found in the environment.
    goto fail
)
"%VENV%\Scripts\ogs.exe" --version
if errorlevel 1 goto fail
if not exist "%VENV%\Scripts\jupyter.exe" (
    echo ERROR: jupyter.exe was not found in the environment.
    goto fail
)
"%VENV%\Scripts\jupyter.exe" notebook --version
if errorlevel 1 goto fail

echo.
echo Installation succeeded. Environment: "%VENV%"
echo Start Jupyter Notebook with: "%VENV%\Scripts\jupyter.exe" notebook
pause
exit /b 0

:fail
echo.
echo Installation or verification failed. Read the message above.
pause
exit /b 1
