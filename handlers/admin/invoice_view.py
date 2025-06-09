from aiogram import Router, types
from app.services.payments import get_recent_invoices
from app.services.auth import is_admin

router = Router()

@router.message(lambda m: m.text == "🧾 فاکتورها")
async def show_invoices(message: types.Message):
    if not await is_admin(message.from_user.id):
        return await message.answer("⛔️ شما مدیر نیستید.")

    invoices = await get_recent_invoices(limit=10)
    if not invoices:
        return await message.answer("هیچ فاکتوری موجود نیست.")
    
    for inv in invoices:
        text = (
            f"🧾 فاکتور #{inv.id}\n"
            f"👤 کاربر: {inv.username or inv.user_id}\n"
            f"💰 مبلغ: {inv.amount} تومان\n"
            f"🗓 تاریخ: {inv.created_at.strftime('%Y-%m-%d')}\n"
            f"📦 پلن: {inv.plan_name}\n"
            f"✅ وضعیت: {'تایید شده' if inv.status == 'approved' else 'در انتظار'}"
        )
        await message.answer(text)
from aiogram import Router, types
from app.services.db import async_session
from app.models.invoice import Invoice
from sqlalchemy.future import select

router = Router()

@router.message(lambda m: m.text.startswith("🧾 فاکتورهای پرداخت"))
async def show_invoices(message: types.Message):
    async with async_session() as session:
        result = await session.execute(select(Invoice).order_by(Invoice.created_at.desc()).limit(10))
        invoices = result.scalars().all()
        if not invoices:
            await message.answer("📭 هیچ فاکتوری یافت نشد.")
            return
        text = "📋 آخرین فاکتورهای ثبت‌شده:\n\n"
        for inv in invoices:
            text += (
                f"🧾 فاکتور #{inv.id}\n"
                f"👤 کاربر: {inv.user_id}\n"
                f"💳 روش: {inv.method}\n"
                f"💰 مبلغ: {inv.amount} USDT\n"
                f"⏱ تاریخ: {inv.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"🔑 وضعیت: {inv.status}\n\n"
            )
        await message.answer(text)
