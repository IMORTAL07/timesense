from database import get_db, init_db

init_db()

BASE_TIME = {
    "assignment": 60,
    "lab": 120,
    "study": 45
}

# -------- Bias --------
def load_bias(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT value FROM model_state WHERE user_id=? AND key='bias'",
        (user_id,)
    )
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 1.3

def save_bias(user_id, bias):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO model_state VALUES (?, 'bias', ?)",
        (user_id, bias)
    )
    conn.commit()
    conn.close()

# -------- Keywords --------
def load_keywords(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT keyword, weight FROM keyword_weights WHERE user_id=?",
        (user_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return dict(rows)

def update_or_create_keyword(user_id, keyword, factor):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT weight FROM keyword_weights WHERE user_id=? AND keyword=?",
        (user_id, keyword)
    )
    row = cur.fetchone()

    if row:
        new_weight = min(max(row[0] * factor, 0.8), 2.0)
        cur.execute(
            "UPDATE keyword_weights SET weight=? WHERE user_id=? AND keyword=?",
            (new_weight, user_id, keyword)
        )
    else:
        cur.execute(
            "INSERT INTO keyword_weights VALUES (?, ?, ?)",
            (user_id, keyword, 1.05)
        )

    conn.commit()
    conn.close()

# -------- Word Statistics --------
def record_word_impact(user_id, word, error_ratio):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT count, impact FROM word_stats WHERE user_id=? AND word=?",
        (user_id, word)
    )
    row = cur.fetchone()

    if row:
        count, impact = row
        new_impact = (impact * count + error_ratio) / (count + 1)
        cur.execute(
            "UPDATE word_stats SET count=?, impact=? WHERE user_id=? AND word=?",
            (count + 1, new_impact, user_id, word)
        )
    else:
        cur.execute(
            "INSERT INTO word_stats VALUES (?, ?, ?, ?)",
            (user_id, word, 1, error_ratio)
        )

    conn.commit()
    conn.close()

def is_learned_work_word(user_id, word):
    if len(word) < 4:
        return False

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT count, impact FROM word_stats WHERE user_id=? AND word=?",
        (user_id, word)
    )
    row = cur.fetchone()
    conn.close()

    return row and row[0] >= 3 and row[1] > 1.1

# -------- Prediction --------
def predict_time(user_id, task, category):
    base = BASE_TIME.get(category, 60)
    bias = load_bias(user_id)
    keywords = load_keywords(user_id)

    multiplier = 1.0
    for word in task.lower().split():
        if word in keywords:
            multiplier *= keywords[word]

    return round(base * multiplier * bias, 2)

# -------- Learning --------
def learn(user_id, predicted, actual, task):
    error_ratio = actual / predicted

    bias = load_bias(user_id)
    save_bias(user_id, (bias * 0.7) + (error_ratio * 0.3))

    for word in task.lower().split():
        record_word_impact(user_id, word, error_ratio)

        if is_learned_work_word(user_id, word):
            if error_ratio > 1.15:
                update_or_create_keyword(user_id, word, 1.03)
            elif error_ratio < 0.9:
                update_or_create_keyword(user_id, word, 0.97)
