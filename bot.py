import telebot
import requests
import os
from pymongo import MongoClient
import utils_global
from utils_global import (
    TOKEN,
    uri,
    extract_arg,
    heroku_check,
    kat,
    log,
    admin_id,
)

myclient = MongoClient(uri)
mydb = myclient["userdb"]
users = mydb["users"]
papug = mydb["papug"]
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def start(message):
    if message.chat.type == "private":
        log(message)
        is_user = users.find_one({"_id": message.from_user.id})
        if str(is_user) == "None":
            users.insert_one(
                {
                    "_id": message.from_user.id,
                    "username": message.from_user.username,
                    "fname": message.from_user.first_name,
                    "ban": 0,
                    "small": 0,
                }
            )
            key = utils_global.small(1)
            bot.reply_to(message, utils_global.txtstart, reply_markup=key)
        else:
            if is_user["ban"] == 0:
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
                if is_user["small"] == 0:
                    data = utils_global.small(1)
                else:
                    data = utils_global.small(0)
                bot.reply_to(
                    message,
                    "Вы уже подписаны на обновления бота",
                    reply_markup=data,
                )
    else:
        bot.reply_to(message, "Works only in private chats")


@bot.message_handler(commands=["papuga"])
def ppuga(message):
    if message.chat.type == "private":
        log(message)
        is_user = users.find_one({"_id": message.from_user.id})
        if str(is_user) == "None":
            users.insert_one(
                {
                    "_id": message.from_user.id,
                    "username": message.from_user.username,
                    "fname": message.from_user.first_name,
                    "ban": 0,
                    "small": 0,
                }
            )
        else:
            if is_user["ban"] == 0:
                for i in papug.aggregate([{"$sample": {"size": 1}}]):
                    id = i["id2"]
                    try:
                        bot.send_photo(message.chat.id, id)
                    except:
                        continue
    else:
        bot.reply_to(message, "Works only in private chats")


"""
@bot.message_handler(commands=["minesweeper"])
def size_menu1(message):
    findlist = ulist.find_one({"_id": message.from_user.id})
    if str(findlist) == "None" and str(message.from_user.id) != bot_id:

"""


@bot.callback_query_handler(lambda query: "small" in query.data)
def smallq(call):
    val = int(call.data[5])
    users.update_one({"_id": call.from_user.id}, {"$set": {"small": val}})
    if val == 1:
        text = "Вы подписались на новости о небольших фиксах"
    else:
        text = "Вы отписались от новостей о небольших фиксах"
    bot.answer_callback_query(
        callback_query_id=call.id, text=text, show_alert=1
    )


# ADMIN
#
@bot.message_handler(commands=["ban"])
def ban(message):
    if str(message.from_user.id) == utils_global.admin_id:
        argument = extract_arg(message.text)
        for i in argument:
            usr = int(i)
            is_user = users.find_one({"_id": usr})
            if str(is_user) != "None":
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
                if is_user["ban"] == 0:
                    users.update_one({"_id": usr}, {"$set": {"ban": 1}})
                    name = is_user["fname"]
                    uname = is_user["username"]
                    bot.reply_to(
                        message, f"User |{name}|{i}|{uname} has banned"
                    )
                else:
                    bot.reply_to(message, "User already banned")
            else:
                bot.reply_to(message, "User not found")
    else:
        bot.reply_to(message, "Restricted area")


@bot.message_handler(commands=["unban"])
def unban(message):
    if str(message.from_user.id) == utils_global.admin_id:
        argument = extract_arg(message.text)
        for i in argument:
            usr = int(i)
            is_user = users.find_one({"_id": usr})
            if str(is_user) != "None":
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
                if is_user["ban"] == 1:
                    users.update_one({"_id": usr}, {"$set": {"ban": 0}})
                    name = is_user["fname"]
                    uname = is_user["username"]
                    bot.reply_to(
                        message, f"User |{name}|{i}|{uname} has unbanned"
                    )
                else:
                    bot.reply_to(message, "User not banned")
            else:
                bot.reply_to(message, "User not found")
    else:
        log(message)
        bot.reply_to(message, "Restricted area")


