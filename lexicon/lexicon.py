from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.text import Format
from loguru import logger

# --- Lexicon Structure ---
LEXICON: dict[str, dict[str, str]] = {
    "ru": {
        # General
        "unsupported_message": "Я не понимаю это сообщение. Пожалуйста, используйте команды из меню.",
        "back_button": "⬅️ Назад",
        "confirm_button": "✅ Все верно",
        "close_button": "❌ Закрыть",
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
        "start_registered_user": "С возвращением! У вас нет активных записей. Давайте создадим новую.",
        "start_already_booked": "Вы уже записаны на <b>{date} ({weekday}) в {time}</b>.\nОкно №{window}.\n\nДля отмены используйте команду /cancel.",
        "help_command": "С помощью этого бота ты можешь встать в электронную очередь на получение документов и оплату проживания в ДАС МГУ.\n\n"
        "Бот отправит тебе напоминание за сутки и за час до назначенного времени.\n\n"
        "<b>Обрати внимание:</b> отмена записи возможна не позднее, чем за 3 часа до назначенного времени!",
        "cancel_no_booking": "У вас нет активной записи для отмены.",
        "cancel_successful": "✅ Ваша запись успешно отменена. Вы можете записаться заново.",
        "cancel_failed_too_late": "❌ Отмена записи невозможна! Осталось менее 3-х часов.",
        # Admin Commands
        "admin_grant_success": "✅ Права администратора предоставлены. Используйте /apanel для входа в панель.",
        "admin_already_admin": "Вы уже являетесь администратором.",
        "admin_wrong_password": "❌ Неверный пароль.",
        "admin_not_registered": "Сначала вам нужно зарегистрироваться в боте через /start.",
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
        "booking_failed_already_booked": "❌ У вас уже есть активная запись.",
        "booking_failed_too_late": "❌ Этот временной слот уже занят. Пожалуйста, выберите другой.",
        # Booking Management Dialog
        "my_booking_title": "<b>Ваша текущая запись:</b>\n\n"
        "<b>Дата:</b> {date} ({weekday})\n"
        "<b>Время:</b> {time}\n"
        "<b>Окно:</b> №{window}",
        "cancel_booking_button": "🚫 Отменить запись",
        "confirm_cancel_prompt": "Вы уверены, что хотите отменить эту запись?",
        "confirm_cancel_button": "Да, отменить",
        # Admin Dialog
        "admin_panel_title": "Панель Администратора",
        "admin_stats_info": "Записано: {booked_users}\nВсего зарегистрировано: {total_users}",
        "admin_get_report": "📈 Сформировать отчет (.xlsx)",
        "admin_set_last_day": "🗓️ Установить дату окончания записи",
        "admin_broadcast": "📢 Сделать рассылку",
        "admin_manage_schedule": "🛠️ Управление расписанием",
        "admin_schedule_menu_prompt": "Выберите действие для управления расписанием:",
        "admin_block_day": "🚫 Сделать день/слот нерабочим",
        "admin_block_day_prompt": "Выберите дату, для которой нужно внести исключение:",
        "admin_block_type_prompt": "Что сделать с датой <b>{date_to_block}</b>?",
        "admin_block_whole_day": "Сделать весь день нерабочим",
        "admin_block_time_slot": "Убрать конкретный временной слот",
        "admin_select_slot_to_block_prompt": "Какой слот убрать на <b>{date_to_block}</b>?",
        "admin_block_day_select_window_prompt": "Для какого окна применить исключение на <b>{date_to_block}</b>?",
        "admin_window_1": "Окно 1",
        "admin_window_2": "Окно 2",
        "admin_window_3": "Окно 3",
        "admin_all_windows": "Все окна",
        "admin_day_blocked_success": "✅ День {date} успешно сделан нерабочим.",
        "admin_time_slot_blocked_success": "✅ Слот с {start} до {end} на {date} успешно убран из расписания.",
        "report_generation_started": "Начинаю формирование отчета. Это может занять некоторое время...",
        "report_generation_failed": "❌ Не удалось сформировать отчет.",
        "admin_select_date_prompt": "Выберите последний день, доступный для записи:",
        "last_day_set_success": "✅ Последний день для записи установлен на {date}.",
        "admin_broadcast_prompt": "Введите текст для рассылки всем зарегистрированным пользователям:",
        "admin_broadcast_confirm_prompt": "Вы уверены, что хотите отправить следующее сообщение?\n\n<pre>{broadcast_text}</pre>",
        "broadcast_started": "Начинаю рассылку...",
        "broadcast_finished": "✅ Рассылка завершена.\nОтправлено: {sent}\nНе удалось: {failed}",
        # Notifications
        "notification_day_before": "Привет! Напоминаем, что вы записаны на получение документов в ДАС <b>завтра в {time}</b>.\nОкно №{window}.",
        "notification_hour_before": "Привет! Напоминаем, что вы записаны на получение документов в ДАС уже <b>через час, в {time}</b>.\nОкно №{window}.",
        # Throttling
        "throttling_warning": "Пожалуйста, не так часто! Подождите несколько секунд.",
    }
}

# --- Bot Commands ---
LEXICON_COMMANDS: dict[str, str] = {
    "/start": "Записаться / Моя запись",
    "/help": "Справка",
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
