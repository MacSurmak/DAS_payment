import datetime

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, Calendar, Group, Select, SwitchTo
from aiogram_dialog.widgets.text import Const, Format
from loguru import logger
from magic_filter import F
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import LastDay, User
from lexicon import LocalizedTextFormat, lexicon
from services.schedule_service import create_booking, get_available_slots


class ScheduleSG(StatesGroup):
    """States for the scheduling dialog."""

    date_select = State()
    time_select = State()
    confirm = State()


# --- Getters ---
async def get_dates_data(dialog_manager: DialogManager, **kwargs) -> dict:
    """Prepares data for the date selection window."""
    session: AsyncSession = dialog_manager.middleware_data["session"]
    last_day_record = await session.get(LastDay, 1)
    min_date = datetime.date.today()
    max_date = last_day_record.last_date if last_day_record else min_date
    return {"min_date": min_date, "max_date": max_date}


async def get_times_data(dialog_manager: DialogManager, **kwargs) -> dict:
    """Prepares data for the time selection window."""
    session: AsyncSession = dialog_manager.middleware_data["session"]
    user: User = dialog_manager.middleware_data["user"]
    selected_date_iso = dialog_manager.dialog_data.get("selected_date")
    if not selected_date_iso:
        return {"slots": [], "has_slots": False}

    selected_date = datetime.date.fromisoformat(selected_date_iso)
    slots = await get_available_slots(session, user, selected_date)

    return {
        "selected_date_str": selected_date.strftime("%d.%m.%Y"),
        "slots": [(slot.strftime("%H:%M"), slot.isoformat()) for slot in slots],
        "has_slots": bool(slots),
    }


async def get_confirmation_data(dialog_manager: DialogManager, **kwargs) -> dict:
    """Prepares data for the confirmation window."""
    dt_iso = dialog_manager.dialog_data.get("selected_datetime")
    dt = datetime.datetime.fromisoformat(dt_iso)
    return {
        "date": dt.strftime("%d.%m.%Y"),
        "time": dt.strftime("%H:%M"),
        "weekday": lexicon("ru", f"weekday_{dt.weekday()}"),
    }


# --- Handlers ---
async def on_date_selected(
    callback: CallbackQuery,
    widget,
    dialog_manager: DialogManager,
    selected_date: datetime.date,
):
    """Handles date selection from the calendar."""
    dialog_manager.dialog_data["selected_date"] = selected_date.isoformat()
    await dialog_manager.switch_to(ScheduleSG.time_select)


async def on_time_selected(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Handles time slot selection."""
    dialog_manager.dialog_data["selected_datetime"] = item_id
    await dialog_manager.switch_to(ScheduleSG.confirm)


async def on_booking_confirm(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    """Handles the final booking confirmation."""
    session: AsyncSession = dialog_manager.middleware_data["session"]
    user: User = dialog_manager.middleware_data["user"]
    lang = dialog_manager.middleware_data.get("lang")
    dt_iso = dialog_manager.dialog_data.get("selected_datetime")
    booking_dt = datetime.datetime.fromisoformat(dt_iso)

    booking, error = await create_booking(session, user, booking_dt)

    if booking:
        logger.info(
            f"User {user.telegram_id} successfully booked slot for {booking_dt}"
        )
        await callback.message.edit_text(lexicon(lang, "booking_successful"))
        await dialog_manager.done()
    else:
        logger.warning(
            f"Booking failed for user {user.telegram_id} for slot {booking_dt}. Reason: {error}"
        )
        await callback.answer(lexicon(lang, f"booking_failed_{error}"), show_alert=True)
        # Go back to time selection, as the slots might have changed
        await dialog_manager.switch_to(ScheduleSG.time_select)


# --- Dialog Windows ---
schedule_dialog = Dialog(
    Window(
        LocalizedTextFormat("get_date_prompt"),
        Calendar(
            id="calendar",
            on_click=on_date_selected,
            min_date_getter=lambda data: data["min_date"],
            max_date_getter=lambda data: data["max_date"],
        ),
        state=ScheduleSG.date_select,
        getter=get_dates_data,
    ),
    Window(
        LocalizedTextFormat("get_time_prompt"),
        Const(lexicon("ru", "no_slots_available"), when=~F["has_slots"]),
        Group(
            Select(
                Format("{item[0]}"),
                id="time_select",
                item_id_getter=lambda item: item[1],
                items="slots",
                on_click=on_time_selected,
            ),
            width=4,
            when=F["has_slots"],
        ),
        SwitchTo(
            LocalizedTextFormat("back_button"),
            id="back_to_date",
            state=ScheduleSG.date_select,
        ),
        state=ScheduleSG.time_select,
        getter=get_times_data,
    ),
    Window(
        LocalizedTextFormat("confirm_booking_prompt"),
        Group(
            Button(
                LocalizedTextFormat("confirm_button"),
                id="confirm",
                on_click=on_booking_confirm,
            ),
            SwitchTo(
                LocalizedTextFormat("back_button"),
                id="back_to_time",
                state=ScheduleSG.time_select,
            ),
            width=2,
        ),
        state=ScheduleSG.confirm,
        getter=get_confirmation_data,
    ),
)
