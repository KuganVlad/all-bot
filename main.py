import configparser
from aiogram import executor
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3
import db_function
import bot_function
from geo_data import find_nearest_city


config = configparser.ConfigParser()
config.read("config.ini")
TOKEN = config['Telegram']['bot_token']
admin_id = config['Telegram']['admin_id']

# Создаем объекты бота и диспетчера
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Определяем состояния для вопроса
class UserStates(StatesGroup):
    MAIN_MENU = State()
    ASKING_QUESTION = State()
    ANSWERING_QUESTION = State()

# Определяем состояния для старта
class StartStates(StatesGroup):
    WHAT_NAME = State()
    WHAT_AGE = State()
    WHAT_CITY = State()



@dp.message_handler(Command("start"), state="*")
async def start(message: types.Message, state: FSMContext):
    # Очищаем состояние пользователя при старте
    await state.finish()
    user_id = message.from_user.id
    if db_function.is_admin_allowed(user_id):
        await message.answer("Приветствую! админ")
    elif db_function.is_user_allowed(user_id):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["О модельной школе", "Направления обучения", "Учебные дисциплины", "Преподаватели",
               "События", "Запись на кастинг", "Задать вопрос?"]
        keyboard.add(*buttons)
        await message.answer("Выбери интересующий раздел", reply_markup=keyboard)
        await UserStates.MAIN_MENU.set()
    else:
        # Информация для простох пользователей
        await message.answer("Приветствую! Давай дружить! Как тебя зовут?")
        await StartStates.WHAT_NAME.set()

@dp.message_handler(Command("help"), state="*")
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    if db_function.is_user_allowed(user_id):
        await message.answer("Описание бота для зарегистрированного пользователя")
        await UserStates.MAIN_MENU.set()
    else:
        # Информация для простох пользователей
        await message.answer("Описание бота для зарегистрированного пользователя")
        await StartStates.WHAT_NAME.set()

# Начала диалога для пользователя, запрос имени
@dp.message_handler(state=StartStates.WHAT_NAME)
async def ask_question(message: types.Message, state: FSMContext):
    first_name = message.text
    age = None
    city = None
    # Сохраняем имя пользователя в состояние
    await state.update_data(first_name=first_name)
    await message.answer("Сколько тебе лет?")
    await StartStates.WHAT_AGE.set()

# запрос возраста
@dp.message_handler(state=StartStates.WHAT_AGE)
async def ask_question(message: types.Message, state: FSMContext):
    # Получаем возраст пользователя
    age = message.text
    await message.answer("Отлично! А теперь введи свой город:")
    # Устанавливаем состояние ASKING_CITY
    await StartStates.WHAT_CITY.set()
    # Сохраняем возраст пользователя в состояние
    await state.update_data(age=age)

