import sys
from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QFontDatabase, QFont, QPixmap
from db import *
from threading import *
from time import sleep
from errors import error_codes

''' Вспомогательные функции '''


def close_all_threads():
    global if_check_game, if_refresh_slots
    if_check_game, if_refresh_slots = False, False


def check_game_status(name: str, nickname: str):
    sleep(5)
    while if_check_game:
        get_game_status(name, nickname)
        sleep(2)


def list_refresh(lobby):
    global game_info
    name = game_info['name']
    while if_refresh_slots:
        try:
            players = get_player_nicknames(name)
        except:
            break
        lobby.labelSlot1.setText(players[0])
        if len(players) > 1:
            lobby.labelSlot2.setText(players[1])
        else:
            lobby.labelSlot2.setText('Empty slot')
            lobby.labelSlot3.setText('Empty slot')
            lobby.labelSlot4.setText('Empty slot')
            lobby.labelSlot5.setText('Empty slot')
        if len(players) > 2:
            lobby.labelSlot3.setText(players[2])
        else:
            lobby.labelSlot3.setText('Empty slot')
            lobby.labelSlot4.setText('Empty slot')
            lobby.labelSlot5.setText('Empty slot')
        if len(players) > 3:
            lobby.labelSlot4.setText(players[3])
        else:
            lobby.labelSlot4.setText('Empty slot')
            lobby.labelSlot5.setText('Empty slot')
        if len(players) > 4:
            lobby.labelSlot5.setText(players[4])
        else:
            lobby.labelSlot5.setText('Empty slot')
        sleep(2)


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


''' Окна '''


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

    def closeEvent(self, event):
        print('zxc')
        event.accept()


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
            lobby.labelLobbyname.setText(game_info['name'])
            global t1, if_refresh_slots, if_check_game
            if_refresh_slots, if_check_game = True, True
            slot_refreshing = Thread(target=list_refresh, args=(lobby,))
            slot_refreshing.start()
            game_status_checking = Thread(target=check_game_status, args=(game_info['name'], game_info['nick']))
            game_status_checking.start()
            move_forward(1)

    def back_clicked(self):
        self.servernameLine.text = 'Server name'
        move_back(1)


class Lobby(QMainWindow):
    def __init__(self):
        global game_info
        super(Lobby, self).__init__()
        loadUi("screens/lobby.ui", self)
        self.backButton.clicked.connect(self.back_clicked)
        self.startButton.clicked.connect(self.start_clicked)

    def back_clicked(self):
        global if_refresh_slots, if_check_game
        if_refresh_slots, if_check_game = False, False
        if get_server_role(game_info['name'], game_info['nick']) == 'host':
            drop_lobby(game_info['name'])
        else:
            leave_player(game_info['name'], game_info['nick'])
        move_back(2)

    def start_clicked(self):
        change_game_status(game_info['name'], 'started')


class Screens(QtWidgets.QStackedWidget):
    def closeEvent(self, event):
        close_all_threads()
        event.accept()


''' Запуск программы '''

app = QApplication(sys.argv)
id = QFontDatabase.addApplicationFont('fonts/20665.ttf')
widget = Screens()
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

''' Завершение работы программы '''

try:
    sys.exit(app.exec_())
except:
    print('Exiting')
