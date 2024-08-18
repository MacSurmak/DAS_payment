from datetime import datetime

from aiogram import Router
from aiogram.types import Message, CallbackQuery

from aiogram.filters import StateFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database import window
from database.crud import *
from filters.filters import IsRegistered, NoData, NoName, IsSigned
from keyboards.commands_menu import yesno_markup, degree_markup, year_markup, faculty_markup, calendar_markup, \
    day_markup
from lexicon.lexicon import lexicon

router: Router = Router(name='messages-router')


class FSMRegistration(StatesGroup):
    name = State()
    faculty = State()
    degree = State()
    year = State()
    registered = State()


@router.message(~IsRegistered())
async def process_registration(message: Message, state: FSMContext):
    """
    :param message: Telegram message
    :param state: FSM state
    """
    user_id = message.from_user.id
    create(table='Users',
           user_id=user_id)
    await message.answer(text=lexicon('/start'))
    await state.set_state(FSMRegistration.name)


@router.message(IsRegistered(), StateFilter(FSMRegistration.name))
async def process_adding_data(message: Message, state: FSMContext):
    """
    :param message: Telegram message
    :param state: FSM state
    """
    if message.text:
        if message.text.replace(' ', '').isalpha():
            text = message.text.split()
            if len(text) in [2, 3]:
                surname = text[0]
                name = text[1]
                if len(text) == 3:
                    patronymic = text[2]
                else:
                    patronymic = '-'
                await state.update_data(name=name,
                                        surname=surname,
                                        patronymic=patronymic)
                # update(table='Users',
                #        name=name,
                #        surname=surname,
                #        patronymic=patronymic,
                #        where=f'user_id = {message.chat.id}')
                await message.answer(
                    text=lexicon('name-confirmation').format(name=name, surname=surname, patronymic=patronymic),
                    reply_markup=yesno_markup())
            elif len(text) == 1:
                await message.answer(text=lexicon('name-wrong2'),
                                     reply_markup=None)
            else:
                await message.answer(text=lexicon('name-wrong3'),
                                     reply_markup=None)
        else:
            await message.answer(text=lexicon('name-wrong'),
                                 reply_markup=None)
    else:
        await message.answer(text=lexicon('name-wrong4'),
                             reply_markup=None)


@router.callback_query(lambda callback: callback.data == '_no', StateFilter(FSMRegistration.name))
async def no(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    # update(table='Users',
    #        name=None,
    #        surname=None,
    #        patronymic=None,
    #        where=f'user_id = {callback.message.chat.id}')
    await callback.message.edit_text(text=lexicon('repeat'),
                                     reply_markup=None)


@router.callback_query(lambda callback: callback.data == '_yes', StateFilter(FSMRegistration.name))
async def yes(callback: CallbackQuery, state: FSMContext):
    """
    :param callback: Telegram callback
    :param state: FSM state
    """
    # text = callback.message.text.split('\n')
    # surname = text[0].split(' ')[1]
    # name = text[1].split(' ')[1]
    # patronymic = text[2].split(' ')[1]
    # update(table='Users',
    #        name=name,
    #        surname=surname,
    #        patronymic=patronymic,
    #        where=f'user_id = {callback.message.chat.id}')
    data = await state.get_data()
    name = data['name']
    await callback.message.edit_text(text=lexicon('faculty').format(name=name),
                                     reply_markup=faculty_markup())
    await state.set_state(FSMRegistration.faculty)


@router.callback_query(lambda callback: callback.data == 'back_degree')
async def back_degree(callback: CallbackQuery, state: FSMContext):
    """
    :param callback: Telegram callback
    :param state: FSM state
    """
    await callback.message.edit_text(text=lexicon('faculty_2'),
                                     reply_markup=faculty_markup())
    await state.set_state(FSMRegistration.faculty)


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'faculty')
async def faculty(callback: CallbackQuery, state: FSMContext):
    """
    :param callback: Telegram callback
    :param state: FSM state
    """
    faculty = lexicon(key=callback.data.split('_')[1])
    window = lexicon(faculty)
    await state.update_data(faculty=faculty,
                            window=window)
    # update(table='Users',
    #        faculty=faculty,
    #        window=window,
    #        where=f'user_id={callback.message.chat.id}')
    await callback.message.edit_text(text=lexicon('accepted'),
                                     reply_markup=degree_markup())
    await state.set_state(FSMRegistration.degree)