# запрос города, запись первичной информации в базу данных
@dp.message_handler(state=StartStates.WHAT_CITY)
async def ask_question(message: types.Message, state: FSMContext):
    # Получаем возраст пользователя
    city = message.text
    data = await state.get_data()
    first_name = data.get("first_name")
    age = data.get("age")

    # Сохраняем данные пользователя в базу данных
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()

    # Проверяем, существует ли пользователь с данным tg_user_id
    cursor.execute('SELECT tg_user_id FROM users WHERE tg_user_id = ?', (message.from_user.id,))
    existing_user = cursor.fetchone()

    if existing_user:
        # Пользователь уже зарегистрирован, выполняем операцию обновления данных
        cursor.execute('''
            UPDATE users SET tg_first_name=?, tg_last_name=?, tg_user_name=?, first_name=?, last_name=?, second_name=?, age=?, city=?, phone_number=?, casting_status=?, casting_id=?
            WHERE tg_user_id=?
        ''', (message.from_user.first_name, message.from_user.last_name, message.from_user.username,
              first_name, None, None, age, city, None, None, None, message.from_user.id))
    else:
        # Пользователь не зарегистрирован, выполняем операцию вставки
        cursor.execute('''
            INSERT INTO users (tg_user_id, tg_first_name, tg_last_name, tg_user_name, first_name, last_name, second_name, age, city, phone_number, casting_status, casting_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (message.from_user.id, message.from_user.first_name, message.from_user.last_name,
              message.from_user.username, first_name, None, None, age, city, None, None, None))

    conn.commit()
    conn.close()

    # Отправляем приветственное сообщение и главное меню
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["О модельной школе", "Направления обучения", "Учебные дисциплины", "Преподаватели",
               "События", "Запись на кастинг", "Задать вопрос?"]
    keyboard.add(*buttons)
    await message.answer(f"Добро пожаловать в бот-помощник модельной школы All-models!\n"
                         f"Здесь ты можешь ознакомиться с информацией о модельной школе, направлениях обучения,\n"
                         f"учебных дисциплинах, преподавателях, предстоящих событиях, записаться на кастинг\n"
                         f"или же задать интересующий тебя вопрос!", reply_markup=keyboard)

    # Устанавливаем состояние MAIN_MENU
    await UserStates.MAIN_MENU.set()

# Функция возврата в главное меню
@dp.message_handler(lambda message: message.text == "Вернуться в главное меню", state="*")
async def return_start(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    if db_function.is_user_allowed(user_id):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["О модельной школе", "Направления обучения", "Учебные дисциплины", "Преподаватели",
               "События", "Запись на кастинг", "Задать вопрос?"]
        keyboard.add(*buttons)
        await message.answer("Выбери интересующий раздел", reply_markup=keyboard)
        await UserStates.MAIN_MENU.set()
    else:
        await message.answer("Доступ закрыт.")


@dp.message_handler()
async def handle_button_click(message: types.Message):
    user_id = message.from_user.id
    if db_function.is_user_allowed(user_id):
        if message.text == "О модельной школе":
            data = bot_function.get_reference_school_information()
            if data:
                await message.answer(data[0])
            else:
                await message.answer("Запрашиваемая информация отсутствует")

        elif message.text == "Направления обучения":
            data = bot_function.get_information_on_destinations()
            if data:
                await message.answer(data[0])
            else:
                await message.answer("Запрашиваемая информация отсутствует")
        elif message.text == "Учебные дисциплины":
            data = bot_function.get_academic_disciplines()
            if data:
                await message.answer(data[0])
            else:
                await message.answer("Запрашиваемая информация отсутствует")
        elif message.text == "Преподаватели":
            user_city = db_function.get_user_city(user_id)
            if db_function.get_filial_at_city(user_city[0]):
                pass
            else:
                nearest_city = find_nearest_city(user_city[0])
                await message.answer(f"К сожалению мы ещё не открыли филиал в вашем городе,\n"
                                     f"но мы будем очень рады вас видеть в нашем филиале\n в г. {nearest_city}e\n"
                                     f"где вас встретит наш дружный коллектив:\n")

        elif message.text == "События":
            pass
        elif message.text == "Запись на кастинг":
            pass
        else:
            await message.answer("Неизвестная команда")
    else:
        await message.answer("Для получения доступа к боту необходимо пройти процедуру регистрации")


# Раздел задать вопрос
@dp.message_handler(text="Задать вопрос?", state=UserStates.MAIN_MENU)
async def ask_question(message: types.Message, state: FSMContext):
    # Устанавливаем состояние ASKING_QUESTION
    await UserStates.ASKING_QUESTION.set()
    await message.answer("Введите свой вопрос:")
    # Сохраняем идентификатор пользователя, чтобы отправить ему ответ
    await state.update_data(user_id=message.from_user.id)

@dp.message_handler(state=UserStates.ASKING_QUESTION)
async def process_question(message: types.Message, state: FSMContext):
    # Получаем идентификатор пользователя и вопрос из состояния
    data = await state.get_data()
    user_id = data.get("user_id")
    question = message.text

    # Создаем Inline кнопку "Ответить"
    reply_button = InlineKeyboardButton(text="Ответить", callback_data=f"answer:{user_id}")

    # Отправляем вопрос администратору с кнопкой "Ответить"
    await bot.send_message(admin_id, f"Новый вопрос от пользователя (ID: {user_id}):\n\n{question}",
                           reply_markup=InlineKeyboardMarkup().add(reply_button))

    # Устанавливаем состояние MAIN_MENU
    await UserStates.MAIN_MENU.set()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Задать вопрос?", "Вернуться в главное меню")
    await message.answer("Спасибо за ваш вопрос! Мы ответим вам в ближайшее время.", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("answer:"), state="*")
async def answer_question_callback(query: types.CallbackQuery, state: FSMContext):
    # Извлекаем идентификатор пользователя из данных callback-кнопки
    user_id = int(query.data.split(":")[1])

    # Устанавливаем состояние ANSWERING_QUESTION
    await UserStates.ANSWERING_QUESTION.set()
    await state.update_data(user_id=user_id)

    # Отправляем запрос администратору для получения ответа
    await query.message.answer("Введите ответ на вопрос пользователя:")


@dp.message_handler(state=UserStates.ANSWERING_QUESTION)
async def process_answer(query: types.Message, state: FSMContext):
    # Получаем идентификатор пользователя и ответ из состояния
    data = await state.get_data()
    user_id = data.get("user_id")
    answer = query.text

    # Отправляем ответ пользователю
    await bot.send_message(user_id, f"Ответ от администратора:\n\n{answer}")

    # Устанавливаем состояние MAIN_MENU
    await UserStates.MAIN_MENU.set()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Преподаватели", "События", "Запись на кастинг")
    await query.answer("Ответ успешно отправлен пользователю.")



if __name__ == '__main__':
    db_function.create_db()
    executor.start_polling(dp, skip_updates=True)