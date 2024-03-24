from aiogram import Bot, Dispatcher, executor
import aioschedule
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


def get_users_list():
    with open('users.txt', 'r') as f:
        return f.readlines()


def new_user(uid):
    if str(uid) + '\n' not in get_users_list():
        with open('users.txt', 'a') as f:
            f.write(str(uid) + '\n')


async def start_mailing():  # Функция рассылки
    for i in get_users_list():
        try:
            await bot.send_message(chat_id=i,
                                   text='Это рассылка')
        except:
            pass


async def scheduler():
    aioschedule.every().day.at('10:00').do(start_mailing)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup():
    asyncio.create_task(scheduler())


@dp.message_handler(commands='start')
async def start(mes):
    user_id = mes.from_user.id
    await mes.answer('Привет! Тут ты будешь получать рассылку.')
    new_user(user_id)


@dp.message_handler(commands='mailing')
async def mailing(mes):
    user_id = mes.from_user.id
    if user_id == 111111111:  # Тут id того, кому можно выполнять команду рассылки
        await start_mailing()


@dp.message_handler()
async def error_mes(mes):
    await mes.answer('Я бот, который не умеет отвечать на сообщения!')


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
