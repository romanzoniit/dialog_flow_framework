import logging
import os

from dff.connectors.messenger.telegram.interface import FlaskTelegramInterface
from dff.connectors.messenger.telegram.connector import DFFTeleBot

from flask import Flask

from dff.core.pipeline import Pipeline
from dff.utils.testing.toy_script import TOY_SCRIPT
from dff.utils.testing.common import is_interactive_mode, run_interactive_mode, check_env_var

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = Flask(__name__)

bot = DFFTeleBot(os.getenv("BOT_TOKEN", "SOMETOKEN"))

interface = FlaskTelegramInterface(bot=bot, app=app)

pipeline = Pipeline.from_script(
    script=TOY_SCRIPT,
    start_label=("greeting_flow", "start_node"),
    fallback_label=("greeting_flow", "fallback_node"),
    context_storage=dict(),
    messenger_interface=interface,
)

if __name__ == "__main__":
    check_env_var("BOT_TOKEN")
    if is_interactive_mode():
        run_interactive_mode(pipeline)
    else:
        pipeline.run()