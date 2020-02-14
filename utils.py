import os
import telebot


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
else:
    import config

    uri = config.mongouri
    TOKEN = config.token
    admin_id = config.admin_id
    bot_id = config.bot_id


txtstart = "Вы подписались на бота. Все крупные обновления будут сопровождаться оповещениями (не чаще раза в неделю). По кнопке ниже можно подписаться и на сообщения о небольших фиксах (не чаще раза в день)"


def small(i):
    if int(i) == 1:
        text = "Подписаться на новости о небольших фиксах"
    else:
        text = "Отписаться от новостей о небольших фиксах"
    button = telebot.types.InlineKeyboardButton(
        text=text, callback_data="small" + str(i),
    )
    return telebot.types.InlineKeyboardMarkup().row(button)


def extract_arg(arg):
    return arg.split()[1:]
