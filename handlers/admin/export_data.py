from aiogram import Router, types
from app.services.stats import export_users_csv
from aiogram.types import FSInputFile
from app.services.auth import is_admin

router = Router()

@router.message(lambda m: m.text == "📤 خروجی کاربران")
async def export_users(message: types.Message):
    if not await is_admin(message.from_user.id):
        return await message.answer("⛔️ فقط مدیر مجاز است.")

    path = await export_users_csv()
    file = FSInputFile(path)
    await message.answer_document(file, caption="📊 خروجی کاربران به‌صورت CSV آماده است.")
from aiogram import Router, types
from app.services.exporter import export_users_to_excel
from aiogram.types import FSInputFile

router = Router()

@router.message(lambda msg: msg.text == "📤 خروجی کاربران")
async def export_users(message: types.Message):
    path = await export_users_to_excel()
    await message.answer_document(FSInputFile(path), caption="📊 خروجی کاربران به اکسل")
