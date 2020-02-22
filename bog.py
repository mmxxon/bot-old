import telebot
import os
from utils import bog, TOKEN, heroku_check
import handlers


if heroku_check():
    from flask import Flask, request

    server = Flask(__name__)

    @server.route("/" + TOKEN, methods=["POST"])
    def getMessage():
        bog.process_new_updates(
            [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))]
        )

        return "!", 200

    @server.route("/")
    def webhook():
        bog.remove_webhook()
        bog.set_webhook(url=str(url) + TOKEN)
        return "!", 200

    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
    bog.remove_webhook()
    bog.polling(none_stop=True)
