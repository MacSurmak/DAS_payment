import re
import random

from aiogram import Router, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from database.crud import *
from filters.filters import IsRegistered, NoData
from keyboards.commands_menu import yesno_markup
from lexicon.lexicon import lexicon

router: Router = Router(name='commands-router')


@router.message(CommandStart(), ~IsRegistered())
async def process_start_command(message: Message):
    """
    Handles /start command and adds user into database
    :param message: Telegram message
    """
    user_id = message.from_user.id
    insert_id(user_id)
    await message.answer(text=lexicon('/start'))


@router.message(CommandStart(), IsRegistered(), NoData())
async def process_start_command(message: Message):
    """
    Handles /start command for registered users
    :param message: Telegram message
    """
    await message.answer(text=lexicon('/start-registered'))


@router.message(CommandStart(), IsRegistered(), ~NoData())
async def process_start_command(message: Message):
    """
    Handles /start command for registered users with data
    :param message: Telegram message
    """
    await message.answer(text=lexicon('/start-data').format(name=select_data(message.chat.id)[0]))

# @router.message(Command("hate"), IsAllowed())
# async def process_help_command(message: Message):
#     """
#     Handles /help command
#     :param message: Telegram message
#     """
#     msg = re.sub(' +', ' ', message.text)
#     try:
#         name = msg.split(" ")[1].lower().capitalize()
#     except IndexError:
#         name = ""
#         await message.answer(text="Не понимаю, кого хейтить")
#     try:
#         surname = msg.split(" ")[2].lower().capitalize()
#     except IndexError:
#         surname = ""
#
#     if len(select(name, surname)) == 0:
#         if name != "":
#             insert(name, surname, 0)
#             name, surname = case(name, surname)
#             await message.answer(text=f"Дней без хейта {name} {surname}: 0")
#     else:
#         update(0, name, surname)
#         name, surname = case(name, surname)
#         await message.answer(text=f"Дней без хейта {name} {surname}: 0")
#
#
# @router.message(Command("forgive"), IsAllowed())
# async def process_help_command(message: Message):
#     """
#     Handles /help command
#     :param message: Telegram message
#     """
#     msg = re.sub(' +', ' ', message.text)
#     try:
#         name = msg.split(" ")[1].lower().capitalize()
#     except IndexError:
#         name = ""
#         await message.answer(text="Не понимаю, кого помиловать")
#     try:
#         surname = msg.split(" ")[2].lower().capitalize()
#     except IndexError:
#         surname = ""
#
#     if len(select(name, surname)) != 0:
#         if name != "":
#             delete(name, surname)
#             await message.answer(text=f"{name} {surname} помилован(а)!")
#     else:
#         await message.answer(text=f"Такого человека нет в списке")
#
#
# @router.message(Command("list"), IsAllowed())
# async def process_help_command(message: Message):
#     """
#     Handles /list command
#     :param message: Telegram message
#     """
#     msg = []
#     count = []
#     bitches = select_all()
#     if len(bitches) != 0:
#         for bitch in bitches:
#             name, surname = case(bitch[0], bitch[1])
#             msg.append(f"Дней без хейта {name} {surname}: ")
#             count.append(bitch[2])
#         df = pd.DataFrame()
#         df["msg"] = msg
#         df["count"] = count
#         df = df.sort_values("count")
#         print(df)
#         msg = ""
#         counter = 1
#         for index, row in df.iterrows():
#             msg = f"{msg}{counter}) {row['msg']}{row['count']}\n"
#             counter += 1
#         await message.answer(text=msg)
#     else:
#         await message.answer(text="Список пуст")
#
#
# @router.callback_query(lambda callback: callback.data.split('_')[0] == 'no')
# async def admin_exit(callback: CallbackQuery):
#     """
#     Handles callback with 'exit' and returns admin into
#     user menu
#     :param callback: Telegram callback
#     """
#     await callback.message.edit_text(text=f"Мы никого не захейтили",
#                                      reply_markup=None)
#
#
# @router.callback_query(lambda callback: callback.data.split('_')[0] == 'yes')
# async def admin_exit(callback: CallbackQuery):
#     """
#     Handles callback with 'exit' and returns admin into
#     user menu
#     :param callback: Telegram callback
#     """
#     name, surname = case(callback.data.split('_')[1], callback.data.split('_')[2])
#     update(0, callback.data.split('_')[1], callback.data.split('_')[2])
#     await callback.message.edit_text(text=f"Дней без хейта {name} {surname}: 0",
#                                      reply_markup=None)
#
#
# @router.message(Command("random"))
# async def random_hate(message: Message):
#     """
#     Handles /random command
#     :param message: Telegram message
#     """
#     bitches = select_all()
#     ln = len(bitches)
#     num = random.randint(0, ln-1)
#     rb = bitches[num]
#     name, surname = case(rb[0], rb[1], cs="accusative")
#     await message.answer(text=f"Кажется, вы давно не хейтили {name} {surname}. Захейтим прямо сейчас?",
#                          reply_markup=yesno_markup(rb[0], rb[1]))
#
#
# @router.message(Command("auth"))
# async def process_help_command(message: Message):
#     """
#     Handles /auth command
#     :param message: Telegram message
#     """
#     key = message.text.split(" ")[1]
#     if key == "hatelist_629807":
#         insert_id(message.chat.id)
