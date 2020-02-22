import os
import telebot
from pymongo import MongoClient
from consts import MARKUP
import consts
from telebot import types
from datetime import datetime
import pytz
import requests


# Herok
def heroku_check():
    return "HEROKU" in list(os.environ.keys())


if heroku_check():
    TOKEN = os.environ["TOKEN"]
    url = os.environ["URL"]
    admin_id = int(os.environ["ID"])
    uri = os.environ["MONGODB_URI"]
    bot_id = int(os.environ["BOT_ID"])
    kat = os.environ["Kat"]
    group1 = os.environ["GR1"]
    group2 = os.environ["GR2"]
else:
    import config

    admin_id = int(config.admin_id)
    TOKEN = config.token
    uri = config.uri
    bot_id = config.bot_id
    url = config.url

bog = telebot.TeleBot(TOKEN)
servak = MongoClient(uri)
users = servak["userdb"]["users"]
papug = servak["userdb"]["papug"]
saper = servak["userdb"]["minesweeper"]
# vars
#
txtstart = (
    "<b>Вы подписаны на важные обновления бота</b>\n"
    + "Все крупные обновления будут сопровождаться оповещениями (не чаще раза в неделю)."
    + "Кнопкой ниже можно включить/выключить так же остальные оповещения(не чаще раза в день)"
    + "\n\n<b>Бот может</b>:\n"
    + "- Показать папужку: /papuga\n"
    + "- Создать игру в сапёр /minesweeper\n"
    + "- Показать статистику из сапера /stats\n"
    + "- (Новое скоро)"
)

#
# end vars
# GOVNO
#


def log(message):
    if str(message.from_user.id) != bot_id and str(message.from_user.id) != admin_id:
        kyiv = pytz.timezone("Europe/Kiev")
        kyiv_time = kyiv.localize(datetime.now())
        timen = kyiv_time.strftime("%d %B %Y %H:%M:%S")
        html = consts.html_message(
            timen,
            "MESSAGE",
            message.chat.type,
            message.chat.id,
            message.chat.username,
            message.from_user.first_name,
            message.from_user.last_name,
            message.from_user.username,
            message.from_user.id,
            message.text,
            "None",
        )
        bog.send_message(group1, html, parse_mode="html")


def form(message):
    text = message.text
    chat = message.chat.id
    user = message.chat.username
    kyiv = pytz.timezone("Europe/Kiev")
    kyiv_time = kyiv.localize(datetime.now())
    time = kyiv_time.strftime("%d %B %Y %H:%M:%S")
    return f"{text}\n\n" + f"id:{chat}\n" + f"username:{user}\n" + f"time:{time}"


def chat_test(id, name):
    if id < 0:
        return 1

    if not users.find_one({"_id": id}):
        users.insert_one({"_id": id, "n": name})

    elif not users.find_one({"_id": id, "n": name}):
        users.update_one({"_id": id}, {"$set": {"n": name}})

    if users.find_one({"_id": id, "ban": {"$exists": 1}}):
        return 1
    return 0


def extract_arg(arg):
    return arg.split()[1:]


#
# END GOVNA
# UZVERS
#
def start_message(message, markup):
    bog.send_message(
        message.chat.id, txtstart, parse_mode="html", reply_markup=markup,
    )


def start_menu(message):
    if chat_test(message.chat.id, message.chat.username) != 0:
        return
    log(message)
    if users.find_one({"_id": message.chat.id, "small": {"$exists": False}}):
        start_message(message, MARKUP.START)
    else:
        start_message(message, MARKUP.START2)


def papuga(message):
    if chat_test(message.chat.id, message.chat.username) != 0:
        return
    log(message)
    for i in papug.aggregate([{"$sample": {"size": 1}}]):
        id = i["id2"]
        try:
            bog.send_photo(message.chat.id, id)
        except:
            continue


def text(message):
    if chat_test(message.chat.id, message.chat.username) != 0:
        return
    log(message)
    bog.send_message(admin_id, form(message))


#
# END UZVERS
# ODMEN
#
def ban(message):
    arg = extract_arg(message.text)
    if users.find_one({"_id": int(arg[0]), "ban": {"$exists": 0}}):
        users.update_one({"_id": int(arg[0])}, {"$set": {"ban": None}})
        user = users.find_one({"_id": int(arg[0])})["n"]
        bog.send_message(admin_id, f"Забанен @{user}")
    else:
        bog.send_message(admin_id, f"Не найден незабаненный {arg[0]}")


def unban(message):
    arg = extract_arg(message.text)
    if users.find_one({"_id": int(arg[0]), "ban": {"$exists": 1}}):
        users.update_one({"_id": int(arg[0])}, {"$unset": {"ban": 1}})
        user = users.find_one({"_id": int(arg[0])})["n"]
        bog.send_message(admin_id, f"Разбанен @{user}")
    else:
        bog.send_message(admin_id, f"Не найден забаненный {arg[0]}")


def mass(message):
    argument = extract_arg(message.text)
    txt = " ".join(argument)
    cursor = users.find({"ban": {"$exists": 0}})
    for i in cursor:
        try:
            bog.send_message(int(i["_id"]), txt, parse_mode="markdown")
        except:
            uname = i["n"]
            id = i["_id"]
            bog.send_message(
                admin_id, f"Error sending message to |{id}|{uname}|",
            )
            continue


def massmall(message):
    argument = extract_arg(message.text)
    txt = " ".join(argument)
    cursor = users.find({"ban": {"$exists": 1}, "small": {"$exists": 1}})
    for i in cursor:
        try:
            bog.send_message(int(i["_id"]), txt, parse_mode="markdown")
        except:
            uname = i["n"]
            id = i["_id"]
            bog.send_message(
                admin_id, f"Error sending message to |{id}|{uname}|",
            )
            continue


def masstest(message):
    argument = extract_arg(message.text)
    txt = " ".join(argument)
    try:
        bog.send_message(admin_id, txt, parse_mode="markdown")
    except:
        pass


def write(message):
    argument = extract_arg(message.text)
    usr = int(argument[0])
    del argument[0]
    txt = " ".join(argument)
    try:
        bog.send_message(usr, txt, parse_mode="markdown")
    except:
        pass


def papug_insert(message):
    file_id = message.photo[-1].file_id
    response = requests.get(
        f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}"
    )
    unique = response.json()["result"]["file_unique_id"]
    find = papug.find_one({"_id": str(unique)})
    if str(find) == "None":
        bog.send_photo(
            -1001477733398, file_id, file_id,
        )
        papug.insert_one({"_id": str(unique), "id2": str(file_id)})


def dlbase(message):
    arg = extract_arg(message.text)
    file_id = str(arg[0])
    response = requests.get(
        f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}"
    )
    unique = response.json()["result"]["file_unique_id"]
    find = papug.find_one({"_id": str(unique)})
    if str(find) != "None":
        bog.send_photo(
            message.chat.id, file_id, "deleted",
        )
        bog.send_photo(
            admin_id, file_id, "deleted",
        )
        papug.delete_one({"_id": str(unique)})
