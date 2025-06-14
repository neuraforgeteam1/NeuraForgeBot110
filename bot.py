import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
from config import Config

async def health_check(request):
    return web.Response(text="OK")

async def main():
    # تنظیمات لاگینگ
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    config = Config()
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # تنظیم دستورات منو
    await bot.set_my_commands([
        types.BotCommand(command="start", description="شروع کار"),
        types.BotCommand(command="help", description="راهنما")
    ])
    
    # ثبت هندلرها
    @dp.message(F.command == "start")
    async def cmd_start(message: types.Message):
        await message.answer("سلام! به ربات خوش آمدید.")
    
    # ایجاد سرور سلامت
    app = web.Application()
    app.add_routes([web.get("/health", health_check)])
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=8080)
    await site.start()
    
    try:
        # حذف به‌روزرسانی‌های قدیمی
        await bot.delete_webhook(drop_pending_updates=True)
        
        # شروع پولینگ
        logging.info("Starting bot polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        
    except Exception as e:
        logging.error(f"Bot stopped with error: {e}")
    finally:
        await runner.cleanup()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())