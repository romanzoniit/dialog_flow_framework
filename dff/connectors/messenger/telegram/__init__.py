# -*- coding: utf-8 -*-
# flake8: noqa: F401

try:
    import telebot
except ImportError:
    raise ImportError("telebot is not installed. Run `pip install dff[telegram]`")