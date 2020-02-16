import telebot
from telebot import types
import requests
import os
from pymongo import MongoClient
import utils_global
import utils_mines
from utils_global import heroku_check, extract_arg, log, log_call
import random

TOKEN = utils_global.TOKEN
uri = utils_global.uri
kat = utils_global.kat
admin_id = utils_global.admin_id
bot_id = utils_global.bot_id

myclient = MongoClient(uri)
mydb = myclient["userdb"]
users = mydb["users"]
papug = mydb["papug"]
dbmine = mydb["minesweeper"]
bot = telebot.AsyncTeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def start(message):
    is_user = users.find_one({"_id": message.chat.id})
    if str(is_user) == "None":
        users.insert_one(
            {
                "_id": message.chat.id,
                "username": message.from_user.username,
                "fname": message.from_user.first_name,
                "ban": 0,
                "small": 0,
            }
        )
        key = utils_global.small(1)
        bot.reply_to(message, utils_global.txtstart, reply_markup=key)
    elif is_user["ban"] == 0:
        if message.chat.type == "private":
            utils_global.update_info(is_user, message, users)
            if is_user["small"] == 0:
                data = utils_global.small(1)
            else:
                data = utils_global.small(0)
            bot.reply_to(
                message,
                "Вы уже подписаны на обновления бота",
                reply_markup=data,
            )
            log(message)
        else:
            bot.reply_to(message, "Works only in private chats")


@bot.message_handler(commands=["papuga"])
def ppuga(message):
    is_user = users.find_one({"_id": message.chat.id})
    if str(is_user) == "None":
        users.insert_one(
            {
                "_id": message.chat.id,
                "username": message.from_user.username,
                "fname": message.from_user.first_name,
                "ban": 0,
                "small": 0,
            }
        )
    elif is_user["ban"] == 0:
        if message.chat.type == "private":
            for i in papug.aggregate([{"$sample": {"size": 1}}]):
                id = i["id2"]
                try:
                    bot.send_photo(message.chat.id, id)
                except:
                    continue
            log(message)
        else:
            bot.reply_to(message, "Works only in private chats")


@bot.callback_query_handler(lambda query: "small" in query.data)
def smallq(call):
    val = int(call.data[5])
    users.update_one({"_id": call.message.chat.id}, {"$set": {"small": val}})
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
                utils_global.update_info(is_user, message, users)
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
                utils_global.update_info(is_user, message, users)
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
        bot.reply_to(message, "Restricted area")
        log(message)


@bot.message_handler(commands=["massmall"])
def massmall(message):
    if str(message.from_user.id) == utils_global.admin_id:
        argument = extract_arg(message.text)
        txt = " ".join(argument)
        cursor = users.find({})
        for i in cursor:
            if int(i["ban"]) == 0 and int(i["small"]) == 1:
                try:
                    bot.send_message(int(i["_id"]), txt, parse_mode="markdown")
                except:
                    print(i)
                    continue
    else:
        bot.reply_to(message, "Restricted area")
        log(message)


@bot.message_handler(commands=["masstest"])
def masstest(message):
    if str(message.from_user.id) == utils_global.admin_id:
        argument = extract_arg(message.text)
        txt = " ".join(argument)
        bot.send_message(utils_global.admin_id, txt, parse_mode="markdown")
    else:
        bot.reply_to(message, "Restricted area")
        log(message)


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


#
# ADMIN
# -----
# MINESWEEPER
#


