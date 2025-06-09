from aiogram import Router, types
from app.services.settings import switch_project, get_all_projects

router = Router()

@router.message(lambda msg: msg.text == "🔀 تغییر پروژه")
async def choose_project(message: types.Message):
    projects = await get_all_projects()
    text = "🗂 لطفاً پروژه مورد نظر را انتخاب کنید:\n"
    for p in projects:
        text += f"/setproject_{p.id} - {p.name}\n"
    await message.answer(text)

@router.message(lambda msg: msg.text.startswith("/setproject_"))
async def set_project(message: types.Message):
    project_id = int(message.text.split("_")[1])
    await switch_project(message.from_user.id, project_id)
    await message.answer(f"✅ پروژه شما تغییر یافت.")
