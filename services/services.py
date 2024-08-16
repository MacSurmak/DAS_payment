# from database.crud import
# from aiogram import Bot
# from keyboards.commands_menu import yesno_markup
# import random
#
#
# async def notify_day_before(bot: Bot):
#     if random.random() < 0.03:
#         bitches = select_all()
#         ln = len(bitches)
#         for i in select_all_id():
#             num = random.randint(0, ln-1)
#             rb = bitches[num]
#             name, surname = case(rb[0], rb[1], cs="accusative")
#             await bot.send_message(chat_id=i[0],
#                                    text=f"Кажется, вы давно не хейтили {name} {surname}. Захейтим прямо сейчас?",
#                                    reply_markup=yesno_markup(rb[0], rb[1]))
