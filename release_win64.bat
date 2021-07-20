: Releases UALab
@echo off
if exist venv rd /s/q venv
if exist dist rd /s/q dist
if exist build rd /s/q build
if exist release_win64 rd /s/q release_win64
echo Please wait. Unfortunately, sometimes it takes several minutes :(
python -m venv  venv

venv\Scripts\python -m pip install --upgrade pip
venv\Scripts\python -m pip install -r requirements.txt

venv\Scripts\python -m pip install pyinstaller
venv\Scripts\pyinstaller -i "usbadc10gui/UALab.ico" --add-data "usbadc10gui/UALab.ico;." --clean -F --noconsole --add-binary "usbadc10gui/usbadc10-win64/usbadc10.dll;." usbadc10gui/__main__.py -n UALab

move dist release_win64
if exist build rd /s/q build
if exist dist rd /s/q dist
if exist __main__.spec del __main__.spec
copy usbadc10gui\UALab.ico release_win64