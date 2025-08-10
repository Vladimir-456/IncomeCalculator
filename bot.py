import asyncio
from os.path import split
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from models import add_user, add_profit, today
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.validate import ProfitValidator, ValidationError
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from datetime import date
import logging

logger = logging.getLogger(__name__)
# import os
BOT_TOKEN = '8164556484:AAFEZYa89soIDMQlFWlBcVaeeEfGtMTxcB0'
# bot = Bot(token=os.getenv('BOT_TOKEN'))
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

class AddProfit(StatesGroup):
    profit = State()

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить прибыль")],
        [KeyboardButton(text="Статистика")],
        [KeyboardButton(text="Помощь")]
    ],
    resize_keyboard=True
)
@dp.message(lambda message: message.text == "Помощь")
async def help_message(message: Message):
    await message.answer("Я помогу вам учитывать ваши доходы и расходы.")

@dp.message(lambda message: message.text == "Добавить прибыль")
async def add_payment(message: Message, state: FSMContext):
    await message.answer("Введите сумму платежа и дату, пример - 1000 2024-06-01:")
    await state.set_state(AddProfit.profit)

@dp.message(AddProfit.profit)
async def process_payment(message: Message, state: FSMContext):
    try:
        amount, profit_date = ProfitValidator.parse_profit_input(message.text)
        if profit_date is None:
            profit_date = date.today()
        print(amount, profit_date)

        add_profit(message.from_user.id, amount, profit_date)

        # date_text = "сегодня" if profit_date == date.today() else profit_date.strftime('%d.%m.%Y')
        emoji = "💰" if amount > 0 else "📉"

        await message.answer(
            f"✅ {emoji} Прибыль успешно добавлена!\n"
            f"📅 Дата: {profit_date}\n"
            f"💵 Сумма: {amount}$"
        )
        await state.clear()
    except ValidationError as e:
        # Ошибки валидации - показываем пользователю
        await message.answer(
            f"❌ {str(e)}\n\n"
            f"📝 Примеры правильного ввода:\n"
            f"• 1000 (прибыль за сегодня)\n"
            f"• 500 2024-06-25\n"
            f"• -200 вчера (убыток)\n"
            f"• 1500 25.06.2024"
        )

    except Exception as e:
        # Неожиданные ошибки - логируем и показываем общее сообщение
        logger.error(f"Unexpected error in process_profit_input: {e}", exc_info=True)
        await message.answer(
            "❌ Произошла системная ошибка. Попробуйте позже или обратитесь к администратору."
        )

@dp.message(CommandStart())
async def cmd_start(message: Message):
    add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    await message.answer("Привет! Я бот для учета прибыли.", reply_markup=main_kb)

@dp.message(lambda message: message.text == "/today")
async def cmd_today(message: Message):
    sum_amount = today()
    if(sum_amount is False):
        await message.answer("Ошибка при получении прибыли за сегодня.")
    else:
        await message.answer(f"Прибыль за сегодня — {sum_amount}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())