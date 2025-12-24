from database import get_db, init_db

init_db()

BASE_TIME = {
    "assignment": 60,
    "lab": 120,
    "study": 45
}

DEFAULT_KEYWORDS = {
    "report": 1.4,
    "analysis": 1.3,
    "final": 1.5,
    "revision": 1.2,
    "research": 1.4,
    "coding": 1.6,
    "debug": 1.3,
    "design": 1.3,
    "presentation": 1.2,
    "documentation": 1.25,
    "numerical": 1.35,
    "simulation": 1.45,
    "testing": 1.3
}

def load_bias():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT value FROM model_state WHERE key='bias'")
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 1.3

def save_bias(bias):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO model_state VALUES ('bias', ?)", (bias,))
    conn.commit()
    conn.close()

def load_keywords():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT keyword, weight FROM keyword_weights")
    rows = cur.fetchall()

    if not rows:
        for k, v in DEFAULT_KEYWORDS.items():
            cur.execute("INSERT OR IGNORE INTO keyword_weights VALUES (?, ?)", (k, v))
        conn.commit()
        rows = DEFAULT_KEYWORDS.items()

    conn.close()
    return dict(rows)

def update_keyword(keyword, factor):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    INSERT OR REPLACE INTO keyword_weights
    VALUES (?, COALESCE((SELECT weight FROM keyword_weights WHERE keyword=?), 1.0) * ?)
    """, (keyword, keyword, factor))
    conn.commit()
    conn.close()

def predict_time(task, category):
    keywords = load_keywords()
    bias = load_bias()

    base = BASE_TIME.get(category, 60)
    multiplier = 1.0

    words = task.lower().split()
    for word in words:
        if word in keywords:
            multiplier *= keywords[word]

    return round(base * multiplier * bias, 2)

def learn(predicted, actual, task):
    bias = load_bias()
    error_ratio = actual / predicted

    new_bias = (bias * 0.7) + (error_ratio * 0.3)
    save_bias(new_bias)

    if error_ratio > 1.15:
        for word in task.lower().split():
            update_keyword(word, 1.02)
    elif error_ratio < 0.9:
        for word in task.lower().split():
            update_keyword(word, 0.98)
