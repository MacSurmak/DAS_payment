import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties

from config_data import config
from handlers import commands, messages, admin
from keyboards.commands_menu import set_commands_menu
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from services import setup_logger
from services.services import notify_day_before


async def main() -> None:

    bot: Bot = Bot(token=config.bot.token,
                   default=DefaultBotProperties(parse_mode='HTML'))

    dp: Dispatcher = Dispatcher()

    dp.include_router(admin.router)
    dp.include_router(commands.router)
    dp.include_router(messages.router)

    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.start()

    # scheduler.add_job(update_counter, 'cron', hour='00', minute='00')
    scheduler.add_job(notify_day_before, 'cron', hour='9-18', minute='*/5', args=[bot])

    await set_commands_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)

    polling_task = asyncio.create_task(dp.start_polling(bot))

    await polling_task


if __name__ == '__main__':
    setup_logger("DEBUG")
    asyncio.run(main())
