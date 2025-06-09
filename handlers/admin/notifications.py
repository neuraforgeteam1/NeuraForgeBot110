from aiogram import Bot

async def notify_admins(bot: Bot, text: str, admin_ids: list[int]):
    for admin_id in admin_ids:
        try:
            await bot.send_message(admin_id, f"📢 اعلان مدیریتی:\n{text}")
        except Exception:
            continue
from aiogram import Bot
from app.config import settings

# لیست مدیران در .env تعریف می‌شه
ADMIN_IDS = list(map(int, settings.ADMIN_IDS.split(",")))

async def notify_admins(bot: Bot, text: str):
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, f"🔔 {text}")
        except Exception as e:
            print(f"❌ Failed to notify {admin_id}: {e}")
