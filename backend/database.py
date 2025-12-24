import sqlite3

DB_NAME = "timesense.db"

def get_db():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Users
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password_hash TEXT
    )
    """)

    # User-specific bias
    cur.execute("""
    CREATE TABLE IF NOT EXISTS model_state (
        user_id INTEGER,
        key TEXT,
        value REAL,
        PRIMARY KEY (user_id, key)
    )
    """)

    # User-specific learned keywords
    cur.execute("""
    CREATE TABLE IF NOT EXISTS keyword_weights (
        user_id INTEGER,
        keyword TEXT,
        weight REAL,
        PRIMARY KEY (user_id, keyword)
    )
    """)

    # User-specific word statistics
    cur.execute("""
    CREATE TABLE IF NOT EXISTS word_stats (
        user_id INTEGER,
        word TEXT,
        count INTEGER,
        impact REAL,
        PRIMARY KEY (user_id, word)
    )
    """)

    conn.commit()
    conn.close()
