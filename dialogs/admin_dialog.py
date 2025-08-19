import datetime
from typing import List, Tuple

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Calendar, Group, Select, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, Multi
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import LastDay, TimetableSlot
from lexicon import LocalizedTextFormat, lexicon
from services.admin_service import (
    block_day_in_schedule,
    broadcast_message,
    get_statistics,
)
from services.report_service import generate_excel_report


class AdminSG(StatesGroup):
    """States for the admin panel dialog."""

    main_menu = State()
    set_last_day = State()
    broadcast_text = State()
    broadcast_confirm = State()
    schedule_management = State()
    block_day_select_date = State()
    block_day_select_type = State()
    block_day_select_slot = State()
    block_day_select_window = State()


# --- Getters ---
async def get_stats_data(dialog_manager: DialogManager, **kwargs) -> dict:
    """Prepares data for the main menu, including statistics."""
    session: AsyncSession = dialog_manager.middleware_data["session"]
    stats = await get_statistics(session)
    return stats


async def get_broadcast_data(dialog_manager: DialogManager, **kwargs) -> dict:
    """Gets the broadcast message text for confirmation."""
    return {"broadcast_text": dialog_manager.dialog_data.get("broadcast_text", "")}


async def get_block_day_data(dialog_manager: DialogManager, **kwargs) -> dict:
    """Prepares data for window selection and date display."""
    lang = dialog_manager.middleware_data.get("lang")
    date_iso = dialog_manager.dialog_data.get("date_to_block")
    date_str = datetime.date.fromisoformat(date_iso).strftime("%d.%m.%Y")
    windows = [
        (lexicon(lang, "admin_window_1"), 1),
        (lexicon(lang, "admin_window_2"), 2),
        (lexicon(lang, "admin_window_3"), 3),
        (lexicon(lang, "admin_all_windows"), 0),
    ]
    return {"date_to_block": date_str, "windows": windows}


async def get_slots_for_day_data(dialog_manager: DialogManager, **kwargs) -> dict:
    """Gets default timetable slots for the selected day of the week."""
    session: AsyncSession = dialog_manager.middleware_data["session"]
    date_iso = dialog_manager.dialog_data.get("date_to_block")
    target_date = datetime.date.fromisoformat(date_iso)
    day_of_week = target_date.weekday()

    stmt = (
        select(TimetableSlot.start_time, TimetableSlot.end_time)
        .where(TimetableSlot.day_of_week == day_of_week)
        .distinct()
        .order_by(TimetableSlot.start_time)
    )
    result = await session.execute(stmt)
    slots = result.all()

    # Format for Select widget: (display_text, item_id)
    formatted_slots = [
        (
            f"{s.start_time.strftime('%H:%M')} - {s.end_time.strftime('%H:%M')}",
            f"{s.start_time.isoformat()}|{s.end_time.isoformat()}",
        )
        for s in slots
    ]
    return {
        "date_to_block": target_date.strftime("%d.%m.%Y"),
        "slots": formatted_slots,
    }


# --- Handlers ---
async def on_get_report_click(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    """Handles the report generation button click."""
    session: AsyncSession = dialog_manager.middleware_data["session"]
    lang = dialog_manager.middleware_data.get("lang")
    await callback.answer(lexicon(lang, "report_generation_started"), show_alert=False)
    file_path = None
    try:
        file_path = await generate_excel_report(session, lang)
        await callback.message.answer_document(FSInputFile(file_path))
        logger.info(f"Admin {callback.from_user.id} generated a report.")
    except Exception as e:
        logger.exception("Failed to generate report.")
        await callback.message.answer(lexicon(lang, "report_generation_failed"))
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)


async def on_date_selected(
    callback: CallbackQuery, widget, dialog_manager: DialogManager, date: datetime.date
):
    """Handles selection of a new last booking date."""
    session: AsyncSession = dialog_manager.middleware_data["session"]
    lang = dialog_manager.middleware_data.get("lang")

    last_day_record = await session.get(LastDay, 1)
    if not last_day_record:
        last_day_record = LastDay(id=1, last_date=date)
        session.add(last_day_record)
    else:
        last_day_record.last_date = date

    await session.commit()
    logger.info(f"Admin {callback.from_user.id} set last day to {date.isoformat()}")
    await callback.answer(
        lexicon(lang, "last_day_set_success", date=date.strftime("%d.%m.%Y"))
    )
    await dialog_manager.switch_to(AdminSG.main_menu)


