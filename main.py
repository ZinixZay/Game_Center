import random
import sys
from fuzzywuzzy import fuzz
from threading import *
from time import sleep
from time import time

from PyQt5 import QtWidgets
from PyQt5.QtGui import QFontDatabase, QFont, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.uic import loadUi

from db import *
from errors import error_codes
from locations import locations

''' Вспомогательные функции '''


def calculate_game_result():
    players = get_player_nicknames(game_info['name'])
    vote_result = dict()
    for nickname in players:
        vote_result[nickname] = int(get_votes(game_info['name'], nickname))
    mc, killed, draw = 0, '', False
    for player, count in vote_result.items():
        if count > mc:
            mc, killed, draw = count, player, False
        elif count == mc:
            draw = True
    if draw or killed != get_spy(game_info['name']):
        results.labelSpy_info.setText('Шпиона не поймали. Им был:')
    results.labelSpy.setText(f'{get_spy(game_info["name"])}')
    if fuzz.token_sort_ratio(get_suggestion(game_info['name'], game_info['nick']),
                             get_location(game_info['name'], game_info['nick'])) < 60:
        results.labellocation_info.setText('Шпион не угадал локацию:')
    results.labellocation.setText(get_location(game_info['name'], game_info['nick']))


def check_game_ended():
    while 1:
        status = is_end_game(game_info['name'], game_info['nick'])
        if status == 'yes':
            calculate_game_result()
            move_forward(1)
            break
        sleep(1)


def check_all_ready():
    while 1:
        players = get_player_nicknames(game_info['name'])
        statuses = list()
        for nickname in players:
            statuses.append(get_ready_status(game_info['name'], nickname))
        if 'no' not in statuses:
            end_game(game_info['name'])
            calculate_game_result()
            move_forward(1)
            break
        sleep(1)


def vote_made():
    voting.candidate4.hide()
    voting.candidate3.hide()
    voting.candidate2.hide()
    voting.candidate1.hide()
    voting.locationLine.hide()
    voting.admitButton.hide()
    voting.labelInfo.hide()
    if get_server_role(game_info['name'], game_info['nick']) == 'host':
        control_all_answered = Thread(target=check_all_ready)
        control_all_answered.start()
    else:
        control_game_ended = Thread(target=check_game_ended)
        control_game_ended.start()
    voting.labelInfo2.show()


def prepare_to_vote():
    voting.labelInfo2.hide()
    if get_game_role(game_info['name'], game_info['nick']) == 'spy':
        voting.candidate1.hide()
        voting.candidate2.hide()
        voting.candidate3.hide()
        voting.candidate4.hide()
    else:
        voting.locationLine.hide()
        voting.admitButton.hide()
        players = get_player_nicknames(game_info['name'])
        del players[players.index(game_info['nick'])]
        if len(players) == 1:
            voting.candidate1.setText(players[0])
            voting.candidate2.hide()
            voting.candidate3.hide()
            voting.candidate4.hide()
        elif len(players) == 2:
            voting.candidate1.setText(players[0])
            voting.candidate2.setText(players[1])
            voting.candidate3.hide()
            voting.candidate4.hide()
        elif len(players) == 3:
            voting.candidate1.setText(players[0])
            voting.candidate2.setText(players[1])
            voting.candidate3.setText(players[2])
            voting.candidate4.hide()
        elif len(players) == 4:
            voting.candidate1.setText(players[0])
            voting.candidate2.setText(players[1])
            voting.candidate3.setText(players[2])
            voting.candidate4.setText(players[3])


def distribute_roles_and_locations():
    global game
    players = get_player_nicknames(game_info['name'])
    spy = random.choice(players)
    location = random.choice(locations)
    change_location(game_info['name'], location)
    change_game_role(game_info['name'], spy, 'spy')
    if spy == game_info['nick']:
        game.labelAddition.setText('Вычислите локацию пока у вас есть время!')
        game.labelAddition_2.setText('Локация: ???')
    else:
        game.labelAddition_2.setText(f'Локация: {location}')


