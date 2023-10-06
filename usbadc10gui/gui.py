"""
This contains the main logic of the program.

The ``UsbadcAPP`` class contains the logic of the GUI.

The ``DataUpdater`` class is responsible for receiving data.

The ``fortest`` function is only needed for the github test.
In fact it is a check that the module is imported normally.

"""
import PyQt5.QtWidgets as qt
from PyQt5 import QtGui
import numpy as np
import PyQt5.QtCore as qtc
import usbadc10gui.design as design
import usbadc10gui.usbadc10 as usbadc10
from usbadc10gui.version import Version
import csv
import serial.tools.list_ports
from platform import system
import qwt
import time
import sys


class DataUpdater(qtc.QObject):
    """
    The ``DataUpdater`` class is responsible for receiving data.
    In this case, the class ``mainwindow`` must have next atributes:

    ``x`` and ``y``, which are arrays of numpai widths (coordinate 2),
    respectively 1 and 10

    ``timer_period``, value in milliseconds

    ``start_stop_status``, bool value to understand,
    get data or not

    ``start_stop_recording_status``, bool value to understand,
    when write data

    ``data_to_scv``, array of numpai width (coordinate 2) is 11
    """
    systimer = time.time()
    connect_error = qtc.pyqtSignal()

    def __init__(self, mainwindow, parent=None):
        super().__init__()
        self.mainwindow = mainwindow

    def run(self):
        """
        Special function to get data.
        """
        while (self.mainwindow.start_stop_status):
            try:
                time_now = time.time() - self.systimer
                data = self.mainwindow.device.get_conversion()
                self.mainwindow.x = np.append(self.mainwindow.x[1:], time_now)
                self.mainwindow.y = np.vstack((self.mainwindow.y[1:, :], np.array(data.data)/10000))
                if self.mainwindow.start_stop_recording_status:
                    self.mainwindow.data_to_scv = np.vstack((self.mainwindow.data_to_scv,
                                                            np.append(time_now, self.mainwindow.y[-1, :])))
            except usbadc10.UrpcDeviceUndefinedError:
                self.connect_error.emit()
                break
            if (self.mainwindow.timer_period > 200):
                period = int(self.mainwindow.timer_period/100)
                for _ in range(period):
                    qtc.QThread.msleep(100)
                    if self.mainwindow.out_status:
                        self.mainwindow.out_status = False
                        break
            elif (self.mainwindow.timer_period <= 200 and self.mainwindow.timer_period != 1):
                qtc.QThread.msleep(int(self.mainwindow.timer_period))
            # else blablabla? No, nothing, it will be near maximum.


