import datetime
from zoneinfo import ZoneInfo

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Group, SwitchTo
from aiogram_dialog.widgets.text import Format
from loguru import logger
from magic_filter import F
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from dialogs.schedule_dialog import ScheduleSG
from lexicon import LocalizedTextFormat, lexicon
from services.schedule_service import cancel_booking, get_user_booking


class BookingManagementSG(StatesGroup):
    """States for the booking management dialog."""

    view_booking = State()
    confirm_cancel = State()


# --- Getters ---
async def get_booking_data(dialog_manager: DialogManager, **kwargs):
    """
    Prepares data for the booking view window.
    Also determines if cancellation/rescheduling is allowed.
    """
    session: AsyncSession = dialog_manager.middleware_data["session"]
    user: User = dialog_manager.middleware_data["user"]
    lang: str = dialog_manager.middleware_data.get("lang")
    moscow_tz = ZoneInfo("Europe/Moscow")

    booking = await get_user_booking(session, user)
    if not booking:
        return {"has_booking": False}

    # The datetime from DB is now automatically in Moscow time thanks to AwareDateTime type
    dt_moscow = booking.booking_datetime
    now_moscow = datetime.datetime.now(moscow_tz)

    time_diff = dt_moscow - now_moscow
    # Allow modification if >3 hours in the future OR if the time has already passed
    can_modify = (time_diff > datetime.timedelta(hours=3)) or (
        time_diff <= datetime.timedelta(0)
    )

    return {
        "has_booking": True,
        "date": dt_moscow.strftime("%d.%m.%Y"),
        "time": dt_moscow.strftime("%H:%M"),
        "weekday": lexicon(lang, f"weekday_{dt_moscow.weekday()}"),
        "window": booking.window_number,
        "can_modify": can_modify,
    }


# --- Handlers ---
async def on_cancel_booking(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    """Handles the final confirmation of booking cancellation."""
    session: AsyncSession = dialog_manager.middleware_data["session"]
    user: User = dialog_manager.middleware_data["user"]
    lang: str = dialog_manager.middleware_data.get("lang")

    was_cancelled, reason = await cancel_booking(session, user)

    if was_cancelled:
        logger.info(f"User {user.telegram_id} cancelled their booking via dialog.")
        await callback.message.answer(lexicon(lang, "cancel_successful"))
        await dialog_manager.done()
    else:
        logger.warning(
            f"User {user.telegram_id} failed to cancel booking. Reason: {reason}"
        )
        await callback.answer(lexicon(lang, "cancel_failed_too_late"), show_alert=True)
        # Close the confirmation window and return to the main view
        await dialog_manager.switch_to(BookingManagementSG.view_booking)


async def on_reschedule(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    """Starts the rescheduling process by launching the booking dialog."""
    # The actual cancellation of the old slot will happen in the schedule_service
    # when a new slot is confirmed.
    await dialog_manager.start(ScheduleSG.date_select, mode=StartMode.RESET_STACK)


# --- Dialog Windows ---
booking_management_dialog = Dialog(
    Window(
        LocalizedTextFormat("my_booking_title"),
        Group(
            SwitchTo(
                LocalizedTextFormat("cancel_booking_button"),
                id="switch_to_cancel",
                state=BookingManagementSG.confirm_cancel,
                when=F["can_modify"],
            ),
            Button(
                LocalizedTextFormat("reschedule_booking_button"),
                id="reschedule",
                on_click=on_reschedule,
                when=F["can_modify"],
            ),
            width=1,
        ),
        Cancel(LocalizedTextFormat("close_button")),
        state=BookingManagementSG.view_booking,
        getter=get_booking_data,
    ),
    Window(
        LocalizedTextFormat("confirm_cancel_prompt"),
        Group(
            Button(
                LocalizedTextFormat("confirm_cancel_button"),
                id="confirm_cancel",
                on_click=on_cancel_booking,
            ),
            SwitchTo(
                LocalizedTextFormat("back_button"),
                id="back_to_view",
                state=BookingManagementSG.view_booking,
            ),
            width=2,
        ),
        state=BookingManagementSG.confirm_cancel,
    ),
)
