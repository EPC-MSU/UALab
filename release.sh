if [ -d venv ]; then rm -rf venv; fi;
if [ -d dist ]; then rm -rf dist; fi;
if [ -d build ]; then rm -rf build; fi;
if [ -d release ]; then rm -rf release; fi;
if [ -f release ]; then rm -f release; fi;
python3 -m venv venv
venv/bin/python -m pip install --upgrade pip
venv/bin/python -m pip install -r requirements.txt

venv/bin/python -m pip install pyinstaller
venv/bin/pyinstaller --clean -F --add-binary "usbadc10gui/usbadc10-debian/libusbadc10.so:." usbadc10gui/__main__.py -n Usbadc10

mv dist release_linux
if [ -d build ]; then rm -rf build; fi;
if [ -d dist ]; then rm -rf dist; fi;
count='ls -1 *.spec 2>/dev/null | wc -l'
if [[ $count != 0 ]]; then rm -rf *.spec; fi;