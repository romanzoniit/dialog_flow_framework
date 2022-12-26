# %% [markdown]
"""
# 12. No Pipeline Advanced

This example demonstrates how to connect to Telegram without the `pipeline` API.

This shows how you can integrate command and button reactions into your script.
As in other cases, you only need one handler, since the logic is handled by the actor
and the script.
"""


# %%
import os
from typing import Optional

import dff.script.conditions as cnd
from dff.script import Context, Actor, TRANSITIONS, RESPONSE

from telebot import types
from telebot.util import content_type_media

from dff.messengers.telegram import TelegramMessenger, TELEGRAM_KEY
from dff.utils.testing.common import is_interactive_mode

db = dict()  # You can use any other context storage from the library.

bot = TelegramMessenger(os.getenv("TG_BOT_TOKEN", "SOMETOKEN"))


# %% [markdown]
"""
You can handle various values inside your script:

* Use `bot.cnd.message_handler` to create conditions for message values.
* Use `bot.cnd.callback_query_handler` to create conditions depending on the query values.

The signature of these functions is equivalent to the signature of the `telebot` methods.
"""


# %%
script = {
    "root": {
        "start": {
            RESPONSE: "",
            TRANSITIONS: {
                ("general", "keyboard"): cnd.true(),
            },
        },
        "fallback": {
            RESPONSE: "Finishing test, send /restart command to restart",
            TRANSITIONS: {
                ("general", "keyboard"): bot.cnd.message_handler(commands=["start", "restart"])
            },
        },
    },
    "general": {
        "keyboard": {
            RESPONSE: {
                "message": "What's 2 + 2?",
                "markup": {
                    0: {"text": "4", "callback_data": "4"},
                    1: {"text": "5", "callback_data": "5"},
                },
            },
            TRANSITIONS: {
                ("general", "success"): bot.cnd.callback_query_handler(
                    func=lambda call: call.data == "4"
                ),
                ("general", "fail"): bot.cnd.callback_query_handler(
                    func=lambda call: call.data == "5"
                ),
            },
        },
        "success": {
            RESPONSE: {"message": "Success!", "markup": None},
            TRANSITIONS: {("root", "fallback"): cnd.true()},
        },
        "fail": {
            RESPONSE: {"message": "Incorrect answer, try again", "markup": None},
            TRANSITIONS: {("general", "keyboard"): cnd.true()},
        },
    },
}


# %%
actor = Actor(script, start_label=("root", "start"), fallback_label=("root", "fallback"))


# %%
def get_markup(data: Optional[dict]):
    if not data:
        return None
    markup = types.InlineKeyboardMarkup(row_width=2)
    for key, item in data.items():
        markup.add(types.InlineKeyboardButton(**item))
    return markup


# %% [markdown]
"""
If you need to work with callback queries or other types
of queries, you can stack decorators upon the main handler.
"""


# %%
@bot.callback_query_handler(func=lambda call: True)
@bot.message_handler(func=lambda msg: True, content_types=content_type_media)
def handler(update):

    # retrieve or create a context for the user
    user_id = (vars(update).get("from_user")).id
    context: Context = db.get(user_id, Context(id=user_id))
    # add update
    context.framework_states[TELEGRAM_KEY] = update
    context.add_request(getattr(update, "text", "No text"))

    # apply the actor
    context = actor(context)

    # save the context
    db[user_id] = context

    response = context.last_response
    if isinstance(response, str):
        bot.send_message(update.from_user.id, response)
    elif isinstance(response, dict):
        bot.send_message(
            update.from_user.id, response["message"], reply_markup=get_markup(response["markup"])
        )


if __name__ == "__main__" and is_interactive_mode():  # prevent run during doc building
    if not os.getenv("TG_BOT_TOKEN"):
        print("`TG_BOT_TOKEN` variable needs to be set to use TelegramInterface.")
    bot.infinity_polling()