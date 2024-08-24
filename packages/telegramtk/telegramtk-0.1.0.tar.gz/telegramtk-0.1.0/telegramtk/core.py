from http import HTTPStatus

import requests

from . import settings, utils
from .exceptions import TelegramError

TOKEN = ''


def init(token: str) -> None:
    global TOKEN
    TOKEN = token


def send_message(to: str, msg: str) -> None:
    """Send message "msg" to "to" recipient"""
    utils.check_token(TOKEN)
    api_url = settings.TELEGRAM_API_BASE_URL.format(token=TOKEN, method='sendMessage')
    response = requests.get(api_url, dict(chat_id=to, text=msg, parse_mode='MarkdownV2'))
    if response.status_code != HTTPStatus.OK:
        data = response.json()
        raise TelegramError(data['description'])
