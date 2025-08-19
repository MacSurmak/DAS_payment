from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.text import Format
from loguru import logger

# --- Lexicon Structure ---
LEXICON: dict[str, dict[str, str]] = {
    "ru": {
        # General
        "unsupported_message": "Я не понимаю это сообщение. Пожалуйста, используйте команды.",
        # Commands
        "start_new_user": "Добро пожаловать! Давайте начнем регистрацию.",
        "start_registered_user": "С возвращением! Вы уже зарегистрированы.",
        "help_command": "Этот бот поможет вам записаться в очередь. Используйте /start для начала.",
    }
}

# --- Bot Commands ---
LEXICON_COMMANDS: dict[str, str] = {
    "/start": "Запустить / Перезапустить бота",
    "/help": "Помощь",
    "/cancel": "Отменить текущее действие",
}

# --- Supported Languages ---
LANGUAGES = [
    {"code": "ru", "name": "Русский 🇷🇺"},
]
DEFAULT_LANG = "ru"


# --- Localization Functions ---
def lexicon(lang: str | None, key: str, **kwargs) -> str:
    """
    Gets a localized string from the lexicon.
    """
    if lang not in LEXICON:
        lang = DEFAULT_LANG

    text_template = LEXICON.get(lang, {}).get(key, f"err:NO_KEY_{key}")
    return text_template.format(**kwargs) if kwargs else text_template


class LocalizedTextFormat(Format):
    """
    Custom aiogram-dialog widget to format text using the lexicon.
    """

    def __init__(self, key: str):
        super().__init__(text=f"{{{key}}}")
        self.key = key

    async def _render_text(self, data: dict, manager: DialogManager) -> str:
        lang = manager.middleware_data.get("lang", DEFAULT_LANG)
        return lexicon(lang, self.key, **data)
