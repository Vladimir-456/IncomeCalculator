import psycopg2
from psycopg2 import Error
from datetime import datetime



def create_connection():
    try:
        conn = psycopg2.connect(user="postgres",
                                  password="12",
                                  host="127.0.0.1",
                                  port="5432",
                                  database='Calculator')
        print("Вы успешно подключены")
        return conn

    except (Exception, psycopg2.Error) as error :
        print("Ошибка при работе с PostgreSQL", error)


def add_user(telegram_id, username, first_name):
    """Добавление нового пользователя"""
    conn = create_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        # Проверяем, существует ли пользователь
        cursor.execute("SELECT id FROM clients WHERE telegram_id = %s", (telegram_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            print(f"Пользователь с telegram_id {telegram_id} уже существует")
            return existing_user[0]  # Возвращаем ID существующего пользователя

        # Добавляем нового пользователя
        insert_query = '''
                       INSERT INTO clients (telegram_id, username, first_name, registration_date, timezone, currency, \
                                          reminder_enabled)
                       VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id; '''

        cursor.execute(insert_query, (
            telegram_id,
            username,
            first_name,
            datetime.now(),
            'Europe/Moscow',  # По умолчанию
            'RUB',  # По умолчанию
            True  # Напоминания включены
        ))

        user_id = cursor.fetchone()[0]
        conn.commit()
        print(f"Пользователь успешно добавлен с ID: {user_id}")
        return user_id

    except (Exception, psycopg2.Error) as error:
        print("Ошибка при добавлении пользователя:", error)
        conn.rollback()
        return False

    finally:
        if conn:
            cursor.close()
            conn.close()

def today():
    conn = create_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        # Получаем только дату
        today_date = datetime.today().date()
        cursor.execute("SELECT SUM(amount) FROM profits_clients WHERE date = %s", (today_date,))
        sum_amount = cursor.fetchone()[0]
        return sum_amount if sum_amount is not None else 0
    except (Exception, psycopg2.Error) as error:
        print("Ошибка в PostgreSQL", error)
        return False

def add_profit(user_id, amount, date=datetime.today(), category=None, description=None):
    """Добавление записи о прибыли"""
    conn = create_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()

        # Проверяем, есть ли уже запись за эту дату
        cursor.execute(
            "SELECT id FROM profits_clients WHERE user_id = %s AND date = %s",
            (user_id, date)
        )
        existing_profit = cursor.fetchone()

        if existing_profit:
            # Обновляем существующую запись
            update_query = '''
                           UPDATE profits_clients
                           SET amount      = %s, \
                               category    = %s, \
                               description = %s, \
                               updated_at  = %s
                           WHERE user_id = %s \
                             AND date = %s \
                           '''
            cursor.execute(update_query, (
                amount, category, description, datetime.now(), user_id, date
            ))
            print(f"Прибыль за {date} обновлена: {amount}")
        else:
            # Добавляем новую запись
            insert_query = '''
                           INSERT INTO profits_clients (user_id, date, amount, category, description, created_at, updated_at)
                           VALUES (%s, %s, %s, %s, %s, %s, %s) \
                           '''
            cursor.execute(insert_query, (
                user_id, date, amount, category, description, datetime.now(), datetime.now()
            ))
            print(f"Добавлена новая запись о прибыли: {amount} за {date}")

        conn.commit()
        return True

    except (Exception, psycopg2.Error) as error:
        print("Ошибка при добавлении прибыли:", error)
        conn.rollback()
        return False

    finally:
        if conn:
            cursor.close()
            conn.close()