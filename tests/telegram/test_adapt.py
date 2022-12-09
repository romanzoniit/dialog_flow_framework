import json
import pytest
import time
import datetime

from io import IOBase
from pathlib import Path
from pydantic import ValidationError
from telebot import types
from telethon.tl.types import (
    InputMessagesFilterPhotos,
    InputMessagesFilterGeo,
    InputMessagesFilterMusic,
    InputMessagesFilterVideo,
)

from dff.connectors.messenger.telegram.local_types import (
    TelegramResponse,
    TelegramAttachments,
    TelegramAttachment,
    TelegramUI,
)
from dff.connectors.messenger.generics import Attachments, Response, Keyboard, Button, Image, Location, Audio, Video
from dff.connectors.messenger.telegram.utils import open_io, close_io


def reiterate_response(bot, user, message):
    counter = 0
    while True:
        counter += 1
        try:
            bot.send_response(user, message)
            break
        except Exception:
            time.sleep(2)
        finally:
            if counter >= 4:
                break


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["ui", "markup_type", "button_type"],
    [
        (
            Keyboard(
                buttons=[
                    Button(text="button 1", payload=json.dumps({"text": "1", "other_prop": "4"})),
                    Button(text="button 2", payload=json.dumps({"text": "2", "other_prop": "3"})),
                    Button(text="button 3", payload=json.dumps({"text": "3", "other_prop": "2"})),
                    Button(text="button 4", payload=json.dumps({"text": "4", "other_prop": "1"})),
                ]
            ),
            types.InlineKeyboardMarkup,
            types.InlineKeyboardButton,
        ),
        (
            Keyboard(
                is_inline=False,
                buttons=[
                    Button(text="button 1", payload=json.dumps({"text": "1", "other_prop": "4"})),
                    Button(text="button 2", payload=json.dumps({"text": "2", "other_prop": "3"})),
                    Button(text="button 3", payload=json.dumps({"text": "3", "other_prop": "2"})),
                    Button(text="button 4", payload=json.dumps({"text": "4", "other_prop": "1"})),
                ],
            ),
            types.ReplyKeyboardMarkup,
            types.KeyboardButton,
        ),
    ],
)
async def test_adapt_buttons(ui, button_type, markup_type, tg_client, basic_bot, user_id, bot_id):
    generic_response = Response(text="test", ui=ui)
    telegram_response = TelegramResponse.parse_obj(generic_response)
    assert telegram_response.text == generic_response.text
    assert telegram_response.ui and isinstance(telegram_response.ui.keyboard, markup_type)
    print(telegram_response.ui.keyboard.keyboard)
    assert len(telegram_response.ui.keyboard.keyboard) == 2
    reiterate_response(basic_bot, user_id, telegram_response)
    # basic_bot.send_response(user_id, telegram_response)
    minute_ago = datetime.datetime.now() - datetime.timedelta(minutes=1)
    messages = await tg_client.get_messages(bot_id, None, offset_date=minute_ago)
    assert messages


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["ui"],
    [
        (TelegramUI(keyboard=types.ReplyKeyboardRemove()),),
    ],
)
async def test_keyboard_remove(ui, basic_bot, user_id, tg_client, bot_id):
    generic_response = Response(text="test", ui=ui)
    telegram_response = TelegramResponse.parse_obj(generic_response)
    assert telegram_response.text == generic_response.text
    assert telegram_response.ui
    reiterate_response(basic_bot, user_id, telegram_response)
    # basic_bot.send_response(user_id, telegram_response)
    minute_ago = datetime.datetime.now() - datetime.timedelta(minutes=1)
    messages = await tg_client.get_messages(bot_id, None, offset_date=minute_ago)
    assert messages


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["generic_response", "prop", "filter_type"],
    [
        (
            Response(text="test", image=Image(source="https://folklore.linghub.ru/api/gallery/300/23.JPG")),
            "image",
            InputMessagesFilterPhotos,
        ),
        (
            Response(text="test", audio=Audio(source="https://north-folklore.ru/static/sound/IVD_No44.MP3")),
            "audio",
            InputMessagesFilterMusic,
        ),
        (
            Response(
                text="test",
                video=Video(source="https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4"),
            ),
            "video",
            InputMessagesFilterVideo,
        ),
    ],
)
async def test_telegram_attachment(generic_response, prop, filter_type, basic_bot, user_id, tg_client, bot_id):
    telegram_response = TelegramResponse.parse_obj(generic_response)
    telegram_prop = vars(telegram_response).get(prop)
    generic_prop = vars(generic_response).get(prop)
    assert telegram_prop and isinstance(telegram_prop, TelegramAttachment)
    assert telegram_prop.source == generic_prop.source
    reiterate_response(basic_bot, user_id, telegram_response)
    # basic_bot.send_response(user_id, telegram_response)
    minute_ago = datetime.datetime.now() - datetime.timedelta(minutes=1)
    messages = await tg_client.get_messages(bot_id, None, filter=filter_type, offset_date=minute_ago)
    assert messages
    assert len(messages) > 0


