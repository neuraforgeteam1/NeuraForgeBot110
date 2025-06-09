from aiogram import Router, types
from app.services.stats import get_admin_dashboard
from app.utils.translation import t

router = Router()

@router.message(lambda msg: msg.text == t("admin_dashboard", "fa"))
async def admin_dashboard_handler(message: types.Message):
    lang = "fa"
    stats = await get_admin_dashboard()
    text = t("dashboard_template", lang).format(**stats)
    await message.answer(text)
from aiogram import Router, types
from app.services.stats import get_dashboard_data

router = Router()

@router.message(lambda m: m.text.startswith("📊 داشبورد"))
async def show_dashboard(message: types.Message):
    stats = await get_dashboard_data()
    
    text = (
        "📊 داشبورد مدیریتی:\n\n"
        f"👥 کاربران ثبت‌شده: {stats['total_users']}\n"
        f"🧑‍💼 بازاریاب‌ها: {stats['marketers']}\n"
        f"🔐 لایسنس‌های فعال: {stats['active_licenses']}\n"
        f"💰 درآمد تتر: {stats['revenue_tether']} USDT\n"
        f"💳 درآمد ریالی: {stats['revenue_bank']} تومان\n"
        f"🛍 فروش پلن‌ها:\n"
    )

    for plan_name, count in stats["plan_sales"].items():
        text += f"  • {plan_name}: {count} عدد\n"

    text += f"\n🟢 کاربران امروز: {stats['users_today']}\n"
    text += f"📆 کاربران هفته: {stats['users_this_week']}"
    
    await message.answer(text)
