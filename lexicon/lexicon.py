LEXICON: dict[str, str] = {
    # Commands messages
    '/start': 'Привет! Здесь ты можешь встать в электронную очередь на оплату проживания. '
              'Для начала давай познакомимся. Отправь мне свои ФИО, например, "Иванов Иван Иванович".',
    '/start-registered': 'Снова привет! Чтобы продолжить, отправь мне свои ФИО, например, "Иванов Иван Иванович".',
    '/start-data': 'Привет, {name}!',
    '/help': 'Помощь',

    # User messages
    'reply-other': 'Я тебя не понимаю :(',

    # User markups
    '_keygen': 'Сгенерировать ключ',
}


LEXICON_COMMANDS: dict[str, str] = {
    '/start': 'Старт',
    '/help': 'Справка по работе бота'
}


def lexicon(key: str, ) -> str:
    return LEXICON[key]
