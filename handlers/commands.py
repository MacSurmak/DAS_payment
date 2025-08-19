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
from dialogs.registration_dialog import RegistrationSG
from dialogs.schedule_dialog import ScheduleSG
from filters.filters import IsAdmin, IsRegistered
from lexicon import lexicon
from services.schedule_service import cancel_booking, get_user_booking

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
    """Handles the /start command for registered users."""
    logger.info(f"Registered user {user.telegram_id} used /start.")

    booking = await get_user_booking(session, user)

    if booking:
        dt = booking.booking_datetime
        await message.answer(
            lexicon(
                lang,
                "start_already_booked",
                date=dt.strftime("%d.%m.%Y"),
                time=dt.strftime("%H:%M"),
                weekday=lexicon(lang, f"weekday_{dt.weekday()}"),
                window=booking.window_number,
            )
        )
    else:
        await message.answer(lexicon(lang, "start_registered_user"))
        await dialog_manager.start(ScheduleSG.date_select, mode=StartMode.RESET_STACK)


@commands_router.message(Command("cancel"), IsRegistered())
async def process_cancel_command(
    message: Message, session: AsyncSession, user: User, lang: str
):
    """Handles the /cancel command."""
    booking = await get_user_booking(session, user)

    if not booking:
        await message.answer(lexicon(lang, "cancel_no_booking"))
        return

    was_cancelled, reason = await cancel_booking(session, user)

    if was_cancelled:
        logger.info(f"User {user.telegram_id} cancelled their booking.")
        await message.answer(lexicon(lang, "cancel_successful"))
    else:
        logger.warning(
            f"User {user.telegram_id} failed to cancel booking. Reason: {reason}"
        )
        if reason == "too_late":
            await message.answer(lexicon(lang, "cancel_failed_too_late"))


@commands_router.message(Command("admin"), F.text.regexp(r"/admin (.+)"))
async def process_admin_command(
    message: Message, session: AsyncSession, user: User | None, lang: str
):
    """Handles the /admin command to grant admin rights."""
    password = message.text.split(" ", 1)[1]

    if not user:  # Should not happen for registered users, but as a safeguard
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
