import logging
import asyncio
import sys
from pathlib import Path
from aiogram import Bot
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import Config

# تنظیمات مسیر برای Render.com
try:
    site_packages = str(Path(__file__).parent / '.venv' / 'lib' / 'python3.11' / 'site-packages')
    if site_packages not in sys.path:
        sys.path.append(site_packages)
except Exception as e:
    logging.warning(f"Could not add site-packages to path: {e}")

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    config = Config()
    storage = MemoryStorage()
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=storage)
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())

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
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=storage)
    
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

    # bot.py
from aiogram import Bot, Dispatcher
from config import Config

# تغییر در نحوه ایمپورت
from handlers.user import register_user_handlers
from handlers.admin import register_admin_handlers
from handlers.marketing import register_marketing_handlers
from handlers.payment import register_payment_handlers

async def main():
    config = Config()
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(bot)
    
    # ثبت هندلرها
    register_user_handlers(dp)
    register_admin_handlers(dp)
    register_marketing_handlers(dp)
    register_payment_handlers(dp)
    
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())

async def main():
    config = Config()
    
    if not config.TRON_WALLET:
        logging.warning("TRON_WALLET not set, some payment features may be disabled")
    
    # بقیه کدهای راه‌اندازی...