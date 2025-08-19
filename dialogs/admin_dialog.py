import datetime
import os

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Calendar, Group, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, Multi
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import LastDay
from lexicon import LocalizedTextFormat, lexicon
from services.admin_service import broadcast_message, get_statistics
from services.report_service import generate_excel_report


class AdminSG(StatesGroup):
    """States for the admin panel dialog."""

    main_menu = State()
    set_last_day = State()
    broadcast_text = State()
    broadcast_confirm = State()


# --- Getters ---
async def get_stats_data(dialog_manager: DialogManager, **kwargs) -> dict:
    """Prepares data for the main menu, including statistics."""
    session: AsyncSession = dialog_manager.middleware_data["session"]
    stats = await get_statistics(session)
    return stats


async def get_broadcast_data(dialog_manager: DialogManager, **kwargs) -> dict:
    """Gets the broadcast message text for confirmation."""
    return {"broadcast_text": dialog_manager.dialog_data.get("broadcast_text", "")}


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


# --- Dialog Windows ---
admin_dialog = Dialog(
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
                LocalizedTextFormat("admin_broadcast"),
                id="broadcast",
                state=AdminSG.broadcast_text,
            ),
            width=1,
        ),
        state=AdminSG.main_menu,
        getter=get_stats_data,
    ),
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
)
