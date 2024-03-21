# usbadc10

![](media/usbadc10_board.jpg)

## RU

Графический интерфейс для устройства usbadc10.

Помимо программы здесь также приложены тесты и тест скорости, по которому оценивалась скорость работы.
Для работы у вас также должен стоять интерпретатор питон.

### Запустить из под корня под Linux

```bash
sudo -H pip3 install -r requirements.txt
python3 -m usbadc10gui
```

### Запустить из под корня под Windows

```bash
pip install -r requirements.txt
python -m usbadc10gui
```

### Сборка бинарного файла Linux

```bash
sudo -H pip3 install pyinstaller
source release.sh
```

### Сборка бинарного файла Windows

```bash
pip install pyinstaller
.\release-win64.bat
```

![Скриншот совта](media/ualab_main_window.png)

В некоторых дистрибудивах линукс(kde neon) приложение берёт системную цветовую схему.
Также при запуске в некоторые дистрибутивы могут потребовать пакет python3-pyqt5.qtsvg.
Установить sudo apt install python3-pyqt5.qtsvg.

## EN

Graphical interface for usbadc10 device.
In addition to it, tests and a speed test are also attached here, by which the speed of work was assessed.
To work, you must also have a python interpreter (32 bits for Windows).

### Run from root under Linux

```bash
sudo -H pip3 install -r requirements.txt
python3 -m usbadc10gui
```

### Run from root under Windows

```bash
pip install -r requirements.txt
python -m usbadc10gui
```

### Build Linux Binary

```bash
sudo -H pip3 install pyinstaller
source release.sh
```

### Build Windows Binary

```bash
pip install pyinstaller
.\release-win64.bat
```

![App screenshot](media/ualab_main_window.png)

In some Linux distributions (kde neon), the application takes the system color scheme.
Also, when running on some distributions, the python3-pyqt5.qtsvg package may be required.
Install sudo apt install python3-pyqt5.qtsvg. 