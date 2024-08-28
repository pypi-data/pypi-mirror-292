@echo off
SET script_directory=%~dp0
SET script_directory=%script_directory:~0,-1%

SET venv_offset=venv_pious

SET plugin_directory=%script_directory%\Plugins\PiousPlugin
SET "venv_directory=%plugin_directory%\%venv_offset%"

SET "venv_activate=%venv_directory%\Scripts\Activate.ps1"
SET "pious_plugin_py=%plugin_directory%\pious_plugin.py"


powershell -File %venv_directory%\Scripts\activate.ps1
python %plugin_directory%\pious_plugin.py

pause