from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Group, SwitchTo
from aiogram_dialog.widgets.text import Format
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from lexicon import LocalizedTextFormat, lexicon
from services.schedule_service import cancel_booking, get_user_booking


class BookingManagementSG(StatesGroup):
    """States for the booking management dialog."""

    view_booking = State()
    confirm_cancel = State()


# --- Getters ---
async def get_booking_data(dialog_manager: DialogManager, **kwargs):
    """Prepares data for the booking view window."""
    session: AsyncSession = dialog_manager.middleware_data["session"]
    user: User = dialog_manager.middleware_data["user"]
    lang: str = dialog_manager.middleware_data.get("lang")

    booking = await get_user_booking(session, user)
    if not booking:
        # This should ideally not be reached if the dialog is started correctly
        return {"has_booking": False}

    dt = booking.booking_datetime
    return {
        "has_booking": True,
        "date": dt.strftime("%d.%m.%Y"),
        "time": dt.strftime("%H:%M"),
        "weekday": lexicon(lang, f"weekday_{dt.weekday()}"),
        "window": booking.window_number,
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


# --- Dialog Windows ---
booking_management_dialog = Dialog(
    Window(
        LocalizedTextFormat("my_booking_title"),
        SwitchTo(
            LocalizedTextFormat("cancel_booking_button"),
            id="switch_to_cancel",
            state=BookingManagementSG.confirm_cancel,
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
