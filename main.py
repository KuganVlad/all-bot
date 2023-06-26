import configparser
from aiogram import executor
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3


config = configparser.ConfigParser()
config.read("config.ini")
TOKEN = config['Telegram']['bot_token']
admin_id = config['Telegram']['admin_id']

# Создаем объекты бота и диспетчера
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Определяем состояния для FSM
class UserStates(StatesGroup):
    MAIN_MENU = State()
    ASKING_QUESTION = State()
    ANSWERING_QUESTION = State()

class StartStates(StatesGroup):
    WHAT_NAME = State()
    WHAT_AGE = State()
    WHAT_CITY = State()


def create_db():
    # Создаем подключение к базе данных
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()

    # Создаем таблицу users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_user_id INTEGER UNIQUE,
            tg_first_name TEXT,
            tg_last_name TEXT,
            tg_user_name TEXT,
            first_name TEXT,
            last_name TEXT,
            second_name TEXT,
            age INTEGER,
            city TEXT,
            phone_number TEXT
        )
    ''')

    # Создаем таблицу admins
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_admin_id INTEGER UNIQUE
        )
    ''')

    # Создаем таблицу questions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id_questions INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            user_id INTEGER,
            date_time_question TEXT,
            answer TEXT,
            admin_id INTEGER,
            date_time_answer TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (admin_id) REFERENCES admins (admin_id)
        )
    ''')

    # Создаем таблицу data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data (
            data_id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_name TEXT,
            data_text TEXT
        )
    ''')

    # Сохраняем изменения в базе данных
    conn.commit()

    # Закрываем подключение к базе данных
    conn.close()

def is_user_allowed(user_id):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE tg_user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return bool(user)



@dp.message_handler(Command("start"), state="*")
async def start(message: types.Message, state: FSMContext):
    # Очищаем состояние пользователя при старте
    await state.finish()
    user_id = message.from_user.id
    if is_user_allowed(user_id):
        await message.answer("Приветствую! админ")
    else:
        # Информация для простох пользователей
        await message.answer("Приветствую! Давай дружить! Как тебя зовут?")
        await StartStates.WHAT_NAME.set()

@dp.message_handler(text="Задать вопрос?", state=StartStates.WHAT_NAME)
async def ask_question(message: types.Message, state: FSMContext):
    first_name = message.text
    last_name = None
    second_name = None
    age = None
    city = None
    # Устанавливаем состояние ASKING_QUESTION
    await message.answer("Сколько тебе лет?")
    await StartStates.WHAT_AGE.set()




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
async def process_answer(message: types.Message, state: FSMContext):
    # Получаем идентификатор пользователя и ответ из состояния
    data = await state.get_data()
    user_id = data.get("user_id")
    answer = message.text

    # Отправляем ответ пользователю
    await bot.send_message(user_id, f"Ответ от администратора:\n\n{answer}")

    # Устанавливаем состояние MAIN_MENU
    await UserStates.MAIN_MENU.set()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Задать вопрос?", "Вернуться в главное меню")
    await message.answer("Ответ успешно отправлен пользователю.", reply_markup=keyboard)

if __name__ == '__main__':
    create_db()
    executor.start_polling(dp, skip_updates=True)