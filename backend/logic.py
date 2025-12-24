from database import get_db, init_db

init_db()

# ------------------------------
# Base category times (minutes)
# ------------------------------
BASE_TIME = {
    "assignment": 60,
    "lab": 120,
    "study": 45
}

# ------------------------------
# Bias handling
# ------------------------------
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
    cur.execute(
        "INSERT OR REPLACE INTO model_state VALUES ('bias', ?)",
        (bias,)
    )
    conn.commit()
    conn.close()

# ------------------------------
# Keyword weight handling
# ------------------------------
def load_keywords():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT keyword, weight FROM keyword_weights")
    rows = cur.fetchall()
    conn.close()
    return dict(rows)

def update_or_create_keyword(keyword, factor):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT weight FROM keyword_weights WHERE keyword=?",
        (keyword,)
    )
    row = cur.fetchone()

    if row:
        # Smooth bounded update
        new_weight = min(max(row[0] * factor, 0.8), 2.0)
        cur.execute(
            "UPDATE keyword_weights SET weight=? WHERE keyword=?",
            (new_weight, keyword)
        )
    else:
        # New learned work-type keyword
        cur.execute(
            "INSERT INTO keyword_weights VALUES (?, ?)",
            (keyword, 1.05)
        )

    conn.commit()
    conn.close()

# ------------------------------
# Word statistics (unsupervised)
# ------------------------------
def record_word_impact(word, error_ratio):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT count, impact FROM word_stats WHERE word=?",
        (word,)
    )
    row = cur.fetchone()

    if row:
        count, impact = row
        new_impact = (impact * count + error_ratio) / (count + 1)
        cur.execute(
            "UPDATE word_stats SET count=?, impact=? WHERE word=?",
            (count + 1, new_impact, word)
        )
    else:
        cur.execute(
            "INSERT INTO word_stats VALUES (?, ?, ?)",
            (word, 1, error_ratio)
        )

    conn.commit()
    conn.close()

def is_learned_work_word(word):
    if len(word) < 4:
        return False

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT count, impact FROM word_stats WHERE word=?",
        (word,)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return False

    count, impact = row

    # Learned criteria:
    # appears often AND consistently increases effort
    return count >= 3 and impact > 1.1

# ------------------------------
# Prediction
# ------------------------------
def predict_time(task, category):
    bias = load_bias()
    keywords = load_keywords()

    base = BASE_TIME.get(category, 60)
    multiplier = 1.0

    for word in task.lower().split():
        if word in keywords:
            multiplier *= keywords[word]

    return round(base * multiplier * bias, 2)

# ------------------------------
# Learning loop
# ------------------------------
def learn(predicted, actual, task):
    error_ratio = actual / predicted

    # ---- Bias learning (global behavior) ----
    bias = load_bias()
    new_bias = (bias * 0.7) + (error_ratio * 0.3)
    save_bias(new_bias)

    # ---- Word learning (unsupervised) ----
    words = task.lower().split()

    for word in words:
        record_word_impact(word, error_ratio)

        if is_learned_work_word(word):
            if error_ratio > 1.15:
                update_or_create_keyword(word, 1.03)
            elif error_ratio < 0.9:
                update_or_create_keyword(word, 0.97)