@router.callback_query(lambda callback: callback.data == 'back_year')
async def back_year(callback: CallbackQuery, state: FSMContext):
    """
    :param callback: Telegram callback
    :param state: FSM state
    """
    await callback.message.edit_text(text=lexicon('accepted_2'),
                                     reply_markup=degree_markup())
    await state.set_state(FSMRegistration.degree)


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'degree')
async def degree(callback: CallbackQuery, state: FSMContext):
    """
    :param callback: Telegram callback
    :param state: FSM state
    """
    degree = lexicon(key=callback.data.split('_')[1])
    lengths = {
        'Бакалавриат': 4,
        'Магистратура': 2,
        'Специалитет': 6,
    }
    # update(table='Users',
    #        degree=degree,
    #        where=f'user_id={callback.message.chat.id}')
    await state.update_data(degree=degree)
    await callback.message.edit_text(text=lexicon('accepted'),
                                     reply_markup=year_markup(length=lengths[degree]))
    await state.set_state(FSMRegistration.year)


@router.callback_query(lambda callback: callback.data.split('_')[1] == 'year')
async def year(callback: CallbackQuery, state: FSMContext):
    """
    :param callback: Telegram callback
    :param state: FSM state
    """
    # update(table='Users',
    #        year=callback.data.split('_')[0],
    #        where=f'user_id={callback.message.chat.id}')
    # data = read(table='Users',
    #             columns='name, surname, patronymic, faculty, degree, year',
    #             user_id=callback.message.chat.id,
    #             fetch=1)
    await state.update_data(year=callback.data.split('_')[0])
    data = await state.get_data()
    await callback.message.edit_text(text=lexicon('confirm-data').format(name=data['name'],
                                                                         surname=data['surname'],
                                                                         patronymic=data['patronymic'],
                                                                         faculty=data['faculty'],
                                                                         degree=data['degree'],
                                                                         year=data['year']),
                                     reply_markup=yesno_markup())


@router.callback_query(lambda callback: callback.data == '_no', StateFilter(FSMRegistration.year))
async def no(callback: CallbackQuery, state: FSMContext):
    """
    :param callback: Telegram callback
    :param state: FSM state
    """
    lengths = {
        'Бакалавриат': 4,
        'Магистратура': 2,
        'Специалитет': 6,
    }
    data = await state.get_data()
    degree = data['degree']
    # degree = read(table='Users',
    #               columns='degree',
    #               user_id=callback.message.chat.id,
    #               fetch=1)[0]
    # update(table='Users',
    #        year=None,
    #        where=f'user_id={callback.message.chat.id}')
    await callback.message.edit_text(text=lexicon('accepted'),
                                     reply_markup=year_markup(length=lengths[degree]))


@router.callback_query(lambda callback: callback.data == '_yes', StateFilter(FSMRegistration.year))
async def yes(callback: CallbackQuery, state: FSMContext):
    """
    :param callback: Telegram callback
    :param state: FSM state
    """
    data = await state.get_data()
    window =data['window']
    update(table='Users',
           ready=1,
           name=data['name'],
           surname=data['surname'],
           patronymic=data['patronymic'],
           faculty=data['faculty'],
           degree=data['degree'],
           year=data['year'],
           window=window,
           where=f'user_id={callback.message.chat.id}')
    # window = read(table='Users',
    #               columns='window',
    #               user_id=callback.message.chat.id,
    #               fetch=1)[0]
    await callback.message.edit_text(text=lexicon('ready').format(window=window),
                                     reply_markup=calendar_markup(datetime.today().month))
    await state.clear()


# @router.callback_query(lambda callback: callback.data.split('_')[1] == 'year')
# async def aug(callback: CallbackQuery):
#     """
#     :param callback: Telegram callback
#     """
#     window = read(table='Users',
#                   columns='window',
#                   user_id=callback.message.chat.id,
#                   fetch=1)[0]
#     update(table='Users',
#            year=callback.data.split('_')[0],
#            where=f'user_id={callback.message.chat.id}')
#     await callback.message.edit_text(text=lexicon('ready').format(window=window),
#                                      reply_markup=calendar_markup(datetime.today().month))


