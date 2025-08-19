from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from loguru import logger

from dialogs.registration_dialog import RegistrationSG
from filters.filters import IsRegistered
from lexicon import lexicon

commands_router = Router(name="commands-router")


@commands_router.message(CommandStart(), ~IsRegistered())
async def start_new_user(message: Message, dialog_manager: DialogManager, lang: str):
    """Handles the /start command for new users."""
    logger.info(f"New user {message.from_user.id} started registration.")
    await message.answer(lexicon(lang, "start_new_user"))
    await dialog_manager.start(RegistrationSG.get_name, mode=StartMode.RESET_STACK)


@commands_router.message(CommandStart(), IsRegistered())
async def start_registered_user(message: Message, lang: str):
    """Handles the /start command for registered users."""
    logger.info(f"Registered user {message.from_user.id} used /start.")
    await message.answer(lexicon(lang, "start_registered_user"))
    # TODO: Start main menu or schedule dialog here
