class TelegramError(Exception):
    def __init__(self, message='A Telegram error ocurred'):
        super().__init__(message)
