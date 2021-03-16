: Releases UALab
@echo off
if exist venv rd /s/q venv
if exist dist rd /s/q dist
if exist build rd /s/q build
if exist release_win32 rd /s/q release_win32
echo Please wait. Unfortunately, sometimes it takes several minutes :(
python -m venv  venv

venv\Scripts\python -m pip install --upgrade pip
venv\Scripts\python -m pip install -r requirements.txt

venv\Scripts\python -m pip install pyinstaller
venv\Scripts\pyinstaller -i "usbadc10gui/usbadc10.ico" --add-data "usbadc10gui/usbadc10.ico;." --clean -F --noconsole --add-binary "usbadc10gui/usbadc10-win32/usbadc10.dll;." usbadc10gui/__main__.py -n Usbadc10

move dist release_win32
if exist build rd /s/q build
if exist dist rd /s/q dist
if exist __main__.spec del __main__.spec
copy usbadc10gui\usbadc10.ico release_win32