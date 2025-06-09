import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import Config
from database.db import init_db, close_db
from handlers import (
    register_user_handlers,
    register_admin_handlers,
    register_marketing_handlers,
    register_payment_handlers
)
from services.utils import setup_logging

setup_logging()

async def on_startup(dp: Dispatcher):
    await init_db()
    await dp.bot.set_my_commands([
        types.BotCommand("start", "شروع کار با ربات"),
        types.BotCommand("buy", "خرید لایسنس"),
        types.BotCommand("license", "مدیریت لایسنس"),
        types.BotCommand("marketing", "پنل بازاریابی"),
        types.BotCommand("support", "پشتیبانی"),
        types.BotCommand("admin", "ورود به پنل مدیریت")
    ])
    logging.info("Bot started successfully")

async def on_shutdown(dp: Dispatcher):
    await close_db()
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.info("Bot shutdown complete")

async def main():
    config = Config()
    storage = MemoryStorage()
    bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(bot, storage=storage)
    
    register_user_handlers(dp)
    register_admin_handlers(dp)
    register_marketing_handlers(dp)
    register_payment_handlers(dp)
    
    dp.register_startup_handler(on_startup)
    dp.register_shutdown_handler(on_shutdown)
    
    try:
        await dp.start_polling()
    except Exception as e:
        logging.exception("Polling error")
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())