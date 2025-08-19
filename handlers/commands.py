import datetime

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from config_data import config
from database.models import User
from dialogs.admin_dialog import AdminSG
from dialogs.booking_management_dialog import BookingManagementSG
from dialogs.registration_dialog import RegistrationSG
from dialogs.schedule_dialog import ScheduleSG
from filters.filters import IsAdmin, IsRegistered
from lexicon import lexicon
from services.schedule_service import get_user_booking

commands_router = Router(name="commands-router")


@commands_router.message(CommandStart(), ~IsRegistered())
async def start_new_user(message: Message, dialog_manager: DialogManager, lang: str):
    """Handles the /start command for new users."""
    logger.info(f"New user {message.from_user.id} started registration.")
    await message.answer(lexicon(lang, "start_new_user"))
    await dialog_manager.start(RegistrationSG.get_name, mode=StartMode.RESET_STACK)


@commands_router.message(CommandStart(), IsRegistered())
async def start_registered_user(
    message: Message,
    dialog_manager: DialogManager,
    session: AsyncSession,
    user: User,
    lang: str,
):
    """
    Handles the /start command for registered users.
    Starts booking management or a new booking process.
    """
    logger.info(f"Registered user {user.telegram_id} used /start.")

    booking = await get_user_booking(session, user)

    if booking:
        await dialog_manager.start(
            BookingManagementSG.view_booking, mode=StartMode.RESET_STACK
        )
    else:
        await message.answer(lexicon(lang, "start_registered_user"))
        await dialog_manager.start(ScheduleSG.date_select, mode=StartMode.RESET_STACK)


@commands_router.message(Command("help"))
async def process_help_command(message: Message, lang: str):
    """Handles the /help command."""
    await message.answer(lexicon(lang, "help_command"))


@commands_router.message(Command("admin"), F.text.regexp(r"/admin (.+)"))
async def process_admin_command(
    message: Message, session: AsyncSession, user: User | None, lang: str
):
    """Handles the /admin command to grant admin rights."""
    password = message.text.split(" ", 1)[1]

    if not user:
        await message.answer(lexicon(lang, "admin_not_registered"))
        return

    if password == config.bot.admin_password:
        if not user.is_admin:
            user.is_admin = True
            await session.commit()
            logger.info(f"User {user.telegram_id} has been granted admin rights.")
            await message.answer(lexicon(lang, "admin_grant_success"))
        else:
            await message.answer(lexicon(lang, "admin_already_admin"))
    else:
        logger.warning(f"Failed admin login attempt by user {user.telegram_id}.")
        await message.answer(lexicon(lang, "admin_wrong_password"))


@commands_router.message(Command("apanel"), IsAdmin())
async def process_apanel_command(
    message: Message, dialog_manager: DialogManager, lang: str
):
    """Handles the /apanel command to open the admin panel."""
    logger.info(f"Admin {message.from_user.id} accessed the admin panel.")
    await dialog_manager.start(AdminSG.main_menu, mode=StartMode.RESET_STACK)
