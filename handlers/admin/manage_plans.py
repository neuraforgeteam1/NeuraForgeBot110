from aiogram import Router, types
from app.services.db import async_session
from app.models.plan import Plan
from app.utils.translation import t

router = Router()

@router.message(lambda msg: msg.text == t("manage_plans", "fa"))
async def manage_plans_handler(message: types.Message):
    lang = "fa"
    async with async_session() as session:
        plans = await session.execute(Plan.__table__.select())
        plan_list = plans.fetchall()

    msg = t("plan_list_header", lang)
    for p in plan_list:
        msg += f"\n📦 {p.name} - {p.duration} روزه - {p.price} تومان"

    await message.answer(msg or t("no_plans", lang))
