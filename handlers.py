import utils
from utils import bog, users, saper, tictac
import minesweeper_utils
import tic_utils
import random
from consts import MARKUP
from telebot.types import InlineKeyboardMarkup as Mark


@bog.message_handler(commands=["start"])
def start_handler(message):
    utils.start_menu(message)


@bog.message_handler(commands=["papuga"])
def papuga_handler(message):
    utils.papuga(message)


# ADMIN
@bog.message_handler(commands=["ban"])
def ban_handler(message):
    if message.chat.id != utils.admin_id:
        return
    utils.ban(message)


@bog.message_handler(commands=["unban"])
def unban(message):
    if message.chat.id != utils.admin_id:
        return
    utils.unban(message)


@bog.message_handler(commands=["mass"])
def mass_handler(message):
    if message.chat.id != utils.admin_id:
        return
    utils.mass(message)


@bog.message_handler(commands=["massmall"])
def massmall_handler(message):
    if message.chat.id != utils.admin_id:
        return
    utils.massmall(message)


@bog.message_handler(commands=["masstest"])
def masstest_handler(message):
    if message.chat.id != utils.admin_id:
        return
    utils.masstest(message)


@bog.message_handler(commands=["write"])
def writemessage_handler(message):
    if message.chat.id != utils.admin_id:
        return
    utils.write(message)


# END ADMIN
# BASE HELPER
# MINESWEEPER
@bog.message_handler(commands=["minesweeper"])
def minestart_handler(message):
    minesweeper_utils.mine(message)


@bog.message_handler(commands=["stats"])
def stats_handler(message):
    minesweeper_utils.stats(message)


@bog.message_handler(commands=["tic"])
def tic_handler(message):
    tic_utils.start(message)


@bog.message_handler(commands=["dlbase"])
def dlbase_handler(message):
    if message.chat.id != utils.admin_id and message.chat.id != utils.kat:
        return
    utils.dlbase(message)


@bog.message_handler(
    content_types=[
        "audio",
        "photo",
        "voice",
        "video",
        "document",
        "text",
        "location",
        "contact",
        "sticker",
    ],
)
def types_handler(message):
    if message.content_type == "text":
        utils.text(message)
    elif message.content_type == "photo" and (
        message.chat.id == utils.admin_id or message.chat.id == utils.kat
    ):
        utils.papug_insert(message)


# END BASE HELPER