@router.callback_query(lambda callback: callback.data == 'calendar_back' or callback.data == 'back_to_calendar_8')
async def aug(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    window = read(table='Users',
                  columns='window',
                  user_id=callback.message.chat.id,
                  fetch=1)[0]
    await callback.message.edit_text(text=lexicon('ready').format(window=window),
                                     reply_markup=calendar_markup(8))


@router.callback_query(lambda callback: callback.data == 'calendar_next' or callback.data == 'back_to_calendar_9')
async def sep(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    window = read(table='Users',
                  columns='window',
                  user_id=callback.message.chat.id,
                  fetch=1)[0]
    await callback.message.edit_text(text=lexicon('ready').format(window=window),
                                     reply_markup=calendar_markup(9))


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'day' and callback.data.split('_')[1] == 'yes')
async def day(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    window = read(table='Users',
                  columns='window',
                  user_id=callback.message.chat.id,
                  fetch=1)[0]
    await callback.message.edit_text(text=lexicon('ready').format(window=window),
                                     reply_markup=day_markup(callback.data.split('_')[2], window))


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'day' and callback.data.split('_')[1] == 'no')
async def day(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    await callback.answer(text=lexicon('unavailable'), show_alert=True)


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'time')
async def day(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    if read(table='Users',
            columns='signed',
            user_id=callback.message.chat.id,
            fetch=1)[0] == 1:
        await callback.answer(text=lexicon('already'), show_alert=True)
    else:
        timestamp = callback.data.split('_')[1].split(':')
        if read(table='Timetable',
                columns='signed',
                month=int(timestamp[0]),
                day=int(timestamp[1]),
                hour=int(timestamp[2]),
                minute=int(timestamp[3]),
                fetch=1)[0] == 1:
            await callback.answer(text=lexicon('already_time'), show_alert=True)
        else:
            window = read(table='Users',
                          columns='window',
                          user_id=callback.message.chat.id,
                          fetch=1)[0]
            update(table='Users',
                   signed=1,
                   where=f'user_id={callback.message.chat.id}')
            update(table='Timetable',
                   signed=1,
                   by_user=callback.message.chat.id,
                   where=f'month={int(timestamp[0])}, '
                         f'day={int(timestamp[1])}, '
                         f'hour={int(timestamp[2])}, '
                         f'minute={int(timestamp[3])}')
            await callback.message.edit_text(text=lexicon('signed').format(date=f"{timestamp[1]} "
                                                                                f"{lexicon(timestamp[0]).split(' ')[0]}",
                                                                           time=f"{timestamp[2]}:{timestamp[3]}",
                                                                           window=window,
                                                                           weekday=read(table='Timetable',
                                                                                        columns='weekday',
                                                                                        by_user=callback.message.chat.id,
                                                                                        fetch=1)[0]),
                                             reply_markup=None)


@router.message(IsSigned())
async def other(message: Message):
    """
    :param message: Telegram message
    """
    timestamp = read(table = 'Timetable',
                     columns='month, day, hour, minute',
                     by_user = message.from_user.id,
                     fetch=1)
    await message.answer(text=lexicon('signed2').format(date=f"{timestamp[1]} "
                                                             f"{lexicon(str(timestamp[0])).split(' ')[0]}",
                                                        time=f"{timestamp[2]}:{timestamp[3]}",
                                                        window=window,
                                                        weekday=read(table='Timetable',
                                                                     columns='weekday',
                                                                     by_user=message.chat.id,
                                                                     fetch=1)[0]),
                         reply_markup=None)


@router.callback_query(lambda callback: callback.data == '_no', IsSigned())
async def no(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    await callback.message.edit_text(text=lexicon('not-cancelled'),
                                     reply_markup=None)


@router.callback_query(lambda callback: callback.data == '_yes', IsSigned())
async def yes(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    update(table='Users',
           signed=0,
           where=f'user_id = {callback.message.chat.id}')
    update(table='Timetable',
           signed=0,
           by_user=None,
           where=f'by_user = {callback.message.chat.id}')
    await callback.message.edit_text(text=lexicon('cancelled'))


@router.message()
async def other(message: Message):
    """
    :param message: Telegram message
    """
    await message.answer(text=lexicon('reply-other'))
