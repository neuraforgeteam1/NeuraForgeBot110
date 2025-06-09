from aiogram import Router, types
from app.services.db import async_session
from app.models.user import User
from app.utils.translation import t

router = Router()

@router.message(lambda msg: msg.text == t("manage_users", "fa"))
async def list_users_handler(message: types.Message):
    lang = "fa"
    async with async_session() as session:
        users = await session.execute(User.__table__.select().limit(10))
        users_list = users.fetchall()

    msg = t("user_list_header", lang)
    for u in users_list:
        msg += f"\n👤 @{u.username or '-'} | ID: {u.id}"

    await message.answer(msg or t("no_users_found", lang))
