from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.text import Format
from loguru import logger

# --- Lexicon Structure ---
LEXICON: dict[str, dict[str, str]] = {
    "ru": {
        # General
        "unsupported_message": "Я не понимаю это сообщение. Пожалуйста, используйте команды.",
        "back_button": "⬅️ Назад",
        "confirm_button": "✅ Подтвердить",
        # Weekdays
        "weekday_0": "Понедельник",
        "weekday_1": "Вторник",
        "weekday_2": "Среда",
        "weekday_3": "Четверг",
        "weekday_4": "Пятница",
        "weekday_5": "Суббота",
        "weekday_6": "Воскресенье",
        # Commands
        "start_new_user": "Добро пожаловать! Давайте начнем регистрацию.",
        "start_registered_user": "С возвращением! Вы уже зарегистрированы. Чтобы записаться, выберите дату.",
        "start_already_booked": "Вы уже записаны на <b>{date} ({weekday}) в {time}</b>.\nОкно №{window}.\n\nДля отмены используйте команду /cancel.",
        "help_command": "Этот бот поможет вам записаться в очередь. Используйте /start для начала.",
        "cancel_no_booking": "У вас нет активной записи для отмены.",
        "cancel_successful": "Ваша запись успешно отменена. Вы можете записаться заново.",
        "cancel_failed_too_late": "Отмена записи возможна не позднее, чем за 3 часа до назначенного времени.",
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
        # Schedule Dialog
        "get_date_prompt": "📅 Выберите удобную дату для записи:",
        "get_time_prompt": "🕒 Выберите свободное время на <b>{selected_date_str}</b>:",
        "no_slots_available": "К сожалению, на этот день нет свободных слотов. Пожалуйста, выберите другую дату.",
        "confirm_booking_prompt": "Вы хотите записаться на <b>{date} ({weekday}) в {time}</b>?",
        "booking_successful": "✅ Вы успешно записаны!",
        "booking_failed_already_booked": "❌ У вас уже есть активная запись. Сначала отмените ее с помощью /cancel.",
        "booking_failed_too_late": "❌ Этот временной слот уже занят. Пожалуйста, выберите другой.",
    }
}

# --- Bot Commands ---
LEXICON_COMMANDS: dict[str, str] = {
    "/start": "Записаться / Моя запись",
    "/cancel": "Отменить запись",
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
