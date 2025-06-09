from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from database.models import User, Referral
from services.marketing import generate_referral_code, calculate_commissions
from services.utils import get_user_language
from config import Config

config = Config()

async def marketing_panel(message: types.Message):
    user = await User.get(telegram_id=message.from_user.id)
    if not user.is_marketer:
        # فعال‌سازی کاربر به عنوان بازاریاب
        await generate_referral_code(user.id)
        user.is_marketer = True
        await user.save()
    
    lang = user.language
    
    # ایجاد لینک دعوت
    bot_username = (await message.bot.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start=ref-{user.referral_code}"
    
    # دریافت آمار بازاریابی
    level1_count = await Referral.filter(referrer=user, level=1).count()
    level2_count = await Referral.filter(referrer=user, level=2).count()
    level3_count = await Referral.filter(referrer=user, level=3).count()
    total_commission = user.balance
    
    text = (
        f"👤 پنل بازاریابی\n\n"
        f"🔗 لینک دعوت شما:\n<code>{referral_link}</code>\n\n"
        f"📊 آمار:\n"
        f"• سطح 1: {level1_count} کاربر\n"
        f"• سطح 2: {level2_count} کاربر\n"
        f"• سطح 3: {level3_count} کاربر\n"
        f"💵 مجموع درآمد: {total_commission} USDT"
    )
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(
        text="درخواست برداشت",
        callback_data="withdraw_request"
    ))
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

async def handle_withdraw_request(callback: types.CallbackQuery):
    # ثبت درخواست برداشت
    await callback.answer("درخواست برداشت شما ثبت شد. ظرف 24 ساعت پرداخت انجام می‌شود.")

def register_marketing_handlers(dp: Dispatcher):
    dp.register_message_handler(marketing_panel, Command("marketing"), state="*")
    dp.register_message_handler(marketing_panel, text="پنل بازاریابی", state="*")
    dp.register_callback_query_handler(handle_withdraw_request, text="withdraw_request")