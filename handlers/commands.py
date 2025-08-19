import datetime

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from dialogs.registration_dialog import RegistrationSG
from dialogs.schedule_dialog import ScheduleSG
from filters.filters import IsRegistered
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
    message: Message, dialog_manager: DialogManager, session: AsyncSession, lang: str
):
    """Handles the /start command for registered users."""
    user = dialog_manager.middleware_data["user"]
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
async def process_cancel_command(message: Message, session: AsyncSession, lang: str):
    """Handles the /cancel command."""
    user = message.middleware_data["user"]
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
