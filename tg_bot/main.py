import logging
from os import getenv

import keyboards
import messages
import redis
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.builtin import CommandStart
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = getenv('TG_BOT_TOKEN')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

r = redis.StrictRedis(
    host=getenv('TG_REDIS_HOST'),
    port=getenv('REDIS_PORT'),
    password=getenv('REDIS_PASSWORD'),
    charset='utf-8',
    decode_responses=True
)


@dp.message_handler(CommandStart())
async def send_welcome(message: types.Message):
    await message.answer(messages.START.format(message.chat.first_name), parse_mode='HTML', reply_markup=keyboards.START)


@dp.message_handler(content_types=['text'])
async def key(message: types.Message):
    if message.text == 'Список товаров':
        await message.delete()
        last_parsing = r.get('last_parsing')
        await message.answer(last_parsing) if last_parsing != None else await message.answer('Нет данных о последнем парсинге')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
