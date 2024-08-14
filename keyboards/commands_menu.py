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
    buttons = ['_yes', '_no']
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    for button in buttons:
        kb_builder.row(InlineKeyboardButton(
            text=lexicon(button),
            callback_data=button))
    return kb_builder.as_markup()
