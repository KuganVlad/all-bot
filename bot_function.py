import sqlite3

# запрос информации о модельной школе
def get_reference_school_information():
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT data_text FROM data WHERE data_name = "reference_information"')
        text_model_shool = cursor.fetchone()
    except Exception as e:
        text_model_shool = ("Запрашиваемая информация отсутствует",)
        print(e)
    conn.close()
    return text_model_shool

# запрос информации о направлениях деятельности
def get_information_on_destinations():
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT data_text FROM data WHERE data_name = "information_on_destinations"')
        text_destinations = cursor.fetchone()
    except Exception as e:
        text_destinations = ["Запрашиваемая информация отсутствует"]
        print(e)
    conn.close()

    return text_destinations

# запрос информации о дисциплинах
def get_academic_disciplines():
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT data_text FROM data WHERE data_name = "academic_disciplines"')
        text_disciplines = cursor.fetchone()
    except Exception as e:
        text_disciplines = ["Запрашиваемая информация отсутствует"]
        print(e)
    conn.close()

    return text_disciplines

# запрос информации о преподавателях