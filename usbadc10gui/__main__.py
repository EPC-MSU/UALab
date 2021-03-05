import PyQt5.QtWidgets as qt
import sys
from usbadc10gui.gui import uRPCApp


def main():
    app = qt.QApplication(sys.argv)
    app.setStyle('Fusion')
    window = uRPCApp()
    window.show()
    sys.exit(app.exec_())
    window.disconnecton()


if __name__ == '__main__':
    main()