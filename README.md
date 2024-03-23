# Телеграм бот для рассылки сообщений
### Вашему вниманию представляется простой пример кода на языке Python для создания Telegram-bota, который будет производить рассылку сообщений всем взаимодействующим с ним пользователям, с подробным описанием каждого шага. Итоговый код бота будет представден в конце статьи.
Рекомендуемые версии Python:
```
Python 3.8 и выше
```
В первую очередь необходимо установить все необходимые зависимости:
```
pip install aiogram==2.25.2
pip install python-dotenv
pip install aioschedule
```
Обращаю внимание на версию библиотеки ```aiogram==2.25.2```, если использовать другую версию некоторые методы могут работать некоректно.

Для корректного хранения ```API_token``` бота в дериктории нашего проекта создаем файл ```.env``` и записываем туда токен бота:
```
TOKEN = 'api токен бота'
```
Теперь непосредственно переходим к написаю бота. В этой же директории создаем файл ```main.py``` и импортируем необходимые библиотеки:
```
from aiogram import Bot, Dispatcher, executor
import aioschedule
import asyncio
import os
from dotenv import load_dotenv
```
Импортируем api токен бота из файла ```.env```:
```
load_dotenv()
TOKEN = os.getenv('TOKEN')
```
Создаем бота с его api токеном:
```
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
```
Прописываем функцию обработки начала работы с ботом (по команде ```/start```)
```
@dp.message_handler(commands='start')
async def start(mes):
    user_id = mes.from_user.id
    await mes.answer('Привет! Тут ты будешь получать рассылку.')
    new_user(user_id)
```
Первая строка ```@dp.message_handler(commands='start')``` - это обработчик команды ```/start```,  ```async def start(mes):``` - определение функции с аргументом ```mes```, который дает боту полную информации о полученном сообщении (текст сообщения, id отправителя и т.д.), ```user_id = mes.from_user.id``` - в переменную ```user_id``` записываем id отправителя сообщения, ```await mes.answer('Привет! Тут ты будешь получать рассылку.')``` - бот в ответ отправляет сообщение и информирует пользователя о том, что теперь он участвует в получении рассылки сообщений, ```new_user(user_id)``` - вызов функции ```new_user``` с передачей в нее id пользователя.

Необходимо создать функцию ```new_user``` для записи id пользователей участвующих в рассылке сообщений:
```
def new_user(uid):
    if str(uid) + '\n' not in get_users_list():
        with open('users.txt', 'a') as f:
            f.write(str(uid) + '\n')
```
Проверяем нет ли данного пользователя в файле ```users.txt``` с помощью вызова функции ```get_users_list()```, если его id отсутсвует, то с помощью контекстного менеджера ```with``` открываем файл и записываем id нового пользователя. Файл ```users.txt``` заранее создавать не обязательно.

Создаем фунцию ```get_users_list()``` для получения массива пользователей из файла ```users.txt```:
```
def get_users_list():
    with open('users.txt', 'r') as f:
        return f.readlines()
```
Наконец создаем обработчик команды ```/mailing```, чтобы владелец или администратор бота мог вручную запускать рассылку сообщений через бота:
```
@dp.message_handler(commands='mailing')
async def mailing(mes):
    user_id = mes.from_user.id
    if user_id == 111111111:  # Тут id того, кому можно выполнять команду рассылки
        await start_mailing()
```
Для выполнения рассылки в последней строке вызываеться функция ```start_mailing```, не забудьде заменить ```user_id``` на id вашего телеграмм профиля:
```
async def start_mailing():  # Функция рассылки
    for i in get_users_list():
        try:
            await bot.send_message(chat_id=i,
                                   text='Это рассылка')
        except:
            pass
```
С помощью цикла ```for``` проходимся по всем имеющимся id пользователей и отправляем им сообщение, конструкция ```try except``` используется для предотвращения остановки работы бота, в случае если он не сможет отправить сообщение какому-либо пользователю. 

Мы сделали ручной вызов рассылки, это хорошо, но еще лучше если мы автоматизируем этот процесс, для этого применим библиотеку ```aioschedule```:
```
async def scheduler():
    aioschedule.every().day.at('10:00').do(start_mailing)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup():
    asyncio.create_task(scheduler())
```
Первая функция ```scheduler()``` отвечает за выполнение рассылки каждый день в 10 часов утра: ```aioschedule.every().day.at('10:00').do(start_mailing)```, в данной строке можно убрать часть ```at('10:00')```, тогда оповещение будет происходить каждый день с момента начала работы бота. Если вам необходимо производить рассылку чаще, то можно заменить часть ```every().day``` например на ```every(30).seconds```,```every(10).minutes```,```every().hour``` или каждый понедельник ```every().monday```, здесь все на ваше усмотрение. Цикл ```while True``` обеспечивает постоянную работу функции.
Вторая функция ```n_startup()``` запускает первую функцию при запуске бота.

Для красоты можно написать обработчик сообщений от пользователей, например:
```
@dp.message_handler()
async def error_mes(mes):
    await mes.answer('Я бот, который не умеет отвечать на сообщения!')
```

Ну и в завершении, обязательно добавить данные строки для работы нашего бота:
```
if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
```
Аргумент ```on_startup``` необходим для запуска функции, которая непосредственно запускает функцию автоматизированной рассылки сообщений пользователям.

### Итоговый код:
```
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
    aioschedule.every().day.at('20:55').do(start_mailing)
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
    if user_id == 335679271:  # Тут id того, кому можно выполнять команду рассылки
        await start_mailing()


@dp.message_handler()
async def error_mes(mes):
    await mes.answer('Я бот, который не умеет отвечать на сообщения!')


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
```
### Вот так довольно просто можно реальзовать бота рассылки сообщений.







































