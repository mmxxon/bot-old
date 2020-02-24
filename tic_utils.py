from consts import MARKUP
import consts
import utils
from utils import bog, users, log, tictac
from telebot.types import InlineKeyboardMarkup as Mark
import random


def empty_field():
    field = []
    for i in range(3):
        for j in range(3):
            field.append({"n": i, "m": j, "val": None})
    return field


def invite(usr1id, usr2id, usr2):
    if usr1id == usr2id:
        task = bog.send_message(usr1id, "Много друзей, ага?")
        task.wait()
    bog.send_message(
        usr1id,
        f"Послать приглашение @{usr2}?",
        reply_markup=Mark().row(
            MARKUP.GAME("ticinvite$yes", "ДА", usr2id),
            MARKUP.GAME("ticinvite$no", "НЕТ", usr2id),
        ),
    )


def start(message):
    if utils.chat_test(message.chat.id, message.chat.username) != 0:
        return
    if message.chat.username is None:
        bog.reply_to(
            message, "Многопользовательские игры не работают с пользователями без ников"
        )
        return
    arg = utils.extract_arg(message.text)
    if len(arg) == 0:
        bog.send_message(message.chat.id, consts.ticrules, parse_mode="html")
    elif len(arg) > 1:
        bog.reply_to(message, "Это не похоже на имя пользователя")
    else:
        if not (
            tictac.find_one({"_id": message.chat.id})
            or tictac.find_one({"_id2": message.chat.id})
        ):
            enemy = list(arg[0])
            if enemy[0] == "@":
                del enemy[0]
            enemy = "".join(enemy)
            find = users.find_one({"n": enemy})
            if not find:
                bog.reply_to(
                    message,
                    "Не найден пользователь в базе."
                    + " Возможно, данные противника в базе устаревшие",
                )
                return
            enemy_id = int(find["_id"])
            if not (
                tictac.find_one({"_id": enemy_id}) or tictac.find_one({"_id2": enemy_id})
            ):
                invite(message.chat.id, enemy_id, enemy)
            else:
                bog.reply_to(
                    message,
                    "У вашего противника найдена незавершенная игра\n"
                    + "Он должен ее завершить/удалить прежде, чем продолжить",
                )

        elif tictac.find_one({"_id": message.chat.id}):
            type = tictac.find_one({"_id": message.chat.id})["m"]
            if int(type) == 2:
                text = "ваше отправленное приглашение"
            else:
                text = "вашу прошлую игру с"
            enemyid = tictac.find_one({"_id": message.chat.id})["_id2"]
            enemy = users.find_one({"_id": enemyid})["n"]
            bog.reply_to(message, f"Найдено {text} @{enemy}")
        elif tictac.find_one({"_id2": message.chat.id}):
            type = tictac.find_one({"_id2": message.chat.id})["m"]
            if int(type) == 2:
                text = "ваше отправленное приглашение"
            else:
                text = "вашу прошлую игру с"
            enemyid = tictac.find_one({"_id2": message.chat.id})["_id"]
            enemy = users.find_one({"_id": enemyid})["n"]
            bog.reply_to(message, f"Найдено {text} @{enemy}")


def begin_game(find):
    bog.edit_message_text("Begin", int(find["_id"]), int(find["mid"]))
    bog.edit_message_text("Begin2", int(find["_id2"]), int(find["mid2"]))
    move = random.randint(0, 1)
    field = empty_field()
    tictac.update_one(find, {"$set": {"m": move, "fm": move, "field": field}})
    find = tictac.find_one({"_id": find["_id"]})
    print(find)
    tictac.delete_one(find)


"""
    if int(find["fm"]) == 0:
        keyfirst =
        first(int(find["_id"]), int(find["mid"]))
        second(int(find["_id2"]), int(find["mid2"]))
    else:
        first(int(find["_id2"]), int(find["mid2"]))
        second(int(find["_id"]), int(find["mid"]))


def first(id, mid):
    try:
        bog.edit_message_text("Ваш ход", id, mid)
    except:
        bog.send_message(id, "Ваш ход")


def second(id, mid):
    try:
        bog.edit_message_text("Ожидаем хода противника", id, mid)
    except:
        bog.send_message(id, "Ожидаем хода противника")
"""
