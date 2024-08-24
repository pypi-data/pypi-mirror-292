import re

from .exceptions import TelegramError


def check_token(token: str) -> bool:
    if not token:
        raise TelegramError('Bot token is undefined! Use init()')
    return True


def escape_markdown(text: str) -> str:
    ESCAPE_CHARS = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(ESCAPE_CHARS)}])', r'\\\1', text)
