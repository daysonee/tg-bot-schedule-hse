import sqlite3

DB_NAME = "schedule.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            teacher TEXT,
            time TEXT,
            classroom TEXT,
            building TEXT,
            date TEXT,
            type TEXT
        )
    """)
    conn.commit()
    conn.close()


def clear_schedule():
    #Удаляет старое расписание
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM schedule")
        conn.commit()


def add_schedule_entry(subject, teacher, time, classroom, building, date, type):
    #Добавляет одну пару
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            INSERT INTO schedule (subject, teacher, time, classroom, building, date, type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (subject, teacher, time, classroom, building, date, type))
        conn.commit()


def get_schedule_for_date(date):
    #Получить расписание на конкретную дату (формат 02.09)
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT subject, teacher, time, classroom, building, type FROM schedule WHERE date = ?", (date,))
        return cur.fetchall()
