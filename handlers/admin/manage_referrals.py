from aiogram import Router, types, F
from app.services.referrals import list_marketers, update_commissions, get_commission_config
from app.utils.translation import t

router = Router()

@router.message(lambda msg: msg.text == t("manage_marketers", "fa"))
async def marketers_list_handler(message: types.Message):
    lang = "fa"
    marketers = await list_marketers()
    commission = await get_commission_config()

    msg = f"📊 <b>{t('marketer_list', lang)}</b>"
    msg += f"\n🧮 <b>درصد پورسانت فعلی:</b>\n"
    msg += f"🔸 سطح 1: {commission['level_1']}٪\n"
    msg += f"🔸 سطح 2: {commission['level_2']}٪\n"
    msg += f"🔸 سطح 3: {commission['level_3']}٪\n"

    if not marketers:
        msg += f"\n\n{t('no_marketers', lang)}"
    else:
        msg += f"\n\n👥 <b>لیست بازاریاب‌ها:</b>"
        for m in marketers:
            msg += f"\n• @{m['username'] or '-'} | امتیاز: {m['points']} | سطح: {m['level']}"

    await message.answer(msg)

@router.message(F.text.startswith("/set_commission"))
async def set_commission_handler(message: types.Message):
    try:
        _, l1, l2, l3 = message.text.split()
        await update_commissions(int(l1), int(l2), int(l3))
        await message.answer("✅ درصدهای جدید با موفقیت ثبت شدند.")
    except:
        await message.answer("❌ فرمت دستور اشتباه است. نمونه صحیح:\n/set_commission 15 10 5")
from app.services.settings import get_commission_config, update_commissions