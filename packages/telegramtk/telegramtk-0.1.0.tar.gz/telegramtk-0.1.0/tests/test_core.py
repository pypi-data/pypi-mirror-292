import pytest
from prettyconf import config

import telegramtk
from telegramtk.exceptions import TelegramError


@pytest.fixture(autouse=True)
def set_token():
    telegramtk.init(config('BOT_TOKEN'))


@pytest.fixture
def recipient():
    return config('RECIPIENT')


@pytest.fixture
def msg():
    return 'Hello'


def test_if_send_message_fails_when_token_is_unset(recipient, msg):
    telegramtk.init('')
    with pytest.raises(TelegramError, match='Bot token is undefined! Use init()'):
        telegramtk.send_message(recipient, msg)


def test_if_send_message_fails_when_cannot_parse_entities(recipient):
    msg = '#1'
    with pytest.raises(TelegramError, match="Bad Request: can't parse entities"):
        telegramtk.send_message(recipient, msg)


def test_if_send_message_fails_when_recipient_is_not_reachable(msg):
    recipient = 'bugsbunny'
    with pytest.raises(TelegramError, match='chat not found'):
        telegramtk.send_message(recipient, msg)


def test_send_message_works(recipient, msg):
    telegramtk.send_message(recipient, msg)
