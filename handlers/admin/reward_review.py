from aiogram import Router, types
from app.services.rewards import get_pending_rewards, approve_reward, reject_reward
from app.services.auth import is_admin

router = Router()

@router.message(lambda m: m.text == "🎁 بررسی جوایز")
async def show_rewards(message: types.Message):
    if not await is_admin(message.from_user.id):
        return await message.answer("⛔️ دسترسی ندارید.")
    
    rewards = await get_pending_rewards()
    if not rewards:
        return await message.answer("هیچ درخواست جایزه‌ای وجود ندارد.")
    
    for reward in rewards:
        await message.answer(
            f"🆔 کاربر: {reward.user_id}\n"
            f"🎯 امتیاز: {reward.points}\n"
            f"📦 نوع درخواست: {reward.request_type}",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="✅ تایید", callback_data=f"reward_approve:{reward.id}")],
                    [types.InlineKeyboardButton(text="❌ رد", callback_data=f"reward_reject:{reward.id}")]
                ]
            )
        )
