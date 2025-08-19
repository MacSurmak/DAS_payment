from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Back, Button, Group, Select, SwitchTo
from aiogram_dialog.widgets.text import Format
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Faculty, User
from lexicon import LocalizedTextFormat, lexicon
from .schedule_dialog import ScheduleSG


class RegistrationSG(StatesGroup):
    """States for the registration dialog."""

    get_name = State()
    get_faculty = State()
    get_degree = State()
    get_year = State()
    confirm = State()


# --- Getters ---
async def get_faculties_data(
    dialog_manager: DialogManager, **kwargs
) -> dict[str, list]:
    """Retrieves a list of faculties from the database."""
    session: AsyncSession = dialog_manager.middleware_data["session"]
    result = await session.scalars(select(Faculty).order_by(Faculty.name))
    faculties = result.all()
    # Format for the Select widget: list of tuples (display_text, id)
    return {"faculties": [(f.name, f.faculty_id) for f in faculties]}


async def get_year_data(dialog_manager: DialogManager, **kwargs) -> dict[str, list]:
    """Generates a list of years based on the selected degree."""
    degree = dialog_manager.dialog_data.get("degree")
    year_map = {
        "bachelor": 4,
        "master": 2,
        "specialist": 6,
    }
    num_years = year_map.get(degree, 4)
    return {"years": [(str(i), i) for i in range(1, num_years + 1)]}


async def get_confirmation_data(dialog_manager: DialogManager, **kwargs) -> dict:
    """Prepares data for the confirmation window."""
    session: AsyncSession = dialog_manager.middleware_data["session"]
    lang = dialog_manager.middleware_data.get("lang")
    faculty_id = dialog_manager.dialog_data.get("faculty_id")

    faculty = await session.get(Faculty, faculty_id)

    data = {
        "last_name": dialog_manager.dialog_data.get("last_name"),
        "first_name": dialog_manager.dialog_data.get("first_name"),
        "patronymic": dialog_manager.dialog_data.get("patronymic", "-"),
        "faculty": faculty.name if faculty else "N/A",
        "degree": lexicon(lang, dialog_manager.dialog_data.get("degree")),
        "year": dialog_manager.dialog_data.get("year"),
    }
    return data


# --- Handlers ---
async def on_name_input(
    message: Message, widget: TextInput, dialog_manager: DialogManager, text: str
):
    """Handles user's full name input."""
    lang = dialog_manager.middleware_data.get("lang")
    parts = text.strip().split()
    if len(parts) not in [2, 3]:
        await message.answer(lexicon(lang, "name_invalid"))
        return

    dialog_manager.dialog_data["last_name"] = parts[0]
    dialog_manager.dialog_data["first_name"] = parts[1]
    if len(parts) == 3:
        dialog_manager.dialog_data["patronymic"] = parts[2]
    else:
        dialog_manager.dialog_data["patronymic"] = None
    await dialog_manager.next()


async def on_faculty_selected(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Handles faculty selection."""
    dialog_manager.dialog_data["faculty_id"] = int(item_id)
    await dialog_manager.next()


async def on_degree_selected(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    """Handles degree selection."""
    dialog_manager.dialog_data["degree"] = button.widget_id
    await dialog_manager.next()


async def on_year_selected(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Handles year of study selection."""
    dialog_manager.dialog_data["year"] = int(item_id)
    await dialog_manager.next()


async def on_confirm(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    """Saves user data to the database upon confirmation."""
    session: AsyncSession = dialog_manager.middleware_data["session"]
    lang = dialog_manager.middleware_data.get("lang")
    dialog_data = dialog_manager.dialog_data

    new_user = User(
        telegram_id=callback.from_user.id,
        first_name=dialog_data.get("first_name"),
        last_name=dialog_data.get("last_name"),
        patronymic=dialog_data.get("patronymic"),
        faculty_id=dialog_data.get("faculty_id"),
        degree=dialog_data.get("degree"),
        year=dialog_data.get("year"),
        lang=lang,
    )
    session.add(new_user)
    await session.commit()
    logger.info(f"New user registered: {new_user}")

    await callback.message.edit_text(lexicon(lang, "registration_successful"))
    # Seamlessly start the scheduling dialog for the new user
    await dialog_manager.start(ScheduleSG.date_select, mode=StartMode.RESET_STACK)


# --- Dialog Windows ---
registration_dialog = Dialog(
    Window(
        LocalizedTextFormat("get_name_prompt"),
        TextInput(id="name_input", on_success=on_name_input),
        state=RegistrationSG.get_name,
    ),
    Window(
        LocalizedTextFormat("get_faculty_prompt"),
        Group(
            Select(
                Format("{item[0]}"),
                id="faculty_select",
                item_id_getter=lambda item: item[1],
                items="faculties",
                on_click=on_faculty_selected,
            ),
            width=2,
        ),
        Back(LocalizedTextFormat("back_button")),
        state=RegistrationSG.get_faculty,
        getter=get_faculties_data,
    ),
    Window(
        LocalizedTextFormat("get_degree_prompt"),
        Group(
            Button(
                LocalizedTextFormat("bachelor"),
                id="bachelor",
                on_click=on_degree_selected,
            ),
            Button(
                LocalizedTextFormat("master"), id="master", on_click=on_degree_selected
            ),
            Button(
                LocalizedTextFormat("specialist"),
                id="specialist",
                on_click=on_degree_selected,
            ),
            width=2,
        ),
        Back(LocalizedTextFormat("back_button")),
        state=RegistrationSG.get_degree,
    ),
    Window(
        LocalizedTextFormat("get_year_prompt"),
        Group(
            Select(
                Format("{item[0]} курс"),
                id="year_select",
                item_id_getter=lambda item: item[1],
                items="years",
                on_click=on_year_selected,
            ),
            width=2,
        ),
        Back(LocalizedTextFormat("back_button")),
        state=RegistrationSG.get_year,
        getter=get_year_data,
    ),
    Window(
        LocalizedTextFormat("confirm_prompt"),
        Group(
            Button(
                LocalizedTextFormat("confirm_button"), id="confirm", on_click=on_confirm
            ),
            SwitchTo(
                LocalizedTextFormat("back_button"),
                id="back_to_start",
                state=RegistrationSG.get_name,
            ),
            width=2,
        ),
        state=RegistrationSG.confirm,
        getter=get_confirmation_data,
    ),
)
