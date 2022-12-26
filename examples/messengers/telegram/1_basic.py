# %% [markdown]
"""
# 1. Basic

The following example shows how to run a regular DFF script in Telegram.
This example does not contain any Telegram-specific logic.
"""


# %%
import os

from dff.messengers.telegram import PollingTelegramInterface, TelegramMessenger
from dff.pipeline import Pipeline
from dff.messengers.telegram import update_processing_service
from dff.utils.testing.common import is_interactive_mode
from dff.utils.testing.toy_script import TOY_SCRIPT


# %% [markdown]
"""
In order to integrate your script with Telegram, you need an instance of
`TelegramMessenger` class and one of the following interfaces:
`PollingMessengerInterface` or `WebhookMessengerInterface`.

`TelegramMessenger` encapsulates the bot logic.
Like Telebot, `TelegramMessenger` only requires a token to run.
However, all parameters from the Telebot class can be passed as keyword arguments.

The two interfaces connect the bot to Telegram. They can be passed directly
to the DFF `Pipeline` instance.
"""


# %%
messenger = TelegramMessenger(os.getenv("TG_BOT_TOKEN", "SOMETOKEN"))
interface = PollingTelegramInterface(messenger=messenger)


# %%
pipeline = Pipeline.from_script(
    script=TOY_SCRIPT,  # Actor script object, defined in `.utils` module.
    start_label=("greeting_flow", "start_node"),
    fallback_label=("greeting_flow", "fallback_node"),
    context_storage=dict(),
    pre_services=[update_processing_service],
    messenger_interface=interface,  # The interface can be passed as a pipeline argument.
)


if __name__ == "__main__" and is_interactive_mode():  # prevent run during doc building
    if not os.getenv("TG_BOT_TOKEN"):
        print("`TG_BOT_TOKEN` variable needs to be set to use TelegramInterface.")
    pipeline.run()