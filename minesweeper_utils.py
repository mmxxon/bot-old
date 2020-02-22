from consts import MARKUP
import consts
import utils
from utils import saper, bog, users
from telebot.types import InlineKeyboardMarkup as Mark


def mine(message):
    if utils.chat_test(message.chat.id, message.chat.username) != 0:
        return

    start(message)


def start(message):
    if not saper.find_one({"_id": message.chat.id}):
        if message.from_user.id != utils.bot_id:
            bog.send_message(
                message.chat.id, "Выбери размер поля🗺", reply_markup=MARKUP.MINE
            ),
        else:
            bog.edit_message_text(
                "Выбери размер поля🗺",
                message.chat.id,
                message.message_id,
                reply_markup=MARKUP.MINE,
            )
    else:
        bog.send_message(
            message.chat.id,
            "Была найдена ваша предыдущая игра в этом чате."
            + "Вы можете начать новую или продолжить незавершенную",
            reply_markup=MARKUP.UNFINISHED,
        )


def empty(size):
    field = []
    for i in range(size):
        for j in range(size):
            field.append(
                {"n": i, "m": j, "around": 0, "mine": 0, "open": 0, "flag": 0, "found": 0}
            )
    return field


def around(field, size, n, m):
    c = size * n + m
    cmine = 0
    if n != 0 and m != 0:
        if field[c - size - 1]["mine"] == 1:
            cmine += 1
    if n != 0:
        if field[c - size]["mine"] == 1:
            cmine += 1
    if n != 0 and m != size - 1:
        if field[c - size + 1]["mine"] == 1:
            cmine += 1
    if m != size - 1:
        if field[c + 1]["mine"] == 1:
            cmine += 1
    if n != size - 1 and m != size - 1:
        if field[c + size + 1]["mine"] == 1:
            cmine += 1
    if n != size - 1:
        if field[c + size]["mine"] == 1:
            cmine += 1
    if n != size - 1 and m != 0:
        if field[c + size - 1]["mine"] == 1:
            cmine += 1
    if m != 0:
        if field[c - 1]["mine"] == 1:
            cmine += 1
    return cmine


def endboard(size, field):
    keyboard = Mark(size)
    for i in range(size):
        rows = []
        for j in range(size):
            if field[i * size + j]["mine"] == 1:
                text = "💣"
            else:
                if field[i * size + j]["around"] == 0:
                    text = "0️⃣"
                elif field[i * size + j]["around"] == 1:
                    text = "1️⃣"
                elif field[i * size + j]["around"] == 2:
                    text = "2⃣"
                elif field[i * size + j]["around"] == 3:
                    text = "3⃣"
                elif field[i * size + j]["around"] == 4:
                    text = "4⃣"
                elif field[i * size + j]["around"] == 5:
                    text = "5⃣"
                elif field[i * size + j]["around"] == 6:
                    text = "6⃣"
                elif field[i * size + j]["around"] == 7:
                    text = "7⃣"
                elif field[i * size + j]["around"] == 8:
                    text = "8⃣"
            rows.append(MARKUP.GAME("OK", text))
        keyboard.row(*rows)
    return keyboard


def lostreply(call, size, field):
    keyboard = endboard(size, field)
    bog.answer_callback_query(
        callback_query_id=call.id, text="Попробуй еще раз🕹", show_alert=1,
    )
    users.update_one(
        {"_id": call.message.chat.id}, {"$inc": {"won": 0, "lost": 1, "points": 0}},
    )
    saper.delete_one({"_id": call.message.chat.id})
    keyboard.row(MARKUP.NEWGAME_B)
    cid = call.message.chat.id
    mid = call.message.message_id
    bog.edit_message_text(
        chat_id=cid, message_id=mid, text="Попробуй еще раз🕹", reply_markup=keyboard,
    )


def winreply(call, size, field):
    keyboard = endboard(size, field)
    bog.answer_callback_query(
        callback_query_id=call.id, text=f"🏆Победа! +{size} очков🏆", show_alert=1
    )
    users.update_one(
        {"_id": call.message.chat.id}, {"$inc": {"won": 1, "lost": 0, "points": size}},
    )
    saper.delete_one({"_id": call.message.chat.id})
    button = MARKUP.NEWGAME_B
    keyboard.row(button)
    bog.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="🏆Победа!🏆",
        reply_markup=keyboard,
    )


