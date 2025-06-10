import logging
import asyncio
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
    
    # ثبت هندلرها به روش جدید aiogram 3.x
    @dp.message(F.text == "/start")
    async def cmd_start(message: types.Message):
        await message.answer("سلام! به ربات خوش آمدید.")
    
    # ایجاد سرور سلامت
    app = web.Application()
    app.add_routes([web.get("/health", health_check)])
    
    try:
        # حذف به‌روزرسانی‌های قدیمی
        await bot.delete_webhook(drop_pending_updates=True)
        
        # سرور سلامت
    app = web.Application()
    app.add_routes([web.get("/health", health_check)])
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", 8080).start()

    try:
        await dp.start_polling(bot)
    finally:
        await runner.cleanup()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(run_bot())