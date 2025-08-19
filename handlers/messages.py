from aiogram import Router
from aiogram.types import Message
from lexicon import lexicon

messages_router = Router(name="messages-router")


@messages_router.message()
async def process_other_messages(message: Message, lang: str):
    """Handles any messages that are not commands or part of a dialog."""
    await message.answer(lexicon(lang, "unsupported_message"))
