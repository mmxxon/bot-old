import os
import telebot
from datetime import datetime
import pytz
from pymongo import MongoClient
import time


def html_message(
    datetime,
    textm,
    ctype,
    cid,
    cusername,
    name,
    lname,
    username,
    id,
    text,
    data,
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


def heroku_check():
    r"""
    true if app has deployed on heroku
    """
    return "HEROKU" in list(os.environ.keys())


if heroku_check():
    TOKEN = os.environ["TOKEN"]
    url = os.environ["URL"]
    admin_id = os.environ["ID"]
    uri = os.environ["MONGODB_URI"]
    bot_id = os.environ["BOT_ID"]
    kat = os.environ["Kat"]
    group1 = os.environ["GR1"]
    group2 = os.environ["GR2"]
else:
    import config

    uri = config.mongouri
    TOKEN = config.token
    admin_id = config.admin_id
    bot_id = config.bot_id
    group1 = config.group1
    group2 = config.group2
    kat = config.kat


bot = telebot.AsyncTeleBot(TOKEN)


def update_info(is_user, message, users):
    if is_user["username"] != message.from_user.username:
        users.update_one(
            {"_id": message.from_user.id},
            {"$set": {"username": message.from_user.username}},
        )
    if is_user["fname"] != message.from_user.first_name:
        users.update_one(
            {"_id": message.from_user.id},
            {"$set": {"username": message.from_user.first_name}},
        )


def log(message):
    if (
        str(message.from_user.id) != bot_id
        and str(message.from_user.id) != admin_id
    ):
        kyiv = pytz.timezone("Europe/Kiev")
        kyiv_time = kyiv.localize(datetime.now())
        timen = kyiv_time.strftime("%d %B %Y %H:%M:%S")
        html = html_message(
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
        bot.send_message(group1, html, parse_mode="html")


def log_call(call):
    if str(call.from_user.id) != admin_id:
        kyiv = pytz.timezone("Europe/Kiev")
        kyiv_time = kyiv.localize(datetime.now())
        timen = kyiv_time.strftime("%d %B %Y %H:%M:%S")
        html = html_message(
            timen,
            "CALL",
            call.message.chat.type,
            call.message.chat.id,
            call.message.chat.username,
            call.from_user.first_name,
            call.from_user.last_name,
            call.from_user.username,
            call.from_user.id,
            call.message.text,
            call.data,
        )
        bot.send_message(group2, html, parse_mode="html")


def small(i):
    if int(i) == 1:
        text = "Подписаться на новости о небольших фиксах"
    else:
        text = "Отписаться от новостей о небольших фиксах"
    button = telebot.types.InlineKeyboardButton(
        text=text, callback_data="small" + str(i),
    )
    return telebot.types.InlineKeyboardMarkup().row(button)


# argument calls
def extract_arg(arg):
    return arg.split()[1:]


#

# vars
txtstart = f"<b>Вы подписались на обновления бота</b>\nВсе крупные обновления будут сопровождаться оповещениями (не чаще раза в неделю). По кнопке ниже можно подписаться и на сообщения о небольших фиксах (не чаще раза в день)\n\n<b>Бот может</b>:\n- Показать папужку: /papuga\n- Создать игру в сапёр /minesweeper\n- Показать статистику из сапера /stats\n- (Новое скоро)"
#
