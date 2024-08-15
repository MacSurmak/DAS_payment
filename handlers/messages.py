import re
import random

from aiogram import Router, Bot
from aiogram import F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from database.crud import *
from filters.filters import IsRegistered, NoData
from keyboards.commands_menu import yesno_markup, degree_markup, year_markup, faculty_markup
from lexicon.lexicon import lexicon

router: Router = Router(name='messages-router')


@router.message(~IsRegistered())
async def process_registration(message: Message):
    """
    Handles text and adds user into database
    :param message: Telegram message
    """
    user_id = message.from_user.id
    insert_id(user_id)
    await message.answer(text=lexicon('/start'))


@router.message(IsRegistered(), NoData(), F.text.replace(' ', '').isalpha())
async def process_adding_data(message: Message):
    """
    Handles text from registered user with no data and adds it if present
    :param message: Telegram message
    """
    text = message.text.split()
    if len(text) in [2, 3]:
        surname = text[0]
        name = text[1]
        if len(text) == 3:
            patronymic = text[2]
        else:
            patronymic = '-'
    await message.answer(text=lexicon('name-confirmation').format(name=name, surname=surname, patronymic=patronymic),
                         reply_markup=yesno_markup())


@router.callback_query(lambda callback: callback.data == '_no')
async def no(callback: CallbackQuery):
    """
    Handles callback with 'no' and returns to waiting for name
    :param callback: Telegram callback
    """
    await callback.message.edit_text(text=lexicon('repeat'),
                                     reply_markup=None)


@router.callback_query(lambda callback: callback.data == '_yes')
async def yes(callback: CallbackQuery):
    """
    Handles callback with 'yes' and adds it to database
    :param callback: Telegram callback
    """
    text = callback.message.text.split('\n')
    surname = text[0].split(' ')[1]
    name = text[1].split(' ')[1]
    patronymic = text[2].split(' ')[1]
    update_name(user_id=callback.message.chat.id,
                name=name,
                surname=surname,
                patronymic=patronymic)
    await callback.message.edit_text(text=lexicon('faculty').format(name=name),
                                     reply_markup=faculty_markup())


@router.callback_query(lambda callback: callback.data == 'back_degree')
async def yes(callback: CallbackQuery):
    """
    Handles callback with 'back' and adds it to database
    :param callback: Telegram callback
    """
    await callback.message.edit_text(text=lexicon('faculty_2'),
                                     reply_markup=faculty_markup())


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'faculty')
async def faculty(callback: CallbackQuery):
    """
    Handles callback with 'faculty' and adds it to database
    :param callback: Telegram callback
    """
    update_faculty(user_id=callback.message.chat.id,
                   faculty=lexicon(key=callback.data.split('_')[1]))
    await callback.message.edit_text(text=lexicon('accepted'),
                                     reply_markup=degree_markup())


@router.callback_query(lambda callback: callback.data == 'back_year')
async def yes(callback: CallbackQuery):
    """
    Handles callback with 'back' and adds it to database
    :param callback: Telegram callback
    """
    await callback.message.edit_text(text=lexicon('accepted_2'),
                                     reply_markup=degree_markup())


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'degree')
async def bachelor(callback: CallbackQuery):
    """
    Handles callback with degree and adds it to database
    :param callback: Telegram callback
    """
    degree = lexicon(key=callback.data.split('_')[1])
    lengths = {
        'Бакалавриат': 4,
        'Магистратура': 2,
        'Специалитет': 6,
    }
    update_degree(user_id=callback.message.chat.id,
                  degree=degree)
    await callback.message.edit_text(text=lexicon('accepted'),
                                     reply_markup=year_markup(length=lengths[degree]))


@router.callback_query(lambda callback: callback.data.split('_')[1] == 'year')
async def year(callback: CallbackQuery):
    """
    Handles callback with 'year' and adds it to database
    :param callback: Telegram callback
    """
    update_year(user_id=callback.message.chat.id,
                year=callback.data.split('_')[0])
    await callback.message.edit_text(text=lexicon('ready'),
                                     reply_markup=None)


