from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.text import Format
from loguru import logger

# --- Lexicon Structure ---
LEXICON: dict[str, dict[str, str]] = {
    "ru": {
        # --- General ---
        "unsupported_message": "Я не понимаю это сообщение. Пожалуйста, используй команды из меню.",
        "back_button": "⬅️ Назад",
        "confirm_button": "✅ Да, всё верно",
        "close_button": "❌ Закрыть",
        "continue_button": "Продолжить ➡️",
        "skip_button": "Пропустить ➡️",
        "not_applicable": "Н/Д",
        "not_provided": "-",
        "course_word": "курс",
        "window_prefix_num": "Окно №{item}",
        "not_set": "не установлено",
        # --- Weekdays ---
        "weekday_0": "Понедельник",
        "weekday_1": "Вторник",
        "weekday_2": "Среда",
        "weekday_3": "Четверг",
        "weekday_4": "Пятница",
        "weekday_5": "Суббота",
        "weekday_6": "Воскресенье",
        "weekday_0_short": "Пн",
        "weekday_1_short": "Вт",
        "weekday_2_short": "Ср",
        "weekday_3_short": "Чт",
        "weekday_4_short": "Пт",
        "all_days_of_week": "Все рабочие дни",
        # --- Commands ---
        "start_new_user": "Привет! Здесь ты можешь встать в электронную очередь на получение документов и оплату проживания в ДАС МГУ.\n\nЭтот бот разработан и поддерживается @macsurmak",
        "start_registered_user": "С возвращением! У тебя нет активных записей. Давай создадим новую.",
        "help_command": "С помощью этого бота ты можешь встать в электронную очередь на получение документов и оплату проживания в ДАС МГУ.\n\n"
        "Для этого тебе будет предложено пройти простую процедуру регистрации, после чего ты сможешь выбрать удобные день и время.\n\n"
        "Бот отправит тебе напоминание за сутки и за час до назначенного времени, чтобы ты точно не забыл(а).\n\n"
        "<b>Обрати внимание:</b> отмена или перенос записи возможны не позднее, чем за 3 часа до назначенного времени!\n\nЭтот бот разработан и поддерживается @macsurmak",
        "cancel_no_booking": "У тебя нет активной записи для отмены",
        "cancel_successful": "✅ Твоя запись успешно отменена! Чтобы записаться снова, используй команду /start.",
        "cancel_failed_too_late": "❌ Отмена записи невозможна! Осталось менее 3-х часов.",
        # --- Admin Commands (Formal Tone) ---
        "admin_grant_success": "✅ Права администратора предоставлены. Используйте /apanel для входа в панель.",
        "admin_already_admin": "Вы уже являетесь администратором.",
        "admin_wrong_password": "❌ Неверный пароль.",
        "admin_not_registered": "Сначала Вам нужно зарегистрироваться в боте через /start.",
        # --- Registration Dialog ---
        "get_name_prompt": "📝 Для начала давай познакомимся. Пожалуйста, отправь свои Фамилию, Имя и Отчество (если есть), например:\n"
        "<i>Иванов Иван Иванович</i>",
        "name_invalid": "❌ Пожалуйста, введи 2 или 3 слова (Фамилия Имя Отчество).",
        "get_faculty_prompt": "🎓 Выбери твой факультет:",
        "get_degree_prompt": "📚 Выбери ступень обучения:",
        "get_year_prompt": "🗓️ Выбери твой курс:",
        "bachelor": "Бакалавриат",
        "master": "Магистратура",
        "specialist": "Специалитет",
        "confirm_prompt": "Пожалуйста, проверь твои данные:\n\n"
        "<b>ФИО:</b> {last_name} {first_name} {patronymic}\n"
        "<b>Факультет:</b> {faculty}\n"
        "<b>Обучение:</b> {degree}, {year} курс\n\n"
        "Всё верно?",
        "registration_successful": "✅ Отлично, регистрация завершена!\n\nТеперь ты можешь выбрать удобное время для записи.",
        # --- Schedule Dialog ---
        "get_date_prompt": "📅 Выбери удобную дату для записи:",
        "get_time_prompt": "🕒 Выбери свободное время на <b>{selected_date_str}</b>:",
        "no_slots_available": "К сожалению, на этот день нет свободных слотов. Пожалуйста, выбери другую дату.",
        "confirm_booking_prompt": "Подтверди запись:\n\n<b>🗓️ Дата:</b> {date} ({weekday})\n<b>🕒 Время:</b> {time}",
        "booking_successful": "✅ Ты успешно записан(а)!\n\n"
        "<b>{date} ({weekday}) в {time}</b> приходи в отдел поселения (кабинет 141). После этого тебе нужно будет оплатить "
        "проживание в кассе (кабинет 140), а затем пойти в паспортный стол (кабинет 137, окно №{window}. Для твоего удобства я отправил тебе схему этажа. "
        "❗️Пожалуйста, приходи немного заранее (за 10-20 минут).\n\n"
        "<b>С собой тебе нужно будет взять:</b>\n"
        "1. Паспорт\n\n"
        "2. Приписное удостоверение или военный билет (при наличии)\n\n"
        "3. Две копии разворотов паспорта с личными сведениями и местом регистрации, ❗️сделанных на одном развороте одного листа А4❗️\n\n"
        "4. Две матовые цветные фотографии 3х4 (для удобства лучше их вырезать заранее)\n\n"
        "5. Наличные деньги — 2590 рублей (желательно без сдачи)\n"
        "Обрати внимание: оплата за каждый семестр вносится отдельно!\n\n"
        "6. Документы с факультета:\n"
        "\t- Ордер на поселение\n"
        "\t- Ходатайство о регистрации\n"
        "\t- Две выписки из приказа о зачислении\n"
        "\t- Две справки о статусе студента\n\n"
        "Я отправлю тебе напоминание, чтобы ты точно не забыл(а)!",
        "reschedule_successful": "✅ Твоя запись успешно перенесена!\n\n"
        "<b>Новое время: {date} ({weekday}) в {time}</b>, окно №{window}.\n\n"
        "Не забудь все необходимые документы. Я также пришлю напоминание.",
        "booking_failed_already_booked": "❌ У тебя уже есть активная запись.",
        "booking_failed_too_late": "❌ Этот временной слот уже занят. Пожалуйста, выбери другой.",
        "date_is_in_future": "❌ Запись возможна только до {date}. Пожалуйста, выбери другую дату.",
        # --- Booking Management Dialog ---
        "my_booking_title": "<b>Твоя текущая запись:</b>\n\n"
        "<b>Дата:</b> {date} ({weekday})\n"
        "<b>Время:</b> {time}\n"
        "<b>Окно:</b> №{window}\n\n"
        "Ты можешь отменить или перенести запись не позднее, чем за 3 часа до назначенного времени.",
        "cancel_booking_button": "🚫 Отменить запись",
        "reschedule_booking_button": "🔄 Перенести запись",
        "confirm_cancel_prompt": "Ты уверен(а), что хочешь отменить эту запись?",
        "confirm_cancel_button": "Да, отменить",
        # --- Admin Dialog (Formal Tone) ---
        "admin_panel_title": "Панель Администратора",
        "admin_stats_info": "Записано: {booked_users}\nВсего зарегистрировано: {total_users}",
        "admin_get_report": "📈 Сформировать отчет (.xlsx)",
        "admin_set_last_day": "🗓️ Установить дату окончания записи",
        "admin_broadcast": "📢 Сделать рассылку",
        "admin_manage_schedule": "🛠️ Управление расписанием",
        "admin_schedule_menu_prompt": "Здесь Вы можете гибко управлять расписанием, добавляя исключения из стандартных правил.",
        "admin_add_non_working_day": "🚫 Сделать день нерабочим",
        "admin_add_modification_rule": "✏️ Создать правило",
        "admin_view_rules": "📄 Посмотреть/изменить правила",
        "admin_block_day_prompt": "Выберите дату, которую нужно сделать нерабочей. Можно выбрать несколько дат подряд.",
        "admin_day_blocked_success": "✅ День {date} успешно сделан нерабочим.",
        "report_generation_started": "Начинаю формирование отчета. Это может занять некоторое время...",
        "report_generation_failed": "❌ Не удалось сформировать отчет.",
        "report_no_data": "Нет данных для формирования отчета.",
        "admin_select_date_prompt": "Выберите последний день, доступный для записи:",
        "admin_current_date_is": "Текущее значение: {date_str}",
        "last_day_set_success": "✅ Последний день для записи установлен на {date}.",
        "admin_broadcast_prompt": "Введите текст для рассылки всем зарегистрированным пользователям:",
        "admin_broadcast_confirm_prompt": "Вы уверены, что хотите отправить следующее сообщение?\n\n<pre>{broadcast_text}</pre>",
        "broadcast_started": "Начинаю рассылку...",
        "broadcast_finished": "✅ Рассылка завершена.\nОтправлено: {sent}\nНе удалось: {failed}",
        "admin_exception_created_success": "✅ Новое правило расписания успешно создано!",
        "admin_exception_updated_success": "✅ Правило успешно обновлено!",
        "admin_exception_deleted_success": "✅ Правило успешно удалено.",
        "admin_end_date_error": "❌ Дата окончания не может быть раньше даты начала.",
        "admin_new_time_format_error": "❌ Неверный формат. Введите время в виде <b>ЧЧ:ММ-ЧЧ:ММ</b>, например, <b>09:30-11:00</b>.",
        "admin_new_time_invalid_error": "❌ Некорректное время. Убедитесь, что время введено правильно и время начала раньше времени окончания.",
        "admin_years_format_error": "❌ Неверный формат. Введите курсы через запятую, например, <b>1, 2</b>.",
        "admin_current_start_date_is": "Текущее значение: {start_date_str}",
        "admin_current_end_date_is": "Текущее значение: {end_date_str}",
        "admin_current_desc_is": "Текущее описание: {description}",
        "admin_current_slot_is": "Текущий слот: {target_slot_str}",
        "admin_current_new_times_is": "Новое время: {new_times_str}",
        "admin_current_years_is": "Курсы: {years_str}",
        "admin_current_start_window_is": "Начальное окно: {start_window_str}",
        "indefinite_button": "🗓️ Сделать бессрочным",
        "apply_selection_button": "Применить выбор",
        "all_days_button": "Для всех рабочих дней",
        "no_change_button": "Не изменять",
        "all_years_button": "Для всех курсов",
        # --- Admin Exception Rule Creation Prompts (Formal Tone) ---
        "admin_exception_desc_prompt": "<b>Шаг 1/9: Описание правила</b>\n\nВведите краткое описание этого правила, чтобы Вы могли его позже опознать (например, 'Прием только 1 курса в сентябре').",
        "admin_exception_start_date_prompt": "<b>Шаг 2/9: Дата начала</b>\n\nВыберите дату, с которой это правило начнет действовать.",
        "admin_exception_end_date_prompt": "<b>Шаг 3/9: Дата окончания</b>\n\nВыберите дату, по которую это правило будет действовать (включительно), или сделайте его бессрочным.",
        "admin_exception_days_prompt": "<b>Шаг 4/9: Дни недели</b>\n\nВыберите дни недели, к которым применяется правило. Если ничего не выбрано, будет применяться ко всем рабочим дням в указанном диапазоне.",
        "admin_exception_target_slot_prompt": "<b>Шаг 5/9: Слот для изменения</b>\n\nКакой стандартный временной слот Вы хотите изменить? Если Вы не меняете время, а только, например, ограничиваете по курсам - нажмите 'Не изменять'.",
        "admin_exception_new_times_prompt": "<b>Шаг 6/9: Новое время</b>\n\nВведите новое время начала и конца для выбранного слота в формате <b>ЧЧ:ММ-ЧЧ:ММ</b> (например, 09:30-11:00).",
        "admin_exception_years_prompt": "<b>Шаг 7/9: Ограничение по курсам</b>\n\nВведите курсы, для которых действует это правило, через запятую (например, '1' или '1, 2').",
        "admin_exception_year_behavior_prompt": "<b>Шаг 8/9: Поведение для других курсов</b>\n\nЧто делать со студентами, чей курс <b>не</b> указан в правиле?",
        "admin_exception_start_window_prompt": "<b>Шаг 9/9: Стартовое окно</b>\n\nХотите изменить окно, с которого начинается отсчет в слотах? (По умолчанию №1). Если нет - нажмите 'Не изменять'.",
        "admin_exception_confirm_prompt": "<b>Проверьте и подтвердите правило:</b>\n\n"
        "<b>Описание:</b> {description}\n"
        "<b>Период:</b> с {start_date} по {end_date}\n"
        "<b>Дни недели:</b> {days}\n"
        "<b>Изменяемый слот:</b> {target_slot}\n"
        "<b>Новое время:</b> {new_times}\n"
        "<b>Доступно для курсов:</b> {years}\n"
        "<b>Поведение для других:</b> {year_behavior}\n"
        "<b>Начальное окно:</b> {start_window}\n\n"
        "Все верно?",
        "year_behavior_modifier": "Правило не применяется",
        "year_behavior_exclusive": "Запись для них закрыта",
        "year_behavior_not_applicable": "Н/Д (правило для всех курсов)",
        "year_behavior_modifier_text": "Не изменять (остальные видят стандартное расписание)",
        "year_behavior_exclusive_text": "Закрыть запись (запись только для указанных курсов)",
        "all_years": "Все",
        "not_changed": "Не изменено",
        "indefinitely": "бессрочно",
        "indefinitely_short": "...",
        # --- Admin View/Delete/Edit Exceptions (Formal Tone) ---
        "admin_view_exceptions_title": "📄 <b>Существующие правила и исключения:</b>",
        "admin_view_rule_title": "<b>Детали правила:</b>\n\n"
        "<b>Описание:</b> {description}\n"
        "<b>Период:</b> с {start_date} по {end_date}\n"
        "<b>Дни недели:</b> {days}\n"
        "<b>Изменяемый слот:</b> {target_slot}\n"
        "<b>Новое время:</b> {new_times}\n"
        "<b>Доступно для курсов:</b> {years}\n"
        "<b>Поведение для других:</b> {year_behavior}\n"
        "<b>Начальное окно:</b> {start_window}",
        "admin_edit_button": "✏️ Редактировать",
        "admin_delete_button": "🗑️ Удалить",
        "admin_exception_confirm_delete_prompt": "Вы уверены, что хотите удалить следующее правило?\n\n<b>📜 {exception.description}</b>",
        "confirm_delete_button": "Да, удалить",
        # --- Report Headers ---
        "report_header_window": "Окно",
        "report_header_room141": "141 каб.",
        "report_header_cashbox": "Касса",
        "report_header_room137": "137 каб.",
        "report_header_lastname": "Фамилия",
        "report_header_firstname": "Имя",
        "report_header_patronymic": "Отчество",
        "report_header_faculty": "Факультет",
        "report_header_degree": "Программа",
        "report_header_year": "Курс",
        # --- Notifications ---
        "notification_day_before": "Привет! Напоминаю, что ты записан(а) на продление проживания в ДАС <b>завтра в {time}</b>.\nОкно №{window} (каб. 137).\n\n"
        "В назначенное время приходи в отдел поселения (кабинет 141). После этого тебе нужно будет оплатить "
        "проживание в кассе (кабинет 140), а затем пойти в паспортный стол (кабинет 137, окно №{window}. Для твоего удобства я отправил тебе схему этажа. "
        "❗️Пожалуйста, приходи немного заранее (за 10-20 минут).\n\n"
        "<b>С собой тебе нужно будет взять:</b>\n"
        "1. Паспорт\n\n"
        "2. Приписное удостоверение или военный билет (при наличии)\n\n"
        "3. Две копии разворотов паспорта с личными сведениями и местом регистрации, ❗️сделанных на одном развороте одного листа А4❗️\n\n"
        "4. Две матовые цветные фотографии 3х4 (для удобства лучше их вырезать заранее)\n\n"
        "5. Наличные деньги — 2590 рублей (желательно без сдачи)\n"
        "Обрати внимание: оплата за каждый семестр вносится отдельно!\n\n"
        "6. Документы с факультета:\n"
        "\t- Ордер на поселение\n"
        "\t- Ходатайство о регистрации\n"
        "\t- Две выписки из приказа о зачислении\n"
        "\t- Две справки о статусе студента\n\n",
        "notification_hour_before": "Привет! Напоминаю, что ты записан(а) на продление проживания в ДАС уже <b>через час, в {time}</b>.\nОкно №{window} (каб. 137).\n\n"
        "Пора собираться! Не забудь документы.",
        # --- Throttling ---
        "throttling_warning": "Пожалуйста, не так часто! Подожди несколько секунд.",
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
