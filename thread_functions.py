from db import *


def list_refresh(lobby):
    global game_info
    name = game_info['name']
    while 1:
        players = get_player_nicknames(name)
        for i in players:
            already_in = [lobby.labelSlot1.text(),
                          lobby.labelSlot2.text(),
                          lobby.labelSlot3.text(),
                          lobby.labelSlot4.text(),
                          lobby.labelSlot5.text()]
            if i in already_in:
                continue
            if lobby.labelSlot1.text() not in players:
                lobby.labelSlot1.setText(i)
                continue
            if lobby.labelSlot2.text() not in players:
                lobby.labelSlot2.setText(i)
                continue
            if lobby.labelSlot3.text() not in players:
                lobby.labelSlot3.setText(i)
                continue
            if lobby.labelSlot4.text() not in players:
                lobby.labelSlot4.setText(i)
                continue
            if lobby.labelSlot5.text() not in players:
                lobby.labelSlot5.setText(i)
                continue
        sleep(2)