async def on_broadcast_text_input(
    message: Message, message_input: MessageInput, dialog_manager: DialogManager
):
    """Saves broadcast message text and switches to confirmation."""
    dialog_manager.dialog_data["broadcast_text"] = message.text
    await dialog_manager.switch_to(AdminSG.broadcast_confirm)


async def on_broadcast_confirm(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    """Confirms and sends the broadcast message."""
    lang = dialog_manager.middleware_data.get("lang")
    if button.widget_id == "confirm_broadcast":
        await callback.answer(lexicon(lang, "broadcast_started"), show_alert=False)
        session: AsyncSession = dialog_manager.middleware_data["session"]
        text = dialog_manager.dialog_data.get("broadcast_text")
        bot = dialog_manager.middleware_data["bot"]

        sent_count, failed_count = await broadcast_message(bot, session, text)
        logger.info(f"Broadcast finished. Sent: {sent_count}, Failed: {failed_count}.")
        await callback.message.answer(
            lexicon(
                lang,
                "broadcast_finished",
                sent=sent_count,
                failed=failed_count,
            )
        )
        await dialog_manager.done()
    else:
        await dialog_manager.switch_to(AdminSG.main_menu)


# --- Schedule Management Handlers ---


async def on_date_to_block_selected(
    callback: CallbackQuery, widget, dialog_manager: DialogManager, date: datetime.date
):
    """Saves the date to block and switches to block type selection."""
    dialog_manager.dialog_data["date_to_block"] = date.isoformat()
    await dialog_manager.switch_to(AdminSG.block_day_select_type)


async def on_block_type_selected(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    """Handles selection of block type (whole day or time slot)."""
    if button.widget_id == "block_whole_day":
        dialog_manager.dialog_data["slot_to_block"] = (
            None  # Clear any previous selection
        )
        await dialog_manager.switch_to(AdminSG.block_day_select_window)
    elif button.widget_id == "block_time_slot":
        await dialog_manager.switch_to(AdminSG.block_day_select_slot)


async def on_slot_to_block_selected(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Saves the selected time slot and proceeds to window selection."""
    dialog_manager.dialog_data["slot_to_block"] = item_id
    await dialog_manager.switch_to(AdminSG.block_day_select_window)


async def on_window_to_block_selected(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Blocks the selected date/slot for the chosen window(s)."""
    session: AsyncSession = dialog_manager.middleware_data["session"]
    lang = dialog_manager.middleware_data.get("lang")

    date_iso = dialog_manager.dialog_data.get("date_to_block")
    target_date = datetime.date.fromisoformat(date_iso)
    window_to_block = int(item_id)
    slot_str = dialog_manager.dialog_data.get("slot_to_block")

    start_time, end_time = None, None
    if slot_str:
        start_iso, end_iso = slot_str.split("|")
        start_time = datetime.time.fromisoformat(start_iso)
        end_time = datetime.time.fromisoformat(end_iso)
        lexicon_key = "admin_time_slot_blocked_success"
    else:
        lexicon_key = "admin_day_blocked_success"

    windows = (
        [1, 2, 3] if window_to_block == 0 else [window_to_block]
    )  # 0 means all windows
    await block_day_in_schedule(session, target_date, windows, start_time, end_time)

    await callback.answer(
        lexicon(
            lang,
            lexicon_key,
            date=target_date.strftime("%d.%m.%Y"),
            start=start_time.strftime("%H:%M") if start_time else "",
            end=end_time.strftime("%H:%M") if end_time else "",
        ),
        show_alert=True,
    )
    logger.info(
        f"Admin {callback.from_user.id} blocked {target_date} "
        f"(from {start_time} to {end_time}) for windows {windows}"
    )
    await dialog_manager.switch_to(AdminSG.schedule_management)


# --- Dialog Windows ---
admin_dialog = Dialog(
    # Main Menu
    Window(
        Multi(
            LocalizedTextFormat("admin_panel_title"),
            Format(lexicon("ru", "admin_stats_info")),
        ),
        Group(
            Button(
                LocalizedTextFormat("admin_get_report"),
                id="get_report",
                on_click=on_get_report_click,
            ),
            SwitchTo(
                LocalizedTextFormat("admin_set_last_day"),
                id="set_last_day",
                state=AdminSG.set_last_day,
            ),
            SwitchTo(
                LocalizedTextFormat("admin_manage_schedule"),
                id="manage_schedule",
                state=AdminSG.schedule_management,
            ),
            SwitchTo(
                LocalizedTextFormat("admin_broadcast"),
                id="broadcast",
                state=AdminSG.broadcast_text,
            ),
            width=1,
        ),
        state=AdminSG.main_menu,
        getter=get_stats_data,
    ),
    # Set Last Day
    Window(
        LocalizedTextFormat("admin_select_date_prompt"),
        Calendar(id="calendar_last_day", on_click=on_date_selected),
        SwitchTo(
            LocalizedTextFormat("back_button"),
            id="back_to_main",
            state=AdminSG.main_menu,
        ),
        state=AdminSG.set_last_day,
    ),
    # Broadcast
    Window(
        LocalizedTextFormat("admin_broadcast_prompt"),
        MessageInput(on_broadcast_text_input),
        SwitchTo(
            LocalizedTextFormat("back_button"),
            id="back_from_broadcast",
            state=AdminSG.main_menu,
        ),
        state=AdminSG.broadcast_text,
    ),
    Window(
        LocalizedTextFormat("admin_broadcast_confirm_prompt"),
        Group(
            Button(
                LocalizedTextFormat("confirm_button"),
                id="confirm_broadcast",
                on_click=on_broadcast_confirm,
            ),
            Button(
                LocalizedTextFormat("back_button"),
                id="cancel_broadcast",
                on_click=on_broadcast_confirm,
            ),
            width=2,
        ),
        state=AdminSG.broadcast_confirm,
        getter=get_broadcast_data,
    ),
    # Schedule Management Menu
    Window(
        LocalizedTextFormat("admin_schedule_menu_prompt"),
        SwitchTo(
            LocalizedTextFormat("admin_block_day"),
            id="block_day",
            state=AdminSG.block_day_select_date,
        ),
        SwitchTo(
            LocalizedTextFormat("back_button"),
            id="back_to_main_from_schedule",
            state=AdminSG.main_menu,
        ),
        state=AdminSG.schedule_management,
    ),
    # Block Day: Select Date
    Window(
        LocalizedTextFormat("admin_block_day_prompt"),
        Calendar(id="calendar_block_day", on_click=on_date_to_block_selected),
        SwitchTo(
            LocalizedTextFormat("back_button"),
            id="back_to_schedule_menu",
            state=AdminSG.schedule_management,
        ),
        state=AdminSG.block_day_select_date,
    ),
    # Block Day: Select Type (Whole day or Slot)
    Window(
        LocalizedTextFormat("admin_block_type_prompt"),
        Group(
            Button(
                LocalizedTextFormat("admin_block_whole_day"),
                id="block_whole_day",
                on_click=on_block_type_selected,
            ),
            Button(
                LocalizedTextFormat("admin_block_time_slot"),
                id="block_time_slot",
                on_click=on_block_type_selected,
            ),
            width=1,
        ),
        SwitchTo(
            LocalizedTextFormat("back_button"),
            id="back_to_date_select",
            state=AdminSG.block_day_select_date,
        ),
        state=AdminSG.block_day_select_type,
        getter=get_block_day_data,
    ),
    # Block Day: Select Slot
    Window(
        LocalizedTextFormat("admin_select_slot_to_block_prompt"),
        Group(
            Select(
                Format("{item[0]}"),
                id="slot_select",
                item_id_getter=lambda item: item[1],
                items="slots",
                on_click=on_slot_to_block_selected,
            ),
            width=1,
        ),
        SwitchTo(
            LocalizedTextFormat("back_button"),
            id="back_to_type_select",
            state=AdminSG.block_day_select_type,
        ),
        state=AdminSG.block_day_select_slot,
        getter=get_slots_for_day_data,
    ),
    # Block Day: Select Window
    Window(
        LocalizedTextFormat("admin_block_day_select_window_prompt"),
        Select(
            Format("{item[0]}"),
            id="window_select",
            item_id_getter=lambda item: item[1],
            items="windows",
            on_click=on_window_to_block_selected,
        ),
        SwitchTo(
            LocalizedTextFormat("back_button"),
            id="back_to_block_day_date",
            state=AdminSG.block_day_select_date,
        ),
        state=AdminSG.block_day_select_window,
        getter=get_block_day_data,
    ),
)
