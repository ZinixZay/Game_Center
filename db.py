import psycopg2
import datetime
from config import *


sql = psycopg2.connect(
    database=db_name,
    user=user_name,
    password=password,
    host=host,
    port=port
)

cur = sql.cursor()


def execute(com: str):
    cur.execute(com)
    sql.commit()


def catch_request(request: dict) -> dict:
    nickname = request['nickname']
    name = request['name']
    answer = dict()
    if request['status'] == 'host':
        answer = create_lobby(name, nickname, request['status'])
    elif request['status'] == 'connect':
        answer = join_lobby(name, nickname, request['status'])
    return answer


def create_lobby(name: str = 'def', nickname: str = "def", role: str = 'def') -> dict:
    try:
        command = f"CREATE TABLE {name}" \
                  f"(" \
                  f"Id SERIAL PRIMARY KEY," \
                  f"name CHARACTER VARYING(30)," \
                  f"role CHARACTER VARYING(20) DEFAULT ('player')," \
                  f"server_role CHARACTER VARYING(10)," \
                  f"location CHARACTER VARYING(30)," \
                  f"status CHARACTER VARYING(15) DEFAULT ('waiting')," \
                  f"votes CHARACTER VARYING(2) DEFAULT ('0')," \
                  f"ready CHARACTER VARYING(3) DEFAULT ('no')," \
                  f"done CHARACTER VARYING(5) DEFAULT ('no')," \
                  f"suggestion CHARACTER VARYING(30) DEFAULT ('no'))"
        execute(command)
    except Exception:
        content = 'Упс! Произошла ошибка. Скорее всего лобби с таким названием уже существует. ' \
                  'Пожалуйста, перезапустите приложение'
        return {'status': 'error', 'content': content}
    command = f"INSERT INTO {name} (name, server_role) VALUES ('{nickname}', '{role}')"
    execute(command)
    return {'status': 'ok', 'nick': nickname, 'name': name}


def join_lobby(name: str = 'def', nickname: str = 'def', role: str = 'def') -> dict:
    try:
        nicknames = list()
        cur.execute(f"SELECT name FROM {name}")
        for nick in cur.fetchall():
            nicknames.append(nick[0])
    except Exception:
        content = 'Упс! Произошла ошибка. Скорее всего лобби с таким названием не существует'
        return {'status': 'error', 'content': content}
    if nickname in nicknames:
        content = 'Упс! Произошла ошибка. Скорее всего игрок с таким ником уже вошел в лобби'
        return {'status': 'error', 'content': content}
    command = f"INSERT INTO {name} (name, server_role) VALUES ('{nickname}', '{role}')"
    execute(command)
    global playable_nick
    playable_nick = nickname
    return {'status': 'ok', 'nick': nickname, 'name': name}


def get_server_role(name: str, nickname: str) -> str:
    com = f"SELECT server_role FROM {name} WHERE name=('{nickname}')"
    cur.execute(f"SELECT server_role FROM {name} WHERE name=('{nickname}')")
    return next(cur)[0]


def get_player_nicknames(name: str) -> list:
    nicknames = list()
    cur.execute(f"SELECT name FROM {name}")
    for nick in cur.fetchall():
        nicknames.append(nick[0])
    return nicknames


def drop_lobby(name: str):
    com = f"DROP TABLE {name}"
    execute(com)


def leave_player(name: str, nickname: str):
    com = f"DELETE FROM {name} WHERE name=('{nickname}')"
    execute(com)


def get_game_status(name: str, nickname: str):
    com = f"SELECT status FROM {name} WHERE name=('{nickname}')"
    cur.execute(com)
    return next(cur)[0]


def change_game_status(name: str, val: str):
    com = f"UPDATE {name} SET status='{val}'"
    execute(com)


def change_game_role(name: str, nick: str, val: str):
    com = f"UPDATE {name} SET role='{val}' WHERE name=('{nick}')"
    execute(com)


def change_location(name: str, val: str):
    com = f"UPDATE {name} SET location='{val}'"
    execute(com)


def get_location(name: str, nick: str):
    com = f"SELECT location FROM {name} WHERE name=('{nick}')"
    cur.execute(com)
    return next(cur)[0]


def get_game_role(name: str, nickname: str):
    com = f"SELECT role FROM {name} WHERE name=('{nickname}')"
    cur.execute(com)
    return next(cur)[0]


def votes_increase(name: str, nickname: str):
    com = f"SELECT votes FROM {name} WHERE name=('{nickname}')"
    cur.execute(com)
    ch = str(int(next(cur)[0]) + 1)
    com = f"UPDATE {name} SET votes='{ch}' WHERE name=('{nickname}')"
    execute(com)


def change_ready_status(name: str, nickname: str):
    com = f"UPDATE {name} SET ready='yes' WHERE name=('{nickname}')"
    execute(com)


def get_ready_status(name: str, nickname: str):
    com = f"SELECT ready FROM {name} WHERE name=('{nickname}')"
    cur.execute(com)
    return next(cur)[0]


def end_game(name: str):
    com = f"UPDATE {name} SET done='yes'"
    execute(com)


def is_end_game(name: str, nickname: str):
    com = f"SELECT done FROM {name} WHERE name=('{nickname}')"
    cur.execute(com)
    return next(cur)[0]


def make_suggestion(name: str, val: str, nickname: str):
    com = f"UPDATE {name} SET suggestion='{val}' WHERE name=('{nickname}')"
    execute(com)


def get_votes(name: str, nickname: str):
    com = f"SELECT votes FROM {name} WHERE name=('{nickname}')"
    cur.execute(com)
    return next(cur)[0]


def get_suggestion(name: str, nickname: str):
    com = f"SELECT suggestion FROM {name} WHERE name=('{nickname}')"
    cur.execute(com)
    return next(cur)[0]


def get_spy(name: str):
    com = f"SELECT name FROM {name} WHERE role=('spy')"
    cur.execute(com)
    return next(cur)[0]