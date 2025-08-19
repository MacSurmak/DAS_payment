from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.text import Format
from loguru import logger

# --- Lexicon Structure ---
LEXICON: dict[str, dict[str, str]] = {
    "ru": {
        # General
        "unsupported_message": "Я не понимаю это сообщение. Пожалуйста, используйте команды.",
        "back_button": "⬅️ Назад",
        "confirm_button": "✅ Все верно",
        # Commands
        "start_new_user": "Добро пожаловать! Давайте начнем регистрацию.",
        "start_registered_user": "С возвращением! Вы уже зарегистрированы. Чтобы записаться, выберите доступное время.",
        "help_command": "Этот бот поможет вам записаться в очередь. Используйте /start для начала.",
        # Registration Dialog
        "get_name_prompt": "📝 Для начала, пожалуйста, отправьте свои Фамилию, Имя и Отчество (если есть).",
        "name_invalid": "❌ Пожалуйста, введите 2 или 3 слова (Фамилия Имя Отчество).",
        "get_faculty_prompt": "🎓 Выберите ваш факультет:",
        "get_degree_prompt": "📚 Выберите ступень обучения:",
        "get_year_prompt": "🗓️ Выберите ваш курс:",
        "bachelor": "Бакалавриат",
        "master": "Магистратура",
        "specialist": "Специалитет",
        "confirm_prompt": "Пожалуйста, проверьте ваши данные:\n\n"
        "<b>ФИО:</b> {last_name} {first_name} {patronymic}\n"
        "<b>Факультет:</b> {faculty}\n"
        "<b>Обучение:</b> {degree}, {year} курс\n\n"
        "Все верно?",
        "registration_successful": "✅ Отлично, регистрация завершена!\n\nТеперь вы можете выбрать удобное время для записи.",
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