@bot.message_handler(commands=["minesweeper"])
def minestart(message):
    is_user = users.find_one({"_id": message.chat.id})
    if str(is_user) == "None":
        users.insert_one(
            {
                "_id": message.chat.id,
                "username": message.from_user.username,
                "fname": message.from_user.first_name,
                "ban": 0,
                "small": 0,
            }
        )
    is_user = users.find_one({"_id": message.chat.id})
    if is_user["ban"] == 0:
        if message.chat.type == "private":
            utils_global.update_info(is_user, message, users)
            find = dbmine.find_one({"_id": message.chat.id})
            if str(find) == "None":
                # Buttons w sizes.
                choice = types.InlineKeyboardMarkup()
                button1 = types.InlineKeyboardButton(
                    text="5", callback_data="s5"
                )
                button2 = types.InlineKeyboardButton(
                    text="6", callback_data="s6"
                )
                choice.row(button1, button2)
                button3 = types.InlineKeyboardButton(
                    text="7", callback_data="s7"
                )
                button4 = types.InlineKeyboardButton(
                    text="8", callback_data="s8"
                )
                choice.row(button3, button4)  # RETURN "S"
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
                    text="Доиграть прошлую игру",
                    callback_data="prevgame",  # RETURN "Prevgame"
                )
                button2 = types.InlineKeyboardButton(
                    text="Начать новую игру",
                    callback_data="newgame",  # RETURN "NEWGAME"
                )
                choice.row(button1, button2)
                bot.send_message(
                    message.chat.id,
                    "Была найдена ваша предыдущая игра в этом чате. Вы можете начать новую или продолжить незавершенную",
                    reply_markup=choice,
                )
        else:
            bot.reply_to(message, "Works only in private chats")


@bot.callback_query_handler(lambda query: "s" in query.data)
def fieldbegin(call):
    is_user = users.find_one({"_id": call.message.chat.id})
    if str(is_user) == "None":
        users.insert_one(
            {
                "_id": call.message.chat.id,
                "username": call.from_user.username,
                "fname": call.from_user.first_name,
                "ban": 0,
                "small": 0,
            }
        )
    is_user = users.find_one({"_id": call.message.chat.id})
    if is_user["ban"] == 0:
        # Takes size from callback
        size = int(call.data[1])
        field = utils_mines.empty_field(size)
        minbomb = int(size * size / 8)
        maxbomb = int(size * size / 4)
        # random mines from +-normal range
        mines = random.randint(minbomb, maxbomb)
        # generating field w mines
        minefield = random.sample(field, mines)
        for i in range(len(field)):
            for j in range(len(minefield)):
                if field[i] == minefield[j]:
                    field[i]["is_mine"] = 1
        c = 0
        for i in range(size):
            for j in range(size):
                field[c]["count_mines"] = utils_mines.minec(field, size, i, j)
                c += 1
        keyboard = utils_mines.board(size, field)
        cid = call.message.chat.id
        mid = call.message.message_id
        bot.edit_message_text(
            chat_id=cid,
            message_id=mid,
            text="Чтобы переключиться между режимом флажков🚩 и обычным💣 нажми кнопку внизу",
            reply_markup=keyboard,
        )
        find = dbmine.find_one({"_id": call.message.chat.id})
        if str(find) == "None":
            user = {"message": mid, "_id": cid, "size": size, "field": field}
            dbmine.insert_one(user)
        log_call(call)


@bot.callback_query_handler(lambda query: query.data == "mark+")
def mark_on(call):
    is_user = users.find_one({"_id": call.message.chat.id})
    if str(is_user) == "None":
        users.insert_one(
            {
                "_id": call.message.chat.id,
                "username": call.from_user.username,
                "fname": call.from_user.first_name,
                "ban": 0,
                "small": 0,
            }
        )
    is_user = users.find_one({"_id": call.message.chat.id})
    if is_user["ban"] == 0:
        find = dbmine.find_one({"_id": call.from_user.id})
        if str(find) != "None":
            field = find["field"]
            size = find["size"]
            keyboard = utils_mines.mark(size, field)
            cid = call.message.chat.id
            mid = call.message.message_id
            bot.edit_message_text(
                chat_id=cid,
                message_id=mid,
                text="Чтобы переключитusersься между режимом флажков🚩 и обычным💣 нажми кнопку внизу",
                reply_markup=keyboard,
            )

            # log_call(call)


@bot.callback_query_handler(lambda query: query.data == "mark-")
def mark_off(call):
    is_user = users.find_one({"_id": call.message.chat.id})
    if str(is_user) == "None":
        users.insert_one(
            {
                "_id": call.message.chat.id,
                "username": call.from_user.username,
                "fname": call.from_user.first_name,
                "ban": 0,
                "small": 0,
            }
        )
    is_user = users.find_one({"_id": call.message.chat.id})
    if is_user["ban"] == 0:
        find = dbmine.find_one({"_id": call.from_user.id})
        if str(find) != "None":
            field = find["field"]
            size = find["size"]
            keyboard = utils_mines.board(size, field)
            cid = call.message.chat.id
            mid = call.message.message_id
            bot.edit_message_text(
                chat_id=cid,
                message_id=mid,
                text="Чтобы переключиться между режимом флажков🚩 и обычным💣 нажми кнопку внизу",
                reply_markup=keyboard,
            )
            # log_call(call)


