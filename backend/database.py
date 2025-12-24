import sqlite3

def get_db():
    return sqlite3.connect("timesense.db")

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS model_state (
        key TEXT PRIMARY KEY,
        value REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS keyword_weights (
        keyword TEXT PRIMARY KEY,
        weight REAL
    )
    """)

    conn.commit()
    conn.close()