@bot.message_handler(commands=["mass"])
def mass(message):
    if str(message.from_user.id) == utils_global.admin_id:
        argument = extract_arg(message.text)
        txt = " ".join(argument)
        cursor = users.find({})
        for i in cursor:
            if int(i["ban"]) == 0:
                try:
                    bot.send_message(int(i["_id"]), txt, parse_mode="markdown")
                except:
                    name = i["fname"]
                    uname = i["username"]
                    id = i["_id"]
                    bot.send_message(
                        admin_id,
                        f"Error sending message to |{name}|{id}|{uname}|",
                    )
                    continue
    else:
        log(message)
        bot.reply_to(message, "Restricted area")


@bot.message_handler(commands=["massmall"])
def massmall(message):
    if str(message.from_user.id) == utils_global.admin_id:
        argument = extract_arg(message.text)
        txt = " ".join(argument)
        cursor = users.find({})
        for i in cursor:
            if int(i["ban"]) == 0:
                if int(i["small"]) == 1:
                    try:
                        bot.send_message(
                            int(i["_id"]), txt, parse_mode="markdown"
                        )
                    except:
                        print(i)
                        continue
    else:
        log(message)
        bot.reply_to(message, "Restricted area")


@bot.message_handler(commands=["masstest"])
def masstest(message):
    if str(message.from_user.id) == utils_global.admin_id:
        argument = extract_arg(message.text)
        txt = " ".join(argument)
        bot.send_message(utils_global.admin_id, txt, parse_mode="markdown")
    else:
        log(message)
        bot.reply_to(message, "Restricted area")


@bot.message_handler(commands=["write"])
def writemessage(message):
    if str(message.from_user.id) == utils_global.admin_id:
        argument = extract_arg(message.text)
        usr = int(argument[0])
        del argument[0]
        txt = " ".join(argument)
        is_user = users.find_one({"_id": usr})
        if str(is_user) != "None":

            try:
                bot.send_message(id, txt, parse_mode="markdown")
            except:
                print(id)
                pass
        else:
            bot.reply_to(message, "User not found")
    else:
        bot.reply_to(message, "Restricted area")


@bot.message_handler(content_types=["photo"])
def papuga(message):
    if (
        str(message.from_user.id) == utils_global.admin_id
        or str(message.from_user.id) == kat
    ):
        file_id = message.photo[-1].file_id
        response = requests.get(
            f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}"
        )
        unique = response.json()["result"]["file_unique_id"]
        find = papug.find_one({"_id": str(unique)})
        if str(find) == "None":
            bot.send_photo(
                -1001477733398, file_id, file_id,
            )
            papug.insert_one({"_id": str(unique), "id2": str(file_id)})


@bot.message_handler(content_types=["text"])
def frwrd(message):
    if message.chat.type == "private":
        is_user = users.find_one({"_id": message.from_user.id})
        if str(is_user) != "None":
            if int(is_user["ban"]) == 0:
                log(message)
                name = is_user["fname"]
                uname = is_user["username"]
                bot.send_message(
                    admin_id,
                    message.text
                    + f"\nName:{name}\nId:{message.from_user.id}\nUsername:{uname}",
                )


#
# ADMIN


if heroku_check():
    from flask import Flask, request

    server = Flask(__name__)

    @server.route("/" + TOKEN, methods=["POST"])
    def getMessage():
        bot.process_new_updates(
            [
                telebot.types.Update.de_json(
                    request.stream.read().decode("utf-8")
                )
            ]
        )
        return "!", 200

    @server.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url=str(utils_global.url) + TOKEN)
        return "!", 200

    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
    bot.remove_webhook()
    bot.polling(none_stop=True)
