import sqlite3
from datetime import datetime

DB_NAME = "chat_logs.db"


# -------- CONNECTION --------
def get_connection():
    conn = sqlite3.connect(
        DB_NAME,
        timeout=30,
        check_same_thread=False
    )

    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")

    return conn


# -------- INIT DB --------
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # chats table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            bot_reply TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # faq table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# -------- SAVE CHAT --------
def save_chat(user_message, bot_reply):
    conn = get_connection()
    cursor = conn.cursor()

    local_time = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")

    cursor.execute("""
        INSERT INTO chats (user_message, bot_reply, created_at)
        VALUES (?, ?, ?)
    """, (user_message, bot_reply, local_time))

    conn.commit()
    conn.close()


# -------- GET CHATS --------
def get_all_chats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_message, bot_reply, created_at
        FROM chats
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


# -------- SEED FAQ (DEFAULT DATA) --------
def seed_faq():
    conn = get_connection()
    cursor = conn.cursor()

    faq_data = [
        ("refund policy", "Refunds are processed within 5-7 business days after approval."),
        ("shipping time", "Standard shipping takes 3-5 business days."),
        ("cancel order", "Orders can be cancelled before shipment."),
        ("reset password", "Click 'Forgot Password' on login page to reset your password."),
        ("subscription plans", "We offer Basic, Pro, and Enterprise subscription plans."),
        ("delivery delay", "Delivery delays may happen due to weather or logistics issues."),
        ("return product", "Products can be returned within 7 days of delivery."),
        ("contact support", "You can contact support by email, phone, or live chat.")
    ]

    cursor.execute("SELECT COUNT(*) FROM faq")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany("""
            INSERT INTO faq (question, answer)
            VALUES (?, ?)
        """, faq_data)

        conn.commit()

    conn.close()


# -------- FAQ OPERATIONS --------
def add_faq(question, answer):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO faq (question, answer)
        VALUES (?, ?)
    """, (question, answer))

    conn.commit()
    conn.close()


def delete_faq(faq_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM faq WHERE id = ?
    """, (faq_id,))

    conn.commit()
    conn.close()


def get_all_faq():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, question, answer
        FROM faq
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows