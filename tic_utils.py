from consts import MARKUP
import consts
import utils
from utils import bog, users, log, tictac
from telebot.types import InlineKeyboardMarkup as Mark
import random


def whowon(field):
    if field[0]["val"] == field[1]["val"] == field[2]["val"] is not None:
        return 1
    elif field[3]["val"] == field[4]["val"] == field[5]["val"] is not None:
        return 1
    elif field[6]["val"] == field[7]["val"] == field[8]["val"] is not None:
        return 1
    elif field[0]["val"] == field[3]["val"] == field[6]["val"] is not None:
        return 1
    elif field[1]["val"] == field[4]["val"] == field[7]["val"] is not None:
        return 1
    elif field[2]["val"] == field[5]["val"] == field[8]["val"] is not None:
        return 1
    elif field[0]["val"] == field[4]["val"] == field[8]["val"] is not None:
        return 1
    elif field[2]["val"] == field[4]["val"] == field[6]["val"] is not None:
        return 1
    else:
        return 0


def call_batya(call):
    admin = users.find_one({"_id": utils.admin_id})["n"]
    bog.edit_message_text(
        f"Error. Напишите @{admin} если это произошло",
        call.message.chat.id,
        call.message.message_id,
    )


def empty_field():
    field = []
    for i in range(3):
        for j in range(3):
            field.append({"n": i, "m": j, "val": None})
    return field


def invite(usr1id, usr2id, usr2):
    if usr1id == usr2id:
        # bog.send_message(usr1id, "Много друзей, ага?")
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
    log(message)
    if message.chat.username is None:
        bog.reply_to(
            message, "Многопользовательские игры не работают с пользователями без ников"
        )
        return
    arg = utils.extract_arg(message.text)
    if len(arg) == 0:
        bog.send_message(message.chat.id, consts.ticrules, parse_mode="markdown")
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
            enemy_id = find["_id"]
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
            bog.reply_to(
                message, f"Найдено {text} @{enemy}", reply_markup=MARKUP.SURRENDER
            )
        elif tictac.find_one({"_id2": message.chat.id}):
            type = tictac.find_one({"_id2": message.chat.id})["m"]
            if int(type) == 2:
                text = "ваше отправленное приглашение"
            else:
                text = "вашу прошлую игру с"
            enemyid = tictac.find_one({"_id2": message.chat.id})["_id"]
            enemy = users.find_one({"_id": enemyid})["n"]
            bog.reply_to(
                message, f"Найдено {text} @{enemy}", reply_markup=MARKUP.SURRENDER
            )


def begin_game(find):
    move = random.randint(0, 1)
    field = empty_field()
    tictac.update_one(find, {"$set": {"m": move, "fm": move, "field": field}})
    find = tictac.find_one({"_id": find["_id"]})
    if move == 0:
        first = find["_id"]
        second = find["_id2"]
        fm = find["mid"]
        sm = find["mid2"]
    else:
        first = find["_id2"]
        second = find["_id"]
        fm = find["mid2"]
        sm = find["mid"]
    bog.edit_message_text(
        "Begin", first, fm, reply_markup=MARKUP.KEYFIRST(field),
    )
    bog.edit_message_text(
        "Begin2", second, sm, reply_markup=MARKUP.KEYSECOND(field),
    )


def play_game(n, m, find, id, mid):
    if find["fm"] == find["m"]:
        mark = 0
    else:
        mark = 1
    field = find["field"]
    field[3 * n + m]["val"] = mark
    if find["m"] == 0:
        newm = 1
    else:
        newm = 0
    tictac.update_one({"_id": find["_id"]}, {"$set": {"m": newm, "field": field}})
    find = tictac.find_one({"_id": find["_id"]})
    if find["_id"] == id and find["mid"] == mid:
        first = find["_id"]
        second = find["_id2"]
        fm = find["mid"]
        sm = find["mid2"]
    else:
        first = find["_id2"]
        second = find["_id"]
        fm = find["mid2"]
        sm = find["mid"]
    if whowon(field) == 1:
        bog.edit_message_text("You lost", second, sm)
        bog.edit_message_text("You won", first, fm)
        tictac.delete_one(find)
        return
    bog.edit_message_text(
        "Begin", second, sm, reply_markup=MARKUP.KEYFIRST(field),
    )
    bog.edit_message_text(
        "Begin2", first, fm, reply_markup=MARKUP.KEYSECOND(field),
    )
