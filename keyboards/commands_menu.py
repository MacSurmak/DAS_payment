from aiogram import Bot
from aiogram.types import BotCommand
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon.lexicon import lexicon, LEXICON

from lexicon.lexicon import LEXICON_COMMANDS


async def set_commands_menu(bot: Bot):
    main_menu_commands = [BotCommand(
        command=command,
        description=description
    ) for command,
        description in LEXICON_COMMANDS.items()]
    await bot.set_my_commands(main_menu_commands)


def yesno_markup() -> InlineKeyboardMarkup:
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=lexicon(key), callback_data=key) for key in ['_yes', '_no']
    ]
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(*buttons, width=2)
    return kb_builder.as_markup(resize_keyboard=True)


def degree_markup() -> InlineKeyboardMarkup:
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=lexicon(key), callback_data=f'degree_{key}') for key in ['bachelor', 'master', 'specialist']
    ]
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(*buttons, width=2).row(InlineKeyboardButton(text=lexicon('back'), callback_data='back_degree'))
    return kb_builder.as_markup(resize_keyboard=True)


def year_markup(length) -> InlineKeyboardMarkup:
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=f'{i + 1} курс', callback_data=f'{i + 1}_year') for i in range(length)
    ]
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(*buttons, width=2).row(InlineKeyboardButton(text=lexicon('back'), callback_data='back_year'))
    return kb_builder.as_markup(resize_keyboard=True)


def faculty_markup() -> InlineKeyboardMarkup:
    buttons_long: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=lexicon(key), callback_data=f'faculty_{key}') for key in ['bio', 'geo', 'jou',
                                                                                            'ist', 'pol', 'soi',
                                                                                            'psy', 'phd', 'eco']
    ]
    buttons_short: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=lexicon(key), callback_data=f'faculty_{key}') for key in ['kpu', 'ssn', 'isa',
                                                                                            'fbb', 'ffm', 'fhi']
    ]
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(*buttons_long, width=2).row(*buttons_short, width=3)
    return kb_builder.as_markup(resize_keyboard=True)
