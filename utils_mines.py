import os
import telebot
from telebot import types
import utils_global
from pymongo import MongoClient
from utils_global import log, extract_arg

TOKEN = utils_global.TOKEN
uri = utils_global.uri
kat = utils_global.kat
admin_id = utils_global.admin_id
bot_id = utils_global.bot_id

myclient = MongoClient(uri)
mydb = myclient["userdb"]
users = mydb["users"]
papug = mydb["papug"]
dbmine = mydb["minseweeper"]
bot = telebot.AsyncTeleBot(TOKEN)


def start_menu(message):
    if str(message.chat.id) != admin_id:
        log(message)
    find = dbmine.find_one({"user": message.from_user.id})
    if str(find) == "None":
        # Buttons w sizes. Return 's' + choice
        choice = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text="5", callback_data="s5")
        button2 = types.InlineKeyboardButton(text="6", callback_data="s6")
        choice.row(button1, button2)
        button3 = types.InlineKeyboardButton(text="7", callback_data="s7")
        button4 = types.InlineKeyboardButton(text="8", callback_data="s8")
        choice.row(button3, button4)
        if str(message.from_user.id) != bot_id:
            bot.send_message(
                message.chat.id, "Choose size:", reply_markup=choice
            )
        else:
            bot.edit_message_text(
                "Choose size:",
                message.chat.id,
                message.message_id,
                reply_markup=choice,
            )
    else:
        choice = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(
            text="Доиграть прошлую игру", callback_data="prevgame",
        )
        button2 = types.InlineKeyboardButton(
            text="Начать новую игру", callback_data="newgame"
        )
        choice.row(button1, button2)
        bot.send_message(
            message.chat.id,
            "Была найдена ваша предыдущая игра в этом чате. Вы можете начать новую или продолжить незавершенную",
            reply_markup=choice,
        )


def minec(field, size, n, m):
    c = size * n + m
    cmine = 0
    if n != 0 and m != 0:
        if field[c - size - 1]["is_mine"] == 1:
            cmine += 1
    if n != 0:
        if field[c - size]["is_mine"] == 1:
            cmine += 1
    if n != 0 and m != size - 1:
        if field[c - size + 1]["is_mine"] == 1:
            cmine += 1
    if m != size - 1:
        if field[c + 1]["is_mine"] == 1:
            cmine += 1
    if n != size - 1 and m != size - 1:
        if field[c + size + 1]["is_mine"] == 1:
            cmine += 1
    if n != size - 1:
        if field[c + size]["is_mine"] == 1:
            cmine += 1
    if n != size - 1 and m != 0:
        if field[c + size - 1]["is_mine"] == 1:
            cmine += 1
    if m != 0:
        if field[c - 1]["is_mine"] == 1:
            cmine += 1
    print("cmine=", cmine)
    return cmine


def empty_field(size):
    field = []
    for i in range(size):
        for j in range(size):
            field.append(
                {
                    "n": i,
                    "m": j,
                    "is_opened": 0,
                    "is_mine": 0,
                    "is_found": 0,
                    "count_mines": 0,
                    "is_marked": 0,
                }
            )
    return field


def endboard(size, field):
    keyboard = types.InlineKeyboardMarkup(size)
    for i in range(size):
        rows = []
        for j in range(size):
            if field[i * size + j]["is_mine"] == 1:
                text = "💣"
            else:
                if field[i * size + j]["count_mines"] == 0:
                    text = "0️⃣"
                elif field[i * size + j]["count_mines"] == 1:
                    text = "1️⃣"
                elif field[i * size + j]["count_mines"] == 2:
                    text = "2⃣"
                elif field[i * size + j]["count_mines"] == 3:
                    text = "3⃣"
                elif field[i * size + j]["count_mines"] == 4:
                    text = "4⃣"
                elif field[i * size + j]["count_mines"] == 5:
                    text = "5⃣"
                elif field[i * size + j]["count_mines"] == 6:
                    text = "6⃣"
                elif field[i * size + j]["count_mines"] == 7:
                    text = "7⃣"
                elif field[i * size + j]["count_mines"] == 8:
                    text = "8⃣"
            rows.append(
                types.InlineKeyboardButton(text=text, callback_data="OK")
            )
        keyboard.row(*rows)
    return keyboard