@bog.callback_query_handler(func=lambda query: True)
def query_handler(call):
    if utils.chat_test(call.message.chat.id, call.message.chat.username) != 0:
        return

    arr = call.data.split("$")
    if arr[0] == "subscribe":  # STARTOVAYA PODPIS`KA
        if arr[1] == "plus":
            users.update_one({"_id": call.message.chat.id}, {"$set": {"small": None}})
            bog.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Вы подписались на все новости о боте",
            )
        elif arr[1] == "minus":
            users.update_one({"_id": call.message.chat.id}, {"$unset": {"small": 1}})
            bog.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Теперь вам будут приходить только крупные обновления бота",
            )
    elif arr[0] == "size":  # RAZMER POLYANY
        size = int(arr[1])
        field = minesweeper_utils.empty(size)
        minbomb = int(size * size / 8)
        maxbomb = int(size * size / 4)
        # random mines from +-normal range
        mines = random.randint(minbomb, maxbomb)
        minefield = random.sample(field, mines)
        for i in range(len(field)):
            for j in range(len(minefield)):
                if field[i] == minefield[j]:
                    field[i]["mine"] = 1
        for i in range(size):
            for j in range(size):
                field[i * size + j]["around"] = minesweeper_utils.around(
                    field, size, i, j
                )
        bog.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Чтобы переключиться между режимом флажков🚩 и обычным💣 нажми кнопку внизу",
            reply_markup=minesweeper_utils.board(size, field),
        )
        if not saper.find_one({"_id": call.message.chat.id}):
            user = {
                "message": call.message.message_id,
                "_id": call.message.chat.id,
                "size": size,
                "field": field,
            }
            saper.insert_one(user)
    elif arr[0] == "tap":  # NOZHATIE
        find = saper.find_one({"_id": call.message.chat.id})
        if not find:
            bog.edit_message_text(
                "Игра не найдена", call.message.chat.id, call.message.message_id,
            )
            return

        if call.message.message_id != find["message"]:
            bog.edit_message_text(
                "Игра доступна только в том сообщении, где была запущена. Используйте "
                + "/minesweeper чтобы переместить ее в самое последнее сообщение",
                call.message.chat.id,
                call.message.message_id,
            )
            return

        size = int(arr[1])
        n = int(arr[2])
        m = int(arr[3])
        field = find["field"]
        field[n * size + m]["open"] = 1
        field[n * size + m]["found"] = 1
        if field[n * size + m]["mine"] == 1 and field[n * size + m]["open"] == 1:
            minesweeper_utils.lostreply(call, size, field)
            return
        if field[n * size + m]["around"] == 0:
            minesweeper_utils.opengame(field, size, n, m)
        opened = 0
        minecounter = 0
        for i in range(len(field)):
            if field[i]["open"] == 0:
                opened += 1
            if field[i]["mine"] == 1:
                minecounter += 1
        if opened == minecounter:
            minesweeper_utils.winreply(call, size, field)
            saper.delete_one({"_id": call.message.chat.id})
            return
        keyboard = minesweeper_utils.board(size, field)
        bog.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Чтобы переключиться между режимом флажков🚩 и обычным💣 нажми кнопку внизу",
            reply_markup=keyboard,
        )
        saper.update_one(
            {"_id": call.message.chat.id}, {"$set": {"field": field}},
        )
    elif arr[0] == "mark":  # FLAJOCHECK
        find = saper.find_one({"_id": call.message.chat.id})
        if not find:
            return
        field = find["field"]
        size = int(find["size"])
        if arr[1] == "plus":
            keyboard = minesweeper_utils.mark(size, field)
        elif arr[1] == "minus":
            keyboard = minesweeper_utils.board(size, field)
        elif arr[1] == "add":
            x = int(arr[2])
            y = int(arr[3])
            c = x * size + y
            field[c]["flag"] = 1
            saper.update_one(
                {"_id": call.message.chat.id}, {"$set": {"field": field}},
            )
            keyboard = minesweeper_utils.mark(size, field)
        elif arr[1] == "remove":
            x = int(call.data[2])
            y = int(call.data[3])
            c = x * size + y
            field = find["field"]
            field[c]["flag"] = 0
            saper.update_one(
                {"_id": call.message.chat.id}, {"$set": {"field": field}},
            )
            keyboard = minesweeper_utils.mark(size, field)
        bog.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Чтобы переключиться между режимом флажков🚩 и обычным💣 нажми кнопку внизу",
            reply_markup=keyboard,
        )
    elif arr[0] == "foundgame":  # NOVAYA - STARAYA GAYME
        find = saper.find_one({"_id": call.message.chat.id})
        if arr[1] == "new":
            try:
                bog.delete_message(call.message.chat.id, int(find["message"]))
            except:
                pass
            if not find:
                minesweeper_utils.start(call.message)
            if saper.find_one({"_id": call.message.chat.id}):
                saper.delete_one({"_id": call.message.chat.id})
            minesweeper_utils.mine(call.message)
        elif arr[1] == "prev":
            if not find:
                return
            try:
                bog.delete_message(call.message.chat.id, int(find["message"]))
            except:
                pass
            find["message"] = call.message.message_id
            saper.update_one(
                {"_id": call.message.chat.id},
                {"$set": {"message": call.message.message_id}},
            )
            field = find["field"]
            size = int(find["size"])
            keyboard = minesweeper_utils.board(size, field)
            bog.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Чтобы переключиться между режимом флажков и обычным нажми кнопку внизу",
                reply_markup=keyboard,
            )
    elif arr[0] == "clearmine":  # PROCHISTKA
        if arr[1] == "first":
            bog.edit_message_text(
                "Точно?",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=MARKUP.CLEAR_MINE_STAT_2,
            )
        elif arr[1] == "second":
            users.update_one(
                {"_id": call.message.chat.id},
                {"$unset": {"lost": 1, "points": 1, "won": 1}},
            )
            bog.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="OK",
            )
        elif arr[1] == "clret":
            bog.delete_message(call.message.chat.id, call.message.message_id)
            minesweeper_utils.stats(call.message)
    elif arr[0] == "ticinvite":
        if arr[1] == "yes":
            if tictac.find_one({"_id": int(arr[2])}) or tictac.find_one(
                {"_id2": int(arr[2])}
            ):
                bog.edit_message_text(
                    "Возможно, приглашение/игра уже существует\n",
                    call.message.chat.id,
                    call.message.message_id,
                )
                return
            try:
                bog.send_message(
                    int(arr[2]),
                    f"Приглашение от @{call.message.chat.username} в крестики-нолики",
                    reply_markup=Mark().row(
                        MARKUP.GAME("ticinvite$accept", "ДА", call.message.chat.id),
                        MARKUP.GAME("ticinvite$decline", "НЕТ", call.message.chat.id),
                    ),
                )
            except Exception as e:
                print(e)
                bog.edit_message_text(
                    "Неудачно. Возможно бот заблокирован у пользователя",
                    call.message.chat.id,
                    call.message.message_id,
                )
                return
            bog.edit_message_text(
                "Ожидаем ответ игрока", call.message.chat.id, call.message.message_id
            )
            tictac.insert_one(
                {
                    "_id": call.message.chat.id,
                    "_id2": int(arr[2]),
                    "m": 2,
                    "mid": call.message.message_id,
                }
            )
        elif arr[1] == "no":
            bog.edit_message_text("ОК", call.message.chat.id, call.message.message_id)
        elif arr[1] == "decline":
            find = tictac.find_one({"_id2": call.message.chat.id})
            if not find:
                bog.edit_message_text("Ок", call.message.chat.id, call.message.message_id)
                return
            tictac.delete_one({"_id2": call.message.chat.id})
            bog.send_message(
                int(find["_id"]),
                f"Игрок @{call.message.chat.username} отклонил приглашение",
                parse_mode="markdown",
            )
            bog.edit_message_text(
                "Приглашение отклонено", call.message.chat.id, call.message.message_id
            )
        elif arr[1] == "accept":
            find = tictac.find_one({"_id2": call.message.chat.id})
            if not find:
                admin = users.find_one({"_id": utils.admin_id})["n"]
                bog.edit_message_text(f"Error. Напишите @{admin} если это произошло")
            tictac.update_one(
                {"_id2": call.message.chat.id},
                {"$set": {"mid2": call.message.message_id}},
            )
            find = tictac.find_one({"_id2": call.message.chat.id})
            tic_utils.begin_game(find)
        else:
            bog.answer_callback_query(call.id, call.data)
    elif arr[0] == "OK":  # NIHOOYA
        bog.answer_callback_query(call.id, "Not changed")
    else:  # OCHEN NIHOOYA
        bog.answer_callback_query(call.id, call.data)
