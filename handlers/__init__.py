from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command('start'))
async def start(message: Message):
    await message.answer("Привет! Я помогу тебе узнать твой ID, просто отправь мне любое сообщение")

@router.message()
async def start(message: Message):
    await message.answer(f'Твой ID: {message.from_user.id}')