def opengame(field, size, n, m):
    c = n * size + m
    field[c]["is_found"] = 1
    if field[c]["count_mines"] == 0:
        if n != 0 and m != 0:
            field[c - size - 1]["is_opened"] = 1
            field[c - size - 1]["is_marked"] = 0
            if field[c - size - 1]["is_found"] != 1:
                opengame(field, size, n - 1, m - 1)
        if n != 0:
            field[c - size]["is_opened"] = 1
            field[c - size]["is_marked"] = 0
            if field[c - size]["is_found"] != 1:
                opengame(field, size, n - 1, m)
        if n != 0 and m != size - 1:
            field[c - size + 1]["is_opened"] = 1
            field[c - size + 1]["is_marked"] = 0
            if field[c - size + 1]["is_found"] != 1:
                opengame(field, size, n - 1, m + 1)
        if m != size - 1:
            field[c + 1]["is_opened"] = 1
            field[c + 1]["is_marked"] = 0
            if field[c + 1]["is_found"] != 1:
                opengame(field, size, n, m + 1)
        if n != size - 1 and m != size - 1:
            field[c + size + 1]["is_opened"] = 1
            field[c + size + 1]["is_marked"] = 0
            if field[c + size + 1]["is_found"] != 1:
                opengame(field, size, n + 1, m + 1)
        if n != size - 1:
            field[c + size]["is_opened"] = 1
            field[c + size]["is_marked"] = 0
            if field[c + size]["is_found"] != 1:
                opengame(field, size, n + 1, m)
        if n != size - 1 and m != 0:
            field[c + size - 1]["is_opened"] = 1
            field[c + size - 1]["is_marked"] = 0
            if field[c + size - 1]["is_found"] != 1:
                opengame(field, size, n + 1, m - 1)
        if m != 0:
            field[c - 1]["is_opened"] = 1
            field[c - 1]["is_marked"] = 0
            if field[c - 1]["is_found"] != 1:
                opengame(field, size, n, m - 1)


def board(size, field):
    keyboard = types.InlineKeyboardMarkup(size)
    c = 0
    for i in range(size):
        rows = []
        for j in range(size):
            if field[c]["is_marked"] == 1:
                text = "🚩"
                data = "OK"
            elif field[c]["is_opened"] == 0:
                text = "⚫️"
                data = str("z" + str(size) + str(i) + str(j))
            elif field[c]["is_mine"] == 1:
                text = "💣"
                data = "OK"
            else:
                if field[i * size + j]["count_mines"] == 0:
                    text = "0️⃣"
                elif field[i * size + j]["count_mines"] == 1:
                    text = "1️⃣"
                elif field[i * size + j]["count_mines"] == 2:
                    text = "2️⃣"
                elif field[i * size + j]["count_mines"] == 3:
                    text = "3️⃣"
                elif field[i * size + j]["count_mines"] == 4:
                    text = "4️⃣"
                elif field[i * size + j]["count_mines"] == 5:
                    text = "5️⃣"
                elif field[i * size + j]["count_mines"] == 6:
                    text = "6️⃣"
                elif field[i * size + j]["count_mines"] == 7:
                    text = "7️⃣"
                elif field[i * size + j]["count_mines"] == 8:
                    text = "8️⃣"
                data = "OK"
            rows.append(
                types.InlineKeyboardButton(text=text, callback_data=data)
            )

            c += 1
        keyboard.row(*rows)
    button = types.InlineKeyboardButton(
        text="Режим игры💣", callback_data="mark+"
    )
    keyboard.row(button)
    return keyboard


def winreply(call, size, field):
    keyboard = endboard(size, field)
    bot.answer_callback_query(
        callback_query_id=call.id, text="🏆Победа!🏆", show_alert=1,
    )
    button = types.InlineKeyboardButton(
        text="Начать новую игру", callback_data="newgame"
    )
    keyboard.row(button)
    cid = call.message.chat.id
    mid = call.message.message_id
    bot.edit_message_text(
        chat_id=cid, message_id=mid, text="🏆Победа!🏆", reply_markup=keyboard,
    )


def mark(size, field):
    keyboard = types.InlineKeyboardMarkup(size)
    c = 0
    for i in range(size):
        rows = []
        for j in range(size):
            if field[c]["is_marked"] == 1:
                text = "🚩"
                data = str("m-" + str(size) + str(i) + str(j))
            elif field[c]["is_opened"] == 0:
                text = "⚫️"
                data = str("m+" + str(size) + str(i) + str(j))
            elif field[c]["is_mine"] == 1:
                text = "💣"
                data = "OK"
                data = str("z" + str(size) + str(i) + str(j))
            else:
                if field[i * size + j]["count_mines"] == 0:
                    text = "0️⃣"
                elif field[i * size + j]["count_mines"] == 1:
                    text = "1️⃣"
                elif field[i * size + j]["count_mines"] == 2:
                    text = "2️⃣"
                elif field[i * size + j]["count_mines"] == 3:
                    text = "3️⃣"
                elif field[i * size + j]["count_mines"] == 4:
                    text = "4️⃣"
                elif field[i * size + j]["count_mines"] == 5:
                    text = "5️⃣"
                elif field[i * size + j]["count_mines"] == 6:
                    text = "6️⃣"
                elif field[i * size + j]["count_mines"] == 7:
                    text = "7️⃣"
                elif field[i * size + j]["count_mines"] == 8:
                    text = "8️⃣"
                data = "OK"
            rows.append(
                types.InlineKeyboardButton(text=text, callback_data=data)
            )
            c += 1
        keyboard.row(*rows)
    button = types.InlineKeyboardButton(
        text="Режим флажков🚩", callback_data="mark-"
    )
    keyboard.row(button)
    return keyboard
