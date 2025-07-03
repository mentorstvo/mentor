import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
import httpx

from aiogram.client.default import DefaultBotProperties
from prompts import create_friendly_feedback  # Импорт функции из prompts.py

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not TELEGRAM_BOT_TOKEN or not OPENROUTER_API_KEY:
    raise ValueError("В .env отсутствует TELEGRAM_BOT_TOKEN или OPENROUTER_API_KEY")

bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()
router = Router()
dp.include_router(router)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = (
    "Ты — дружелюбный и мотивирующий ментор, который даёт каждый раз разную развернутую обратную связь стажёру по его показателям работы. "
    "Объясни, почему показатели AHT, ДУ и Transfer должны стремиться к 100%, а Навигация — быть минимум 45%, "
    "поясни, что значит значение ниже этих порогов и какие это несёт последствия. "
    "Используй технику «бутерброд»: начни с похвалы, затем аккуратно укажи на зоны для улучшения с конкретными рекомендациями, "
    "и заверши поддержкой и мотивацией, чтобы стажёр почувствовал вдохновение для роста. "
    "Обращайся по имени, используй живой, дружелюбный и искренний тон. "
    "Примеры рекомендаций:\n"
    "- Если AHT ниже 100%, посоветуй автоматизировать рутинные вопросы с помощью IVR или чат-ботов, а также подготовить скрипты для частых вопросов.\n"
    "- Если ДУ ниже 100%, порекомендуй активно слушать клиента, задавать уточняющие вопросы, проявлять эмпатию и предлагать альтернативы.\n"
    "- Если Навигация ниже 45%, подчеркни, что это зона роста и важно работать над эффективной фразой для просьбы оценки, больше запрашивать.\n"
    "- Если Transfer ниже 100%, посоветуй избегать некорректных переводов и всегда уточнять у наставника разрешение, если показатель ниже 70%.\n"
    "Делай текст вдохновляющим и очень персональным, чтобы стажёр почувствовал заботу и поддержку."
)


@router.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "👋 Привет! Введи имя стажёра и его показатели в процентах.\n\n"
        "Пример сообщения:\n"
        "Иван\n"
        "AHT: 85%\n"
        "ДУ: 92%\n"
        "Навигация: 75%\n"
        "Transfer: 10%\n"
        "Дополнительно (по желанию): часто перебивает клиента"
    )

@router.message(F.text)
async def handle_metrics(message: Message):
    text = message.text.strip()
    lines = text.split("\n")

    if len(lines) < 5:
        await message.answer(
            "❗️ Пожалуйста, введи имя и все четыре показателя (AHT, ДУ, Навигация, Transfer) в формате:\n"
            "Иван\nAHT: 85%\nДУ: 92%\nНавигация: 75%\nTransfer: 10%\nДополнительно (по желанию): часто перебивает клиента"
        )
        return

    name = lines[0].strip()

    metrics = {}
    comment = ""
    for line in lines[1:]:
        if ':' in line:
            key, val = line.split(":", 1)
            metrics[key.strip()] = val.strip()
        else:
            comment += line.strip() + " "

    # Генерируем дружелюбную обратную связь с рекомендациями и фразами
    feedback = create_friendly_feedback(name, metrics, comment)

    # Опционально: можно отправлять запрос в OpenRouter для дополнительного AI-анализа (если нужно)
    # Ниже пример с комментарием, можно раскомментировать при желании

    # headers = {
    #     "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    #     "Content-Type": "application/json"
    # }
    # payload = {
    #     "model": "gpt-4o-mini",
    #     "messages": [
    #         {"role": "system", "content": SYSTEM_PROMPT},
    #         {"role": "user", "content": feedback}
    #     ],
    #     "temperature": 0.8
    # }
    #
    # try:
    #     async with httpx.AsyncClient() as client:
    #         response = await client.post(OPENROUTER_URL, json=payload, headers=headers)
    #         response.raise_for_status()
    #         data = response.json()
    #         ai_reply = data["choices"][0]["message"]["content"]
    #         await message.answer(ai_reply)
    #         return
    # except Exception as e:
    #     await message.answer(f"❌ Ошибка при обращении к OpenRouter API:\n<code>{str(e)}</code>")
    #     return

    # Если не используем API, отправляем сразу локальный ответ
    await message.answer(feedback)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
