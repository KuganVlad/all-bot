import sqlite3

# Создание базы данных
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
            phone_number TEXT,
            casting_status TEXT,
            casting_id INTEGER,
            FOREIGN KEY (casting_id) REFERENCES castings (casting_id)
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

    # Создаем таблицу casting
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS castings (
            casting_id INTEGER PRIMARY KEY AUTOINCREMENT,
            casting_city TEXT,
            casting_date TEXT,
            casting_time TEXT,
            casting_status INTEGER,
            casting_counter INTEGER
        )
    ''')


    # Создаем таблицу teacher & manager
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_name TEXT,
            teacher_major TEXT,
            teacher_description TEXT,
            teacher_city TEXT,
            tacher_contact TEXT,
            teacher_status INTEGER,
            is_manager INTEGER
        )
    ''')

    # Создаем таблицу event
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_city TEXT,
            event_date TEXT,
            event_time TEXT,
            event_name TEXT,
            casting_status INTEGER
        )
    ''')

    # Создаем таблицу city
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS city (
            city_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_city TEXT,
            filial_status_kids INTEGER,
            filial_status_scouting INTEGER,
            filial_status_age INTEGER
        )
    ''')
    # Сохраняем изменения в базе данных
    conn.commit()

    # Закрываем подключение к базе данных
    conn.close()

#  Проверка администратора
def is_admin_allowed(user_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM admins WHERE tg_admin_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return bool(user)

# Проверка пользователя
def is_user_allowed(user_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE tg_user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return bool(user)

# получение информации о городе пользователя
def get_user_city(user_id):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    cursor.execute('SELECT city FROM users WHERE tg_user_id = ?', (user_id,))
    user_city = cursor.fetchone()
    conn.close()
    return user_city

# проверка наличия города в котором есть филиал
def get_filial_at_city(city_name):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    cursor.execute('SELECT name_city FROM city WHERE name_city = ?', (city_name,))
    city_exist = cursor.fetchone()
    conn.close()
    return bool(city_exist)