def opengame(field, size, n, m):
    c = n * size + m
    field[c]["open"] = 1
    field[c]["found"] = 1
    if field[n * size + m]["around"] == 0:
        if n != 0 and m != 0:
            field[c - size - 1]["open"] = 1
            field[c - size - 1]["flag"] = 0
            if field[c - size - 1]["found"] != 1:
                opengame(field, size, n - 1, m - 1)
        if n != 0:
            field[c - size]["open"] = 1
            field[c - size]["flag"] = 0
            if field[c - size]["found"] != 1:
                opengame(field, size, n - 1, m)
        if n != 0 and m != size - 1:
            field[c - size + 1]["open"] = 1
            field[c - size + 1]["flag"] = 0
            if field[c - size + 1]["found"] != 1:
                opengame(field, size, n - 1, m + 1)
        if m != size - 1:
            field[c + 1]["open"] = 1
            field[c + 1]["flag"] = 0
            if field[c + 1]["found"] != 1:
                opengame(field, size, n, m + 1)
        if n != size - 1 and m != size - 1:
            field[c + size + 1]["open"] = 1
            field[c + size + 1]["flag"] = 0
            if field[c + size + 1]["found"] != 1:
                opengame(field, size, n + 1, m + 1)
        if n != size - 1:
            field[c + size]["open"] = 1
            field[c + size]["flag"] = 0
            if field[c + size]["found"] != 1:
                opengame(field, size, n + 1, m)
        if n != size - 1 and m != 0:
            field[c + size - 1]["open"] = 1
            field[c + size - 1]["flag"] = 0
            if field[c + size - 1]["found"] != 1:
                opengame(field, size, n + 1, m - 1)
        if m != 0:
            field[c - 1]["open"] = 1
            field[c - 1]["flag"] = 0
            if field[c - 1]["found"] != 1:
                opengame(field, size, n, m - 1)


def board(size, field):
    keyboard = Mark(size)
    for i in range(size):
        rows = []
        for j in range(size):
            if field[i * size + j]["flag"] == 1:
                text = "🚩"
                type = "OK"
                data = type
            elif field[i * size + j]["open"] == 0:
                text = "⚫️"
                type = "tap"
                data = consts._callback(size, i, j)
            elif field[i * size + j]["mine"] == 1:
                text = "💣"
                type = "OK"
            else:
                if field[i * size + j]["around"] == 0:
                    text = "0️⃣"
                elif field[i * size + j]["around"] == 1:
                    text = "1️⃣"
                elif field[i * size + j]["around"] == 2:
                    text = "2️⃣"
                elif field[i * size + j]["around"] == 3:
                    text = "3️⃣"
                elif field[i * size + j]["around"] == 4:
                    text = "4️⃣"
                elif field[i * size + j]["around"] == 5:
                    text = "5️⃣"
                elif field[i * size + j]["around"] == 6:
                    text = "6️⃣"
                elif field[i * size + j]["around"] == 7:
                    text = "7️⃣"
                elif field[i * size + j]["around"] == 8:
                    text = "8️⃣"
                type = "OK"
                data = type
            rows.append(MARKUP.GAME(type, text, data))
        keyboard.row(*rows)
    keyboard.row(MARKUP.MODE1)
    return keyboard


def mark(size, field):
    keyboard = Mark(size)
    for i in range(size):
        rows = []
        for j in range(size):
            if field[i * size + j]["flag"] == 1:
                text = "🚩"
                type = "mark"
                data = consts._callback("remove", i, j)
            elif field[i * size + j]["open"] == 0:
                text = "⚫️"
                type = "mark"
                data = consts._callback("add", i, j)
            elif field[i * size + j]["mine"] == 1:
                text = "💣"
                data = "OK"
                type = data
            else:
                if field[i * size + j]["around"] == 0:
                    text = "0️⃣"
                elif field[i * size + j]["around"] == 1:
                    text = "1️⃣"
                elif field[i * size + j]["around"] == 2:
                    text = "2️⃣"
                elif field[i * size + j]["around"] == 3:
                    text = "3️⃣"
                elif field[i * size + j]["around"] == 4:
                    text = "4️⃣"
                elif field[i * size + j]["around"] == 5:
                    text = "5️⃣"
                elif field[i * size + j]["around"] == 6:
                    text = "6️⃣"
                elif field[i * size + j]["around"] == 7:
                    text = "7️⃣"
                elif field[i * size + j]["around"] == 8:
                    text = "8️⃣"
                data = "OK"
                type = data
            rows.append(MARKUP.GAME(type, text, data))
        keyboard.row(*rows)
    keyboard.row(MARKUP.MODE2)
    return keyboard