@bot.callback_query_handler(lambda query: "m+" in query.data)
def markplus(call):
    is_user = users.find_one({"_id": call.message.chat.id})
    if str(is_user) == "None":
        users.insert_one(
            {
                "_id": call.message.chat.id,
                "username": call.from_user.username,
                "fname": call.from_user.first_name,
                "ban": 0,
                "small": 0,
            }
        )
    is_user = users.find_one({"_id": call.message.chat.id})
    if is_user["ban"] == 0:
        find = dbmine.find_one({"_id": call.message.chat.id})
        if str(find) != "None":
            size = int(call.data[2])
            x = int(call.data[3])
            y = int(call.data[4])
            c = x * size + y
            field = find["field"]
            field[c]["is_marked"] = 1
            dbmine.update_one(
                {"_id": call.message.chat.id}, {"$set": {"field": field}},
            )
            keyboard = utils_mines.mark(size, field)
            bot.edit_message_text(
                "Чтобы переключиться между режимом флажков🚩 и обычным💣 нажми кнопку внизу",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard,
            )


@bot.callback_query_handler(lambda query: "z" in query.data)
def fieldgame(call):
    is_user = users.find_one({"_id": call.message.chat.id})
    if str(is_user) == "None":
        users.insert_one(
            {
                "_id": call.message.chat.id,
                "username": call.from_user.username,
                "fname": call.from_user.first_name,
                "ban": 0,
                "small": 0,
            }
        )
    is_user = users.find_one({"_id": call.message.chat.id})
    if is_user["ban"] == 0:
        find = dbmine.find_one({"_id": call.message.chat.id})
        if call.message.message_id != find["message"]:
            bot.edit_message_text(
                "Use last message from chat or run /minesweeper to play",
                call.message.chat.id,
                call.message.message_id,
            )
        else:
            size = int(call.data[1])
            x = int(call.data[2])
            y = int(call.data[3])
            if str(find) != "None":
                field = find["field"]
                field[x * size + y]["is_opened"] = 1
                if (
                    field[x * size + y]["is_mine"] == 1
                    and field[x * size + y]["is_opened"] == 1
                ):
                    keyboard = utils_mines.endboard(size, field)
                    bot.answer_callback_query(
                        callback_query_id=call.id,
                        text="Попробуй еще раз🕹",
                        show_alert=1,
                    )
                    dbmine.delete_one({"_id": call.message.chat.id})
                    button = types.InlineKeyboardButton(
                        text="Начать новую игру", callback_data="newgame"
                    )
                    keyboard.row(button)
                    cid = call.message.chat.id
                    mid = call.message.message_id
                    bot.edit_message_text(
                        chat_id=cid,
                        message_id=mid,
                        text="Попробуй еще раз🕹",
                        reply_markup=keyboard,
                    )
                else:
                    nopened = 0
                    minecounter = 0
                    for i in range(len(field)):
                        if field[i]["is_opened"] == 0:
                            nopened += 1
                        if field[i]["is_mine"] == 1:
                            minecounter += 1
                    if nopened == minecounter:
                        utils_mines.winreply(call, size, field)
                        dbmine.delete_one({"_id": call.message.chat.id})
                    else:
                        utils_mines.opengame(field, size, x, y)
                        nopened = 0
                        minecounter = 0
                        for i in range(len(field)):
                            if field[i]["is_opened"] == 0:
                                nopened += 1
                            if field[i]["is_mine"] == 1:
                                minecounter += 1
                        if nopened == minecounter:
                            utils_mines.winreply(call, size, field)
                            dbmine.delete_one({"_id": call.message.chat.id})
                        else:
                            keyboard = utils_mines.board(size, field)
                            cid = call.message.chat.id
                            mid = call.message.message_id
                            bot.edit_message_text(
                                chat_id=cid,
                                message_id=mid,
                                text="Чтобы переключиться между режимом флажков🚩 и обычным💣 нажми кнопку внизу",
                                reply_markup=keyboard,
                            )
                            find = dbmine.find_one(
                                {"_id": call.message.chat.id}
                            )
                            dbmine.update_one(
                                {"_id": call.message.chat.id},
                                {"$set": {"field": field}},
                            )
            else:
                bot.edit_message_text(
                    "ERROR", call.message.chat.id, call.message.message_id
                )
        log_call(call)