@pytest.mark.asyncio
async def test_adapt_attachments(basic_bot, user_id, tg_client, bot_id):
    generic_response = Response(
        text="test",
        attachments=Attachments(
            files=[
                Image(source="https://folklore.linghub.ru/api/gallery/300/23.JPG", title="image 1"),
                Image(source="https://folklore.linghub.ru/api/gallery/300/22.JPG", title="image 2"),
            ]
        ),
    )
    telegram_response = TelegramResponse.parse_obj(generic_response)
    assert telegram_response.text == generic_response.text
    assert telegram_response.attachments and isinstance(telegram_response.attachments, TelegramAttachments)
    assert len(telegram_response.attachments.files) == 2
    assert isinstance(telegram_response.attachments.files[0], types.InputMediaPhoto)
    assert telegram_response.attachments.files[0].media == generic_response.attachments.files[0].source
    assert telegram_response.attachments.files[0].caption == generic_response.attachments.files[0].title
    # basic_bot.send_response(user_id, telegram_response)
    reiterate_response(basic_bot, user_id, telegram_response)
    minute_ago = datetime.datetime.now() - datetime.timedelta(minutes=1)
    messages = await tg_client.get_messages(bot_id, None, filter=InputMessagesFilterPhotos, offset_date=minute_ago)
    assert messages
    assert len(messages) > 0


@pytest.mark.asyncio
async def test_location(basic_bot, user_id, tg_client, bot_id):
    generic_response = Response(text="location", location=Location(longitude=39.0, latitude=43.0))
    telegram_response = TelegramResponse.parse_obj(generic_response)
    assert telegram_response.text == generic_response.text
    assert telegram_response.location
    reiterate_response(basic_bot, user_id, telegram_response)
    # basic_bot.send_response(user_id, telegram_response)
    minute_ago = datetime.datetime.now() - datetime.timedelta(minutes=1)
    messages = await tg_client.get_messages(bot_id, None, filter=InputMessagesFilterGeo, offset_date=minute_ago)
    assert messages
    assert len(messages) > 0


def test_adapt_error(basic_bot, user_id):
    with pytest.raises(TypeError) as e:
        basic_bot.send_response(user_id, 1.2)
    assert e


def test_missing_error():
    with pytest.raises(ValidationError) as e:
        _ = TelegramAttachment(source="http://google.com", id="123")
    assert e

    with pytest.raises(ValidationError) as e:
        _ = TelegramAttachment(source="/etc/missing_file")
    assert e


def test_attachment_error():
    with pytest.raises(ValidationError) as e:
        _ = TelegramAttachments(files=["a", "b"])
    assert e


def test_empty_keyboard():
    with pytest.raises(ValidationError) as e:
        _ = TelegramUI(buttons=[])
    assert e


def test_io(document):
    tele_doc = types.InputMediaDocument(media=Path(document))
    opened_doc = open_io(tele_doc)
    print(type(opened_doc.media))
    assert isinstance(opened_doc.media, IOBase)
    close_io(opened_doc)
    assert opened_doc.media.closed
