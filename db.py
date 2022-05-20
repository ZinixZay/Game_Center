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
                  f"role CHARACTER VARYING(20)," \
                  f"server_role CHARACTER VARYING(10)," \
                  f"location CHARACTER VARYING(30)," \
                  f"status BOOLEAN DEFAULT (false))"
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