def set_the_local_timer():
    timer = '2:30'
    start_time = int(round(time(), 0))
    end_time = start_time + int(timer[0]) * 60 + int(timer[2:])
    secs = str(int(end_time - time()) % 60)
    if len(secs) == 1:
        secs = '0' + secs
    timer = str(int(end_time - time()) // 60) + ':' + secs
    while timer != '0:00':
        secs = str(int(end_time - time()) % 60)
        if len(secs) == 1:
                secs = '0' + secs
        timer = str(int(end_time - time()) // 60) + ':' + secs
        game.labelTimer.setText(timer)
        sleep(1)
    if get_server_role(game_info['name'], game_info['nick']) == 'host':
        change_game_status(game_info['name'], 'time_up')
    else:
        while get_game_status(game_info['name'], game_info['nick']) != 'time_up':
            sleep(1)
    prepare_to_vote()
    move_forward(1)


def close_all_threads():
    global if_check_game, if_refresh_slots
    if get_server_role(game_info['name'], game_info['nick']) == 'host':
        drop_lobby(game_info['name'])
    if_check_game, if_refresh_slots = False, False


def check_game_status(name: str, nickname: str):
    sleep(3)
    while if_check_game:
        status = get_game_status(name, nickname)
        if status == 'started':
            local_timer = Thread(target=set_the_local_timer)
            local_timer.start()
            if get_game_role(game_info['name'], game_info['nick']) == 'spy':
                game.labelAddition.setText('Вычислите локацию пока у вас есть время!')
                game.labelAddition_2.setText('Локация: ???')
            else:
                game.labelAddition_2.setText(f'Локация: {get_location(game_info["name"], game_info["nick"])}')
            move_forward(1)
            break
        sleep(1)


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


''' Создание окон '''


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
            lobby.labelLobbyname.setText(game_info['name'])
            global t1, if_refresh_slots, if_check_game
            if_refresh_slots, if_check_game = True, True
            slot_refreshing = Thread(target=list_refresh, args=(lobby,))
            slot_refreshing.start()
            sleep(0.5)
            if get_server_role(game_info['name'], game_info['nick']) != 'host':
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
        global if_refresh_slots
        if_refresh_slots = False
        distribute_roles_and_locations()
        change_game_status(game_info['name'], 'started')
        local_timer = Thread(target=set_the_local_timer)
        local_timer.start()
        move_forward(1)


class Game(QMainWindow):
    def __init__(self):
        super(Game, self).__init__()
        loadUi("screens/game.ui", self)


class Voting(QMainWindow):
    def __init__(self):
        super(Voting, self).__init__()
        loadUi("screens/voting.ui", self)
        self.candidate1.clicked.connect(self.cd1)
        self.candidate2.clicked.connect(self.cd2)
        self.candidate3.clicked.connect(self.cd3)
        self.candidate4.clicked.connect(self.cd4)
        self.admitButton.clicked.connect(self.done)

    def cd1(self):
        votes_increase(game_info['name'], self.candidate1.text())
        change_ready_status(game_info['name'], game_info['nick'])
        vote_made()

    def cd2(self):
        votes_increase(game_info['name'], self.candidate2.text())
        change_ready_status(game_info['name'], game_info['nick'])
        vote_made()

    def cd3(self):
        votes_increase(game_info['name'], self.candidate3.text())
        change_ready_status(game_info['name'], game_info['nick'])
        vote_made()

    def cd4(self):
        votes_increase(game_info['name'], self.candidate4.text())
        change_ready_status(game_info['name'], game_info['nick'])
        vote_made()

    def done(self):
        change_ready_status(game_info['name'], game_info['nick'])
        players = get_player_nicknames(game_info['name'])
        for nickname in players:
            make_suggestion(game_info['name'], self.locationLine.text(), nickname)
        vote_made()


class Results(QMainWindow):
    def __init__(self):
        super(Results, self).__init__()
        loadUi("screens/results.ui", self)
        self.exitButton.clicked.connect(self.end)

    def end(self):
        sys.exit()


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
game = Game()
voting = Voting()
results = Results()
font = QFont('20665')
widget.setFont(font)
widget.setWindowTitle('Spy')
widget.addWidget(mainWindow)
widget.addWidget(serverName)
widget.addWidget(lobby)
widget.addWidget(game)
widget.addWidget(voting)
widget.addWidget(results)
widget.setFixedSize(800, 600)
widget.show()

''' Завершение работы программы '''

try:
    sys.exit(app.exec_())
except:
    print('Exiting')