@bot.callback_query_handler(lambda query: "m-" in query.data)
def markminus(call):
    is_user = users.find_one({"_id": call.message.chat.id})
    if str(is_user) == "None":
        users.insert_one(
            {
                "_id": call.message.chat.id,
                "username": call.from_user.username,
                "fname": call.from_user.first_name,
                "ban": 0,
                "small": 0,
            }
        )
    is_user = users.find_one({"_id": call.message.chat.id})
    if is_user["ban"] == 0:
        find = dbmine.find_one({"_id": call.message.chat.id})
        if str(find) != "None":
            size = int(call.data[2])
            x = int(call.data[3])
            y = int(call.data[4])
            c = x * size + y
            field = find["field"]
            field[c]["is_marked"] = 0
            dbmine.update_one(
                {"_id": call.message.chat.id}, {"$set": {"field": field}},
            )
            keyboard = utils_mines.mark(size, field)
            bot.edit_message_text(
                "Чтобы переключиться между режимом флажков🚩 и обычным💣 нажми кнопку внизу",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard,
            )


@bot.callback_query_handler(lambda query: query.data == "prevgame")
def prev_game(call):
    is_user = users.find_one({"_id": call.message.chat.id})
    if str(is_user) == "None" and call.from_user.id != bot_id:
        users.insert_one(
            {
                "_id": call.message.chat.id,
                "username": call.from_user.username,
                "fname": call.from_user.first_name,
                "ban": 0,
                "small": 0,
            }
        )
    if is_user["ban"] == 0:
        find = dbmine.find_one({"_id": call.from_user.id})
        find["message"] = call.message.message_id
        dbmine.update_one(
            {"_id": call.message.chat.id},
            {"$set": {"message": call.message.message_id}},
        )
        field = find["field"]
        size = find["size"]
        keyboard = utils_mines.board(size, field)  # ->BOARD
        cid = call.message.chat.id
        mid = call.message.message_id
        bot.edit_message_text(
            chat_id=cid,
            message_id=mid,
            text="Чтобы переключиться между режимом флажков и обычным нажми кнопку внизу",
            reply_markup=keyboard,
        )
        log_call(call)


@bot.callback_query_handler(lambda query: query.data == "newgame")
def new_game(call):
    is_user = users.find_one({"_id": call.message.chat.id})
    if str(is_user) == "None":
        users.insert_one(
            {
                "_id": call.message.chat.id,
                "username": call.from_user.username,
                "fname": call.from_user.first_name,
                "ban": 0,
                "small": 0,
            }
        )
    is_user = users.find_one({"_id": call.message.chat.id})
    if is_user["ban"] == 0:
        if is_user["ban"] == 0:
            dbmine.delete_one({"_id": call.from_user.id})
            utils_mines.start_menu(call.message)


@bot.callback_query_handler(lambda query: query.data == "OK")
def okay(call):
    is_user = users.find_one({"_id": call.message.chat.id})
    if str(is_user) == "None":
        users.insert_one(
            {
                "_id": call.message.chat.id,
                "username": call.message.chat.username,
                "fname": call.message.chat.first_name,
                "ban": 0,
                "small": 0,
            }
        )
    bot.answer_callback_query(call.id, "Done")
    # log_call(call)


#
# MINESWEEPER
# -----
# Other text


@bot.message_handler(content_types=["text"])
def frwrd(message):
    is_user = users.find_one({"_id": message.chat.id})
    if str(is_user) != "None":
        if int(is_user["ban"]) == 0:
            if message.chat.type == "private":
                name = is_user["fname"]
                uname = is_user["username"]
                bot.send_message(
                    admin_id,
                    message.text
                    + f"\nName:{name}\nId:{message.from_user.id}\nUsername:{uname}",
                )
                log(message)
            else:
                bot.reply_to(
                    message, "Please send message only from private chats"
                )


#
# ------
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
