import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
if not bot_token:
    raise Exception("TELEGRAM_BOT_TOKEN не найден в .env")

bot = Bot(token=bot_token)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    print("Команда /start получена")
    await message.answer("Привет! Бот работает.")

async def main():
    print("Запускаем polling...")
    await dp.start_polling(bot)
    print("Polling остановлен")

if __name__ == "__main__":
    print("Старт бота")
    asyncio.run(main())
    print("Бот завершил работу")
