from telebot.types import InlineKeyboardButton as But
from telebot.types import InlineKeyboardMarkup as Mark


def _callback(*args):
    return "$".join([str(i) for i in args])


txtstart = (
    "<b>Вы подписаны на важные обновления бота</b>\n"
    + "Все крупные обновления будут сопровождаться"
    + " оповещениями (не чаще раза в неделю)."
    + "Кнопкой ниже можно включить/выключить так же"
    + " остальные оповещения(не чаще раза в день)"
    + "\n\n<b>Бот может</b>:\n"
    + "- Показать папужку: /papuga\n"
    + "- Создать игру в сапёр /minesweeper\n"
    + "- Показать статистику из сапера /stats\n"
    + "- (Новое скоро)"
)

ticrules = (
    "* Правила телеграмм версии крестиков -ноликов*\n"
    + "1)Чтобы начать игру нужно ввести юзернейм игрока,"
    + " которого нужно пригласить в игру "
    + "так: \n`/tic @username` или `/tic username`.\n"
    + "Игрок должен предварительно написать боту любое сообщение "
    + "(чтобы бот мог ему написать)\n"
    + "2)Простивник должен одобрить запрос в личке бота\n"
    + "3)После этого случайный игрок станет первым (крестиком)\n"
    + "4)Игра завершается, когда:\n"
    + "- 1.Не остается свободных клеток\n"
    + "- 2.Один из игроков собирает три знака в ряд\n"
    + "- 3.Один из игроков отменит игру (сдастся)\n\n"
    + "Кстати команда `/tic` никак не связана с одноименным"
    + " предметом. Это сокращение от "
    + "[Tic-tac-toe](https://en.wikipedia.org/wiki/Tic-tac-toe)"
)


def html_message(
    datetime, textm, name, lname, username, id, text, data,
):
    return f"""
<b>NEW {textm}</b>
<b>TIME</b>: <code>{datetime}</code>
<b>USER</b>
- First: |<code>{name}</code>|
- Last:  |<code>{lname}</code>|
- Username: @{username}
- ID: <code>{id}</code>
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
    SEND_TIC_INVITE = Mark().row(
        But("Да", None, _callback("ticinvite", "yes")),
        But("Нет", None, _callback("ticinvite", "no")),
    )
    ACCEPT_TIC_INVITE = Mark().row(
        But("Принять", None, _callback("ticinvite", "accept")),
        But("Отклонить", None, _callback("ticinvite", "decline")),
    )

    def SURRENDER(val):
        keyboard = Mark().row(But("Сдаться", None, _callback("ticsurrender", val)))
        return keyboard

    def KEYFIRST(field):
        size = 3
        keyboard = Mark(size)
        for i in range(size):
            rows = []
            for j in range(size):
                cell = field[size * i + j]
                if cell["val"] == 0:
                    text = "❌"
                    type = "OK"
                    data = type
                elif cell["val"] == 1:
                    text = "⭕️"
                    type = "OK"
                    data = type
                elif cell["val"] is None:
                    text = "⚫️"
                    type = "ticlick"
                    data = _callback(i, j)
                rows.append(MARKUP.GAME(type, text, data))
            keyboard.row(*rows)
        return keyboard

    def KEYSECOND(field):
        keyboard = Mark()
        for i in range(3):
            rows = []
            for j in range(3):
                cell = field[3 * i + j]
                if cell["val"] == 0:
                    text = "❌"
                elif cell["val"] == 1:
                    text = "⭕️"
                elif cell["val"] is None:
                    text = "⚫️"
                type = "OK"
                data = type
                rows.append(MARKUP.GAME(type, text, data))
            keyboard.row(*rows)
        return keyboard
