# telegramtk

**Telegram toolkit**

This package provides easy (and sync) access for the Telegram Bot API.

## Installation

```console
pip install telegramtk
```

## Setup

First of all you must [create a Telegram bot](https://core.telegram.org/bots/features#creating-a-new-bot) and grab the **bot token**.

```python
import telegramtk

telegramtk.init('<your-telegram-bot-token-here>')
```

## Send message

```python
import telegramtk

telegramtk.send_message(to, msg)
```

Notes:

- `to` is the recipient and must be a _chat id_ (integer value) or a _known name_ (string value).
- `msg` is the message (string value) and can be "Markdown" formatted.

### Error handling

If an error ocurred during the request to the Telegram API, an exception is raised. You can find this exception at:

```python
import telegramtk
from telegramtk.exceptions import TelegramError

try:
    telegramtk.send_message(to, msg)
except TelegramError as err:
    handle_error(err)
```

## Escape markdown

It's common to send Markdown content through Telegram, but sometimes we want to escape Markdown symbols in order to avoid syntax errors when parsing.

For that end, you might use the following function:

```python
from telegramtk.utils import escape_markdown

>>> escape_markdown('Just some *Markdown* _stuff_ [here](https://example.com/)')
'Just some \\*Markdown\\* \\_stuff\\_ \\[here\\]\\(https://example\\.com/\\)'
```

> 💡 Source: https://github.com/python-telegram-bot/python-telegram-bot/blob/master/telegram/helpers.py#L45
