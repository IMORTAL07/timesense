CATEGORY_BASE_TIME = {
    "assignment": 60,
    "lab": 120,
    "study": 45
}

KEYWORD_MULTIPLIER = {
    "report": 1.4,
    "analysis": 1.3,
    "final": 1.5,
    "revision": 1.2
}

# adaptive bias (this is your ML-like learning)
USER_BIAS = 1.3  

def predict_time(task, category):
    base = CATEGORY_BASE_TIME.get(category, 60)
    multiplier = 1.0

    task = task.lower()
    for key, factor in KEYWORD_MULTIPLIER.items():
        if key in task:
            multiplier *= factor

    predicted = base * multiplier * USER_BIAS
    return round(predicted, 2)

def update_bias(predicted, actual):
    global USER_BIAS
    new_bias = actual / predicted
    # smooth learning (prevents wild jumps)
    USER_BIAS = (USER_BIAS * 0.7) + (new_bias * 0.3)
