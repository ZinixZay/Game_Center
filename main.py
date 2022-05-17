import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QFontDatabase, QFont
from db import *
from errors import error_codes


def showerror(content: str):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(f'Error code = {error_codes[content]}')
    msg.setInformativeText(content)
    msg.setWindowTitle("Error")
    msg.exec_()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("screens/main.ui", self)
        self.hostButton.clicked.connect(self.host_clicked)
        self.connectButton.clicked.connect(self.connect_clicked)

    def host_clicked(self):
        global call_status, nick
        nick = self.nameLine.text()
        call_status = 'host'
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def connect_clicked(self):
        global call_status, nick
        nick = self.nameLine.text()
        call_status = 'connect'
        widget.setCurrentIndex(widget.currentIndex() + 1)


class Servername(QMainWindow):
    def __init__(self):
        global call_status
        super(Servername, self).__init__()
        loadUi("screens/server.ui", self)
        self.backButton.clicked.connect(self.back_clicked)
        self.doneButton.clicked.connect(self.done_clicked)

    def done_clicked(self):
        name = self.servernameLine.text().replace(' ', '_')
        request = {'name': name,
                   'nickname': nick,
                   'status': call_status}
        answer = catch_request(request)
        if answer['status'] == 'error':
            showerror(answer['content'])

    @staticmethod
    def back_clicked():
        widget.setCurrentIndex(widget.currentIndex() - 1)


# Первоначальный запуск программы

app = QApplication(sys.argv)
id = QFontDatabase.addApplicationFont('fonts/20665.ttf')
widget = QtWidgets.QStackedWidget()
mainWindow = MainWindow()
serverName = Servername()
font = QFont('20665')
widget.setFont(font)
widget.setWindowTitle('Spy')
widget.addWidget(mainWindow)
widget.addWidget(serverName)
widget.setFixedSize(800, 600)
widget.show()


try:
    sys.exit(app.exec_())
except:
    print('Exiting')
