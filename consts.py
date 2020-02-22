from telebot.types import InlineKeyboardButton as But
from telebot.types import InlineKeyboardMarkup as Mark


def _callback(*args):
    return "$".join([str(i) for i in args])


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
