import sqlite3

DB_NAME = "timesense.db"

def get_db():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Global model state (bias)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS model_state (
        key TEXT PRIMARY KEY,
        value REAL
    )
    """)

    # Learned keyword weights
    cur.execute("""
    CREATE TABLE IF NOT EXISTS keyword_weights (
        keyword TEXT PRIMARY KEY,
        weight REAL
    )
    """)

    # Word statistics for unsupervised learning
    cur.execute("""
    CREATE TABLE IF NOT EXISTS word_stats (
        word TEXT PRIMARY KEY,
        count INTEGER,
        impact REAL
    )
    """)

    conn.commit()
    conn.close()
