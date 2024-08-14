import asyncio

from aiogram import Bot, Dispatcher

from config_data import config
from handlers import commands
from keyboards.commands_menu import set_commands_menu
from services import setup_logger, update_counter, notify
from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def main() -> None:

    bot: Bot = Bot(token=config.bot.token,
                   parse_mode='HTML')

    dp: Dispatcher = Dispatcher()

    dp.include_router(commands.router)

    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.start()

    scheduler.add_job(update_counter, 'cron', hour='00', minute='00')
    scheduler.add_job(notify, 'cron', hour='12-23', minute='*/5', args=[bot])

    await set_commands_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)

    polling_task = asyncio.create_task(dp.start_polling(bot))

    await polling_task


if __name__ == '__main__':
    setup_logger("DEBUG")
    asyncio.run(main())
