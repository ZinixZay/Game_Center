import sys
from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QFontDatabase, QFont, QPixmap
from db import *
from errors import error_codes


def move_back(step: int):
    widget.setCurrentIndex(widget.currentIndex() - step)


def move_forward(step: int):
    widget.setCurrentIndex(widget.currentIndex() + step)


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
        triple_agent = QPixmap('photos/triple.png')
        self.labelPhoto.setPixmap(triple_agent)

    def host_clicked(self):
        global call_status, nick
        nick = self.nameLine.text()
        if len(nick) > 11:
            showerror('Максимальное количество символов - 11')
            return
        call_status = 'host'
        move_forward(1)

    def connect_clicked(self):
        global call_status, nick
        nick = self.nameLine.text()
        call_status = 'connect'
        move_forward(1)


class Servername(QMainWindow):
    def __init__(self):
        global call_status
        super(Servername, self).__init__()
        loadUi("screens/server.ui", self)
        self.backButton.clicked.connect(self.back_clicked)
        self.doneButton.clicked.connect(self.done_clicked)

    def done_clicked(self):
        name = self.servernameLine.text().replace(' ', '_')
        if len(name) > 11:
            showerror('Максимальное количество символов - 11')
            return
        request = {'name': name,
                   'nickname': nick,
                   'status': call_status}
        answer = catch_request(request)
        if answer['status'] == 'error':
            showerror(answer['content'])
            move_back(1)
        else:
            global game_info
            game_info = {
                'nick': answer['nick'],
                'name': answer['name']
            }
            if get_server_role(game_info['name'], game_info['nick']) != 'host':
                lobby.startButton.hide()
            lobby.list_refresh()
            lobby.labelLobbyname.setText(game_info['name'])
            move_forward(1)

    def back_clicked(self):
        self.servernameLine.text = 'Server name'
        move_back(1)


class Lobby(QMainWindow):
    def __init__(self):
        global game_info
        super(Lobby, self).__init__()
        loadUi("screens/lobby.ui", self)
        self.backButton.clicked.connect(self.back_button)
        self.refreshButton.clicked.connect(self.list_refresh)

    def back_button(self):
        move_back(2)

    def list_refresh(self):
        global game_info
        name = game_info['name']
        players = get_player_nicknames(name)
        for i in players:
            already_in = [self.labelSlot1.text(),
                          self.labelSlot2.text(),
                          self.labelSlot3.text(),
                          self.labelSlot4.text(),
                          self.labelSlot5.text()]
            if i in already_in:
                continue
            if self.labelSlot1.text() not in players:
                self.labelSlot1.setText(i)
                continue
            if self.labelSlot2.text() not in players:
                self.labelSlot2.setText(i)
                continue
            if self.labelSlot3.text() not in players:
                self.labelSlot3.setText(i)
                continue
            if self.labelSlot4.text() not in players:
                self.labelSlot4.setText(i)
                continue
            if self.labelSlot5.text() not in players:
                self.labelSlot5.setText(i)
                continue


# Запуск программы

app = QApplication(sys.argv)
id = QFontDatabase.addApplicationFont('fonts/20665.ttf')
widget = QtWidgets.QStackedWidget()
mainWindow = MainWindow()
serverName = Servername()
lobby = Lobby()
font = QFont('20665')
widget.setFont(font)
widget.setWindowTitle('Spy')
widget.addWidget(mainWindow)
widget.addWidget(serverName)
widget.addWidget(lobby)
widget.setFixedSize(800, 600)
widget.show()


try:
    sys.exit(app.exec_())
except:
    print('Exiting')
