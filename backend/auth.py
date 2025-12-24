from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db

def create_user(email, password):
    conn = get_db()
    cur = conn.cursor()

    password_hash = generate_password_hash(password)

    try:
        cur.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email, password_hash)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, password_hash FROM users WHERE email=?",
        (email,)
    )
    row = cur.fetchone()
    conn.close()

    if row and check_password_hash(row[1], password):
        return row[0]

    return None
