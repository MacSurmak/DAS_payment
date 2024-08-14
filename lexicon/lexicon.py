LEXICON: dict[str, str] = {
    # Commands messages
    '/start': 'Привет! Здесь ты можешь встать в электронную очередь на оплату проживания. '
              'Для начала давай познакомимся. Отправь мне свои ФИО, например, "Иванов Иван Иванович".',
    '/start-registered': 'Снова привет! Чтобы продолжить, отправь мне свои ФИО, например, "Иванов Иван Иванович".',
    '/start-data': 'Привет, {name}!',
    '/help': 'Помощь',

    # User messages
    'reply-other': 'Я тебя не понимаю :(',
    'name-confirmation': 'Фамилия: {surname}\nИмя: {name}\nОтчество: {patronymic}\n\nВсё верно?',
    'repeat': 'Пожалуйста, отправь мне свои ФИО, например, "Иванов Иван Иванович".',
    'accepted': 'Будем знакомы, {name}!',

    # User markups
    '_no': 'Нет',
    '_yes': 'Да'
}


LEXICON_COMMANDS: dict[str, str] = {
    '/start': 'Старт',
    '/help': 'Справка по работе бота'
}


def lexicon(key: str, ) -> str:
    return LEXICON[key]
