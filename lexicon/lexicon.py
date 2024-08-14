LEXICON: dict[str, str] = {
    'yes': 'Да',
    'no': 'Нет',
}

LEXICON_COMMANDS: dict[str, str] = {
    '/hate': 'Захейтить чела',
    '/list': 'Список сучек',
    '/forgive': 'Простить чела',
    '/random': 'Рандомный хейт'
}


def lexicon(key: str) -> str:
    return LEXICON[key.split('_')[0]]
