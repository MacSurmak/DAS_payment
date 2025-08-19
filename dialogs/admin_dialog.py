import datetime
import os
import re

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Calendar,
    Group,
    Multiselect,
    Radio,
    Row,
    ScrollingGroup,
    Select,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Multi
from loguru import logger
from sqlalchemy import distinct, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import LastDay, ScheduleException, TimetableSlot
from lexicon import LocalizedTextFormat, lexicon
from services.admin_actions import (
    broadcast_message,
    create_non_working_day,
    create_schedule_exception,
    delete_schedule_exception,
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
    add_non_working_day = State()

    # States for adding a new modification rule
    add_exception_description = State()
    add_exception_start_date = State()
    add_exception_end_date = State()
    add_exception_days = State()
    add_exception_target_slot = State()
    add_exception_new_times = State()
    add_exception_years = State()
    add_exception_year_behavior = State()
    add_exception_start_window = State()
    add_exception_confirm = State()

    # States for viewing and deleting rules
    view_exceptions = State()
    confirm_delete_exception = State()


# --- Getters ---
async def get_stats_data(dialog_manager: DialogManager, **kwargs) -> dict:
    """Prepares data for the main menu, including statistics."""
    session: AsyncSession = dialog_manager.middleware_data["session"]
    stats = await get_statistics(session)
    return stats


async def get_broadcast_data(dialog_manager: DialogManager, **kwargs) -> dict:
    """Gets the broadcast message text for confirmation."""
    return {"broadcast_text": dialog_manager.dialog_data.get("broadcast_text", "")}


async def get_default_slots_data(dialog_manager: DialogManager, **kwargs) -> dict:
    """
    Gets default timetable slots for selection and caches them in dialog_data
    for later lookup in handlers.
    """
    session: AsyncSession = dialog_manager.middleware_data["session"]
    stmt = (
        select(TimetableSlot.start_time, TimetableSlot.end_time)
        .distinct()
        .order_by(TimetableSlot.start_time)
    )
    result = await session.execute(stmt)
    slots = result.all()
    formatted_slots = [
        (
            f"{s.start_time.strftime('%H:%M')} - {s.end_time.strftime('%H:%M')}",
            f"{s.start_time.isoformat()}",
        )
        for s in slots
    ]
    # Cache the data for the handler to use
    dialog_manager.dialog_data["_slots_cache"] = formatted_slots
    return {"slots": formatted_slots}


async def get_add_confirmation_data(dialog_manager: DialogManager, **kwargs) -> dict:
    """Prepares data for the final confirmation of a new exception rule."""
    lang = dialog_manager.middleware_data.get("lang")
    data = dialog_manager.dialog_data
    days_map = {
        0: lexicon(lang, "weekday_0_short"),
        1: lexicon(lang, "weekday_1_short"),
        2: lexicon(lang, "weekday_2_short"),
        3: lexicon(lang, "weekday_3_short"),
        4: lexicon(lang, "weekday_4_short"),
    }
    selected_days = [days_map[int(d)] for d in data.get("days_of_week", [])]
    behavior_key = (
        "exclusive" if data.get("block_others_if_years_mismatch") else "modifier"
    )

    return {
        "description": data.get("description"),
        "start_date": data.get("start_date"),
        "end_date": data.get("end_date"),
        "days": ", ".join(selected_days) or lexicon(lang, "all_days_of_week"),
        "target_slot": data.get("target_slot_str", lexicon(lang, "not_applicable")),
        "new_times": data.get("new_times_str", lexicon(lang, "not_applicable")),
        "years": ", ".join(map(str, data.get("years", [])))
        or lexicon(lang, "all_years"),
        "year_behavior": lexicon(lang, f"year_behavior_{behavior_key}"),
        "start_window": data.get("start_window") or lexicon(lang, "not_changed"),
    }


async def get_exceptions_data(dialog_manager: DialogManager, **kwargs) -> dict:
    """Fetches all schedule exception rules for viewing."""
    session: AsyncSession = dialog_manager.middleware_data["session"]
    stmt = select(ScheduleException).order_by(ScheduleException.start_date.desc())
    exceptions = (await session.scalars(stmt)).all()
    return {"exceptions": exceptions}


async def get_delete_confirmation_data(dialog_manager: DialogManager, **kwargs) -> dict:
    """Prepares data for the delete confirmation window."""
    exc_id = dialog_manager.dialog_data.get("exception_to_delete_id")
    session: AsyncSession = dialog_manager.middleware_data["session"]
    exception = await session.get(ScheduleException, exc_id)
    return {"exception": exception}


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


async def on_non_working_date_selected(
    callback: CallbackQuery, widget, dialog_manager: DialogManager, date: datetime.date
):
    """Creates a non-working day exception."""
    session: AsyncSession = dialog_manager.middleware_data["session"]
    lang = dialog_manager.middleware_data.get("lang")

    await create_non_working_day(
        session=session,
        date=date,
        description=f"Non-working day added by admin {callback.from_user.id}",
    )
    logger.info(f"Admin {callback.from_user.id} marked {date} as non-working.")
    await callback.answer(
        lexicon(lang, "admin_day_blocked_success", date=date.strftime("%d.%m.%Y")),
        show_alert=True,
    )


# --- Handlers for Adding a New Exception Rule ---


async def on_description_input(
    message: Message, widget: TextInput, dialog_manager: DialogManager, text: str
):
    dialog_manager.dialog_data["description"] = text
    await dialog_manager.next()


async def on_start_date_selected(
    callback: CallbackQuery, widget, dialog_manager: DialogManager, date: datetime.date
):
    dialog_manager.dialog_data["start_date"] = date.isoformat()
    await dialog_manager.next()


async def on_end_date_selected(
    callback: CallbackQuery, widget, dialog_manager: DialogManager, date: datetime.date
):
    lang = dialog_manager.middleware_data.get("lang")
    start_date = datetime.date.fromisoformat(dialog_manager.dialog_data["start_date"])
    if date < start_date:
        await callback.answer(lexicon(lang, "admin_end_date_error"), show_alert=True)
        return
    dialog_manager.dialog_data["end_date"] = date.isoformat()
    await dialog_manager.next()


async def on_days_selection_continue(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    """Handles the 'Continue' button click after day selection."""
    days_multiselect: Multiselect = dialog_manager.find("days_select")
    dialog_manager.dialog_data["days_of_week"] = days_multiselect.get_checked()
    await dialog_manager.next()


async def on_target_slot_selected(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Handles selection of a time slot to be modified."""
    dialog_manager.dialog_data["target_slot"] = item_id
    # Store human-readable string for confirmation getter by looking it up
    # in the cached list from the getter.
    slots_cache = dialog_manager.dialog_data.get("_slots_cache", [])
    for text, slot_id in slots_cache:
        if slot_id == item_id:
            dialog_manager.dialog_data["target_slot_str"] = text
            break
    await dialog_manager.next()


async def on_new_times_input(
    message: Message, widget: TextInput, dialog_manager: DialogManager, text: str
):
    lang = dialog_manager.middleware_data.get("lang")
    match = re.fullmatch(r"(\d{2}:\d{2})-(\d{2}:\d{2})", text.strip())
    if not match:
        await message.answer(lexicon(lang, "admin_new_time_format_error"))
        return
    start_str, end_str = match.groups()
    try:
        start_time = datetime.time.fromisoformat(start_str)
        end_time = datetime.time.fromisoformat(end_str)
        if start_time >= end_time:
            raise ValueError("Start time must be before end time")
    except ValueError:
        await message.answer(lexicon(lang, "admin_new_time_invalid_error"))
        return

    dialog_manager.dialog_data["new_start_time"] = start_str
    dialog_manager.dialog_data["new_end_time"] = end_str
    dialog_manager.dialog_data["new_times_str"] = f"{start_str}-{end_str}"
    await dialog_manager.next()


async def on_years_input(
    message: Message, widget: TextInput, dialog_manager: DialogManager, text: str
):
    lang = dialog_manager.middleware_data.get("lang")
    if not text.strip():  # Empty input means all years
        dialog_manager.dialog_data["years"] = []
        dialog_manager.dialog_data["block_others_if_years_mismatch"] = False
        # If no years are specified, the blocking logic is irrelevant, so we skip the next step.
        await dialog_manager.switch_to(AdminSG.add_exception_start_window)
        return

    try:
        years = [int(y.strip()) for y in text.split(",")]
        if not all(1 <= y <= 6 for y in years):
            raise ValueError
        dialog_manager.dialog_data["years"] = years
        await dialog_manager.next()
    except (ValueError, TypeError):
        await message.answer(lexicon(lang, "admin_years_format_error"))


async def on_year_behavior_selected(
    callback: CallbackQuery, widget: Radio, dialog_manager: DialogManager, item_id: str
):
    """Handles selection of how the year filter should behave."""
    dialog_manager.dialog_data["block_others_if_years_mismatch"] = (
        item_id == "exclusive"
    )
    await dialog_manager.next()


async def on_start_window_selected(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    dialog_manager.dialog_data["start_window"] = int(item_id) if item_id else None
    await dialog_manager.next()


async def on_skip_clicked(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    # Clear potentially conflicting data when skipping a step
    if dialog_manager.current_context().state == AdminSG.add_exception_target_slot:
        dialog_manager.dialog_data["target_slot"] = None
        dialog_manager.dialog_data["new_start_time"] = None
        dialog_manager.dialog_data["new_end_time"] = None
        await dialog_manager.switch_to(AdminSG.add_exception_years)
    elif dialog_manager.current_context().state == AdminSG.add_exception_start_window:
        dialog_manager.dialog_data["start_window"] = None
        await dialog_manager.switch_to(AdminSG.add_exception_confirm)


async def on_confirm_exception_add(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    session: AsyncSession = dialog_manager.middleware_data["session"]
    lang = dialog_manager.middleware_data.get("lang")
    await create_schedule_exception(session, dialog_manager.dialog_data)
    logger.info(
        f"Admin {callback.from_user.id} created a new schedule exception: {dialog_manager.dialog_data.get('description')}"
    )
    await callback.answer(
        lexicon(lang, "admin_exception_created_success"), show_alert=True
    )
    await dialog_manager.switch_to(AdminSG.schedule_management)


# --- Handlers for Deleting an Exception Rule ---
async def on_delete_exception_select(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Stores the ID of the exception to delete and asks for confirmation."""
    dialog_manager.dialog_data["exception_to_delete_id"] = int(item_id)
    await dialog_manager.switch_to(AdminSG.confirm_delete_exception)


async def on_confirm_exception_delete(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    """Deletes the exception from the database."""
    session: AsyncSession = dialog_manager.middleware_data["session"]
    lang = dialog_manager.middleware_data.get("lang")
    exc_id = dialog_manager.dialog_data["exception_to_delete_id"]
    await delete_schedule_exception(session, exc_id)
    logger.info(f"Admin {callback.from_user.id} deleted schedule exception ID {exc_id}")
    await callback.answer(
        lexicon(lang, "admin_exception_deleted_success"), show_alert=True
    )
    # Go back to the list, which will now be updated
    await dialog_manager.switch_to(AdminSG.view_exceptions)


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
        Group(
            SwitchTo(
                LocalizedTextFormat("admin_add_non_working_day"),
                id="add_non_working_day",
                state=AdminSG.add_non_working_day,
            ),
            SwitchTo(
                LocalizedTextFormat("admin_add_modification_rule"),
                id="add_modification_rule",
                state=AdminSG.add_exception_description,
            ),
            SwitchTo(
                LocalizedTextFormat("admin_view_rules"),
                id="view_rules",
                state=AdminSG.view_exceptions,
            ),
            width=1,
        ),
        SwitchTo(
            LocalizedTextFormat("back_button"),
            id="back_to_main_from_schedule",
            state=AdminSG.main_menu,
        ),
        state=AdminSG.schedule_management,
    ),
    # Add Non-Working Day
    Window(
        LocalizedTextFormat("admin_block_day_prompt"),
        Calendar(id="calendar_non_working_day", on_click=on_non_working_date_selected),
        SwitchTo(
            LocalizedTextFormat("back_button"),
            id="back_to_schedule_menu",
            state=AdminSG.schedule_management,
        ),
        state=AdminSG.add_non_working_day,
    ),
    # --- Add Modification Rule Flow ---
    Window(
        LocalizedTextFormat("admin_exception_desc_prompt"),
        TextInput(id="exception_desc_input", on_success=on_description_input),
        SwitchTo(
            LocalizedTextFormat("back_button"),
            id="back_to_sched_menu",
            state=AdminSG.schedule_management,
        ),
        state=AdminSG.add_exception_description,
    ),
    Window(
        LocalizedTextFormat("admin_exception_start_date_prompt"),
        Calendar(id="calendar_start_date", on_click=on_start_date_selected),
        Back(LocalizedTextFormat("back_button")),
        state=AdminSG.add_exception_start_date,
    ),
    Window(
        LocalizedTextFormat("admin_exception_end_date_prompt"),
        Calendar(id="calendar_end_date", on_click=on_end_date_selected),
        Back(LocalizedTextFormat("back_button")),
        state=AdminSG.add_exception_end_date,
    ),
    Window(
        LocalizedTextFormat("admin_exception_days_prompt"),
        Group(
            Multiselect(
                Format("✓ {item[0]}"),
                Format("{item[0]}"),
                id="days_select",
                item_id_getter=lambda item: item[1],
                items=[
                    (lexicon("ru", "weekday_0_short"), 0),
                    (lexicon("ru", "weekday_1_short"), 1),
                    (lexicon("ru", "weekday_2_short"), 2),
                    (lexicon("ru", "weekday_3_short"), 3),
                    (lexicon("ru", "weekday_4_short"), 4),
                ],
            ),
            width=5,
        ),
        Button(
            LocalizedTextFormat("continue_button"),
            id="continue_days",
            on_click=on_days_selection_continue,
        ),
        Back(LocalizedTextFormat("back_button")),
        state=AdminSG.add_exception_days,
    ),
    Window(
        LocalizedTextFormat("admin_exception_target_slot_prompt"),
        Group(
            Select(
                Format("{item[0]}"),
                id="slot_select",
                item_id_getter=lambda item: item[1],
                items="slots",
                on_click=on_target_slot_selected,
            ),
            width=1,
        ),
        Button(
            LocalizedTextFormat("skip_button"),
            id="skip_target_slot",
            on_click=on_skip_clicked,
        ),
        Back(LocalizedTextFormat("back_button")),
        state=AdminSG.add_exception_target_slot,
        getter=get_default_slots_data,
    ),
    Window(
        LocalizedTextFormat("admin_exception_new_times_prompt"),
        TextInput(id="new_times_input", on_success=on_new_times_input),
        Back(LocalizedTextFormat("back_button")),
        state=AdminSG.add_exception_new_times,
    ),
    Window(
        LocalizedTextFormat("admin_exception_years_prompt"),
        TextInput(id="years_input", on_success=on_years_input),
        Back(LocalizedTextFormat("back_button")),
        state=AdminSG.add_exception_years,
    ),
    Window(
        LocalizedTextFormat("admin_exception_year_behavior_prompt"),
        Radio(
            Format("🔘 {item[0]}"),
            Format("⚪️ {item[0]}"),
            id="year_behavior_radio",
            item_id_getter=lambda item: item[1],
            items=[
                (lexicon("ru", "year_behavior_modifier_text"), "modifier"),
                (lexicon("ru", "year_behavior_exclusive_text"), "exclusive"),
            ],
            on_click=on_year_behavior_selected,
        ),
        Back(LocalizedTextFormat("back_button")),
        state=AdminSG.add_exception_year_behavior,
    ),
    Window(
        LocalizedTextFormat("admin_exception_start_window_prompt"),
        Group(
            Select(
                Format(lexicon("ru", "window_prefix_num")),
                id="window_select",
                item_id_getter=lambda item: item,
                items=[1, 2, 3],
                on_click=on_start_window_selected,
            ),
            width=3,
        ),
        Button(
            LocalizedTextFormat("skip_button"),
            id="skip_start_window",
            on_click=on_skip_clicked,
        ),
        Back(LocalizedTextFormat("back_button")),
        state=AdminSG.add_exception_start_window,
    ),
    Window(
        LocalizedTextFormat("admin_exception_confirm_prompt"),
        Group(
            Button(
                LocalizedTextFormat("confirm_button"),
                id="confirm_exception",
                on_click=on_confirm_exception_add,
            ),
            Back(LocalizedTextFormat("back_button")),
            width=2,
        ),
        state=AdminSG.add_exception_confirm,
        getter=get_add_confirmation_data,
    ),
    # --- View and Delete Exceptions Flow ---
    Window(
        LocalizedTextFormat("admin_view_exceptions_title"),
        ScrollingGroup(
            Select(
                Format("📜 {item.description} 🗑️"),
                id="select_exc_to_delete",
                item_id_getter=lambda item: item.exception_id,
                items="exceptions",
                on_click=on_delete_exception_select,
            ),
            id="scroll_exceptions",
            width=1,
            height=5,
        ),
        SwitchTo(
            LocalizedTextFormat("back_button"),
            id="back_to_schedule_menu_from_view",
            state=AdminSG.schedule_management,
        ),
        state=AdminSG.view_exceptions,
        getter=get_exceptions_data,
    ),
    Window(
        LocalizedTextFormat("admin_exception_confirm_delete_prompt"),
        Row(
            SwitchTo(
                LocalizedTextFormat("back_button"),
                id="cancel_delete",
                state=AdminSG.view_exceptions,
            ),
            Button(
                LocalizedTextFormat("confirm_delete_button"),
                id="confirm_delete",
                on_click=on_confirm_exception_delete,
            ),
        ),
        state=AdminSG.confirm_delete_exception,
        getter=get_delete_confirmation_data,
    ),
)