class UsbadcAPP(qt.QMainWindow, design.Ui_MainWindow):
    """
    The ``UsbadcAPP`` class contains the logic of the GUI.
    """
    gcolors = (QtGui.QColor(0, 0, 255), QtGui.QColor(0, 170, 0), QtGui.QColor(255, 0, 0),
               QtGui.QColor(0, 0, 0), QtGui.QColor(255, 85, 0), QtGui.QColor(0, 170, 255),
               QtGui.QColor(0, 255, 0), QtGui.QColor(255, 170, 255), QtGui.QColor(111, 111, 111),
               QtGui.QColor(170, 85, 0))
    # 'blue', 'green', 'red', 'black', 'orange', 'lightblue', 'lightgreen', 'pink',  'grey', 'brown'

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowTitle(self.windowTitle() + " " + Version.full)

        self.timer = qtc.QTimer(self)
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.timer_handler_data)

        self.timer_monitor = qtc.QTimer(self)
        self.timer_monitor.setSingleShot(False)
        self.timer_monitor.timeout.connect(self.timer_monitoring)
        self.timer_monitor.start(5000)

        self.os_kind = system().lower()
        self.rescan_com_ports()

        self.start_stop_status = False
        self.start_stop_recording_status = False
        self.out_status = False
        period_vals = np.array([0.001, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 5, 10, 60, 300, 600])
        for i in range(10):
            self.comboBox_period_val.setItemData(i, period_vals[i])
        self.gstates = [True for gstates in range(10)]

        self.x = np.empty(1000)
        self.x[...] = None
        self.y = np.empty((1000, 10))
        self.y[...] = None
        self.data_to_scv = np.empty((0, 11))

        qwt.QwtPlotGrid.make(plot=self.graphWidget,
                             enablemajor=(True, True),
                             enableminor=(True, True),
                             color=qtc.Qt.gray,
                             width=1,
                             style=qtc.Qt.SolidLine,
                             mincolor=qtc.Qt.gray,
                             minwidth=0.5,
                             minstyle=qtc.Qt.DotLine)
        self.graphWidget.setAxisScale(axisId=qwt.QwtPlot.yLeft,
                                      min_=0.0,
                                      max_=3.3,
                                      stepSize=0.5)
        self.graphWidget.enableAxis(axisId=qwt.QwtPlot.yRight, tf=True)
        self.graphWidget.setAxisScale(axisId=qwt.QwtPlot.yRight,
                                      min_=0.0,
                                      max_=3.3,
                                      stepSize=0.5)

        self.graphWidget.setAxisTitle(qwt.QwtPlot.xBottom, "Time, s")
        self.graphWidget.setAxisTitle(qwt.QwtPlot.yLeft, "Voltage, V")
        self.linias = []
        for i in range(10):
            self.linias.append(qwt.QwtPlotCurve.make(xdata=self.x, ydata=self.y[:, i],
                               plot=self.graphWidget, linewidth=2, linecolor=self.gcolors[i]))
        self.graphWidget.show()
        self.threadplot = qtc.QThread()
        # self.threadplot.setPriority(qtc.QThread.HighPriority)
        self.dataupdater = DataUpdater(mainwindow=self)
        self.dataupdater.connect_error.connect(self.connect_error_handler)
        self.dataupdater.moveToThread(self.threadplot)
        self.threadplot.started.connect(self.dataupdater.run)
        # self.threadplot.start()

        self.disconnect_button.setEnabled(False)
        self.start_stop_recording.setEnabled(False)
        self.start_stop.setEnabled(False)
        self.actionDisconnect.setEnabled(False)
        self.actionStart_stop_recording.setEnabled(False)
        self.actionStart_Stop_getting_data.setEnabled(False)
        self.setWindowIcon(QtGui.QIcon('UALab.ico'))

        self.actionThis_Application.triggered.connect(self.this_app)
        self.connect_button.clicked.connect(self.connection)
        self.disconnect_button.clicked.connect(self.disconnection)
        self.comboBox_period_val.activated.connect(self.period_chanded)
        self.rescan_botton.clicked.connect(self.rescan_com_ports)
        self.b_1_blue.toggled.connect(self.replot)
        self.b_2_green.toggled.connect(self.replot)
        self.b_3_red.toggled.connect(self.replot)
        self.b_4_black.toggled.connect(self.replot)
        self.b_5_orange.toggled.connect(self.replot)
        self.b_6_blue_light.toggled.connect(self.replot)
        self.b_7_green_light.toggled.connect(self.replot)
        self.b_8_pig.toggled.connect(self.replot)
        self.b_9_gray.toggled.connect(self.replot)
        self.b_10_brown.toggled.connect(self.replot)
        self.save_button.clicked.connect(self.save_handler)
        self.start_stop.clicked.connect(self.start_stop_handler)
        self.start_stop_recording.clicked.connect(self.start_stop_recording_handler)

    def connection(self):
        """
        Connect devise, unlock some options.
        """
        device_name = self.comboBox_ports.currentText()
        try:
            self.device = usbadc10.Usbadc10DeviceHandle(device_name)
            self.disconnect_button.setEnabled(True)
            self.connect_button.setEnabled(False)
            self.start_stop.setEnabled(True)
            self.actionDisconnect.setEnabled(True)
            self.actionStart_Stop_getting_data.setEnabled(True)
            self.actionConnect.setEnabled(False)
            self.rescan_botton.setEnabled(False)
            self.actionRescan.setEnabled(False)
        except usbadc10.UrpcDeviceUndefinedError:
            msgbox = qt.QMessageBox()
            msgbox.setText("No connection")
            msgbox.exec_()

    def disconnection(self):
        """
        Disconnect devise and rollback of GUI to its original state.
        """
        self.start_stop_recording.setStyleSheet('background: rgb(238,238,238);')
        self.save_button.setEnabled(True)
        self.actionSave.setEnabled(True)
        self.timer.stop()
        self.threadplot.exit()
        self.rescan_com_ports()
        self.disconnect_button.setEnabled(False)
        self.connect_button.setEnabled(True)
        self.start_stop.setEnabled(False)
        self.actionDisconnect.setEnabled(False)
        self.actionStart_stop_recording.setEnabled(False)
        self.actionStart_Stop_getting_data.setEnabled(False)
        self.actionConnect.setEnabled(True)
        self.start_stop_recording.setEnabled(False)
        self.rescan_botton.setEnabled(True)
        self.actionRescan.setEnabled(True)
        self.start_stop_recording_status = False
        self.start_stop_status = False
        self.device.close_device()

    def this_app(self):
        """
        Simple about))) no more.
        """
        msgbox = qt.QMessageBox()
        msgbox.setText("This is a simple cross-platform application for the usbadc10 device.\n" +
                       "Copyright © 2020 Nikita Presnov\npresnovnikita@yandex.ru")
        msgbox.exec_()

    def period_chanded(self):
        """
        If you chaged period.
        """
        self.timer_period = 1000*(self.comboBox_period_val.currentData())
        self.out_status = True
        self.start_stop_recording_status = False
        self.start_stop_recording.setStyleSheet('background: rgb(238,238,238);')
        self.save_button.setEnabled(True)
        self.actionSave.setEnabled(True)
        if self.start_stop_status:
            self.timer.start(200)
            self.x[...] = None
            self.y[...] = None
            self.data_to_scv = np.empty((0, 11))
            self.dataupdater.systimer = time.time()
            self.threadplot.start(qtc.QThread.HighestPriority)
        else:
            self.timer.stop()
            self.threadplot.exit()

    def timer_handler_data(self):
        """
        Timer handler to call drawing data fuction.
        """
        self.data_drawer(self.x, self.y)

    def data_drawer(self, x, y):
        """
        Drawing data.
        """
        for i in range(10):
            if self.gstates[i]:
                self.linias[i].setData(x, y[:, i])

    def start_stop_handler(self):
        """
        Start or stop getting data.
        """
        self.start_stop_status = not (self.start_stop_status)
        if self.start_stop_status:
            self.start_stop_recording.setEnabled(True)
            self.actionStart_stop_recording.setEnabled(True)
        else:
            self.start_stop_recording.setEnabled(False)
            self.actionStart_stop_recording.setEnabled(False)
        self.period_chanded()

    def start_stop_recording_handler(self):
        """
        Start or stop recording data.
        In fact, it only cange flag value.
        """
        self.start_stop_recording_status = not (self.start_stop_recording_status)
        if self.start_stop_recording_status:
            self.start_stop_recording.setStyleSheet('background: rgb(0,170,0);')
            self.save_button.setEnabled(False)
            self.actionSave.setEnabled(False)
        else:
            self.start_stop_recording.setStyleSheet('background: rgb(238,238,238);')
            self.save_button.setEnabled(True)
            self.actionSave.setEnabled(True)

    def save_handler(self):
        """
        Save data from data_to_scv.
        Of course, I can do it from graph, but here you can get more than 1000 values.
        """
        local_filename = str(time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()))
        filename = qt.QFileDialog.getSaveFileName(None,
                                                  'Save File',
                                                  local_filename + ".csv",
                                                  filter="CSV Files (*.csv)",
                                                  options=qt.QFileDialog.DontUseNativeDialog)
        try:
            with open(filename[0], "w", newline="") as file:
                writer = csv.writer(file, delimiter='\t')
                adcs = []
                adcs.append("Time, s")
                for i in range(10):
                    adcs.append("ADC"+str(i+1))
                writer.writerow(adcs)
                writer.writerows(self.data_to_scv)
            self.data_to_scv = np.empty((0, 11))
        except FileNotFoundError:
            msgbox = qt.QMessageBox()
            msgbox.setText("Did not saved")
            msgbox.exec_()

    def replot(self):
        """
        It only clear unselected lines.
        """
        self.gstates[0] = self.b_1_blue.isChecked()
        self.gstates[1] = self.b_2_green.isChecked()
        self.gstates[2] = self.b_3_red.isChecked()
        self.gstates[3] = self.b_4_black.isChecked()
        self.gstates[4] = self.b_5_orange.isChecked()
        self.gstates[5] = self.b_6_blue_light.isChecked()
        self.gstates[6] = self.b_7_green_light.isChecked()
        self.gstates[7] = self.b_8_pig.isChecked()
        self.gstates[8] = self.b_9_gray.isChecked()
        self.gstates[9] = self.b_10_brown.isChecked()
        for i in range(10):
            if not self.gstates[i]:
                self.linias[i].setData(None, None)

    def rescan_com_ports(self):
        """
        Read name)
        """
        self.comboBox_ports.clear()
        ports = serial.tools.list_ports.comports()
        valid_ports = []
        if self.os_kind == "windows":
            for port in sorted(ports):
                try:
                    s = serial.Serial(port.device)
                    s.close()
                    valid_ports.append("com:\\\\.\\" + port.device)
                except (OSError, serial.SerialException):
                    pass
        elif self.os_kind == "darwin":
            msgbox = qt.QMessageBox()
            msgbox.setText("Unsupported system")
            msgbox.exec_()
        elif self.os_kind == "freebsd" or "linux" in self.os_kind:
            for port in sorted(ports):
                try:
                    s = serial.Serial(port.device)
                    s.close()
                    valid_ports.append("com://" + port.device)
                except (OSError, serial.SerialException):
                    pass
        else:
            msgbox = qt.QMessageBox()
            msgbox.setText("Unsupported system")
            msgbox.exec_()
            raise RuntimeError("unexpected OS")
        self.comboBox_ports.addItems(valid_ports)

    @qtc.pyqtSlot()
    def connect_error_handler(self):
        self.threadplot.exit()
        self.timer.stop()
        self.start_stop_recording.setEnabled(False)
        self.start_stop_recording_status = False
        self.start_stop_status = False
        self.start_stop_recording.setStyleSheet('background: rgb(238,238,238);')
        self.save_button.setEnabled(True)
        self.actionSave.setEnabled(True)
        msgbox = qt.QMessageBox()
        msgbox.setText("Connection lost")
        msgbox.exec_()

    def timer_monitoring(self):
        """
        Ask the size of data_to_csv to print it.
        """
        self.size_of_data_out.setText(str(sys.getsizeof(self.data_to_scv)/1000)+" Kb")


def fortest():
    """
    Test for github.
    """
    hello = "Hello, i am working app)))"
    print(hello)
    return hello
