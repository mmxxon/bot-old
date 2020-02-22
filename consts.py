from telebot.types import InlineKeyboardButton as But
from telebot.types import InlineKeyboardMarkup as Mark


def _callback(*args):
    return "$".join([str(i) for i in args])


def html_message(
    datetime, textm, ctype, cid, cusername, name, lname, username, id, text, data,
):
    return f"""
<b>NEW {textm}</b>
<b>TIME</b>: <code>{datetime}</code>
<b>CHAT</b>
- TYPE: <code>{ctype}</code>
- ID: <code>{str(cid)}</code>
- NAME: @{str(cusername)}
<b>USER</b>
- First: |<code>{name}</code>|
- Last:  |<code>{lname}</code>|
- Username: @{str(username)}
- ID: <code>{str(id)}</code>
MESSAGE TEXT: |<code>{text}</code>|
<b>CALL DATA</b>: |<code>{data}</code>|"""


def stattxt(name, won, lost, points):
    all = won + lost
    if won != 0 and lost != 0:
        percent = int((float(won) / float(all)) * 100)
        middle = float(points) / float(all)
    elif won == 0:
        percent = 0
        middle = 0
    elif lost == 0:
        middle = float(points) / float(all)
        percent = 100
    middle = round(middle, 1)
    if 100 >= percent >= 80 and middle >= 5.6:
        txt = "Зе бест👑"
    elif 80 > percent >= 60 and middle >= 3.6:
        txt = "Мощно💪"
    elif 60 > percent >= 40 and middle >= 2:
        txt = "Хороший результат👍"
    else:
        txt = "Можешь лучше🔝"
    return (
        f"<b>Статистика для {name}</b>"
        + f"\n<b>Всего игр</b>: {all}"
        + f"\n<b>Побед</b>: {won}"
        + f"\n<b>Поражений</b>: {lost}"
        + f"\n<b>Процентное соотношение</b>: {percent}%"
        + f"\n<b>Очков</b>: {points}"
        + f"\n<b>В среднем очков за игру</b>: {middle}"
        + f"\n\n{txt}"
    )


# buttons
class MARKUP:
    START = Mark().row(But("Подписаться", None, _callback("subscribe", "plus")))
    START2 = Mark().row(But("Отписаться", None, _callback("subscribe", "minus")))
    MINE = (
        Mark()
        .row(But("5", None, _callback("size", 5)), But("6", None, _callback("size", 6)))
        .row(But("7", None, _callback("size", 7)), But("8", None, _callback("size", 8)),)
    )
    NEWGAME_B = But("Начать новую игру", None, _callback("foundgame", "new"))
    UNFINISHED = Mark().row(
        But("Доиграть прошлую игру", None, _callback("foundgame", "prev")), NEWGAME_B
    )

    def GAME(game, text, data=None):
        return But(text, None, _callback(game, data))

    MODE1 = But("Режим игры💣", None, _callback("mark", "plus"))
    MODE2 = But("Режим флажков🚩", None, _callback("mark", "minus"))
    CLEAR_MINE_STAT = But("Очистить статистику", None, _callback("clearmine", "first"))
    CLEAR_MINE_STAT_2 = Mark().row(
        But("Да", None, _callback("clearmine", "second")),
        But("Нет", None, _callback("clearmine", "clret")),
    )
