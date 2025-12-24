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

# default bias (user usually underestimates)
USER_BIAS = 1.3

def predict_time(task, category):
    base_time = CATEGORY_BASE_TIME.get(category, 60)
    multiplier = 1.0

    task = task.lower()
    for keyword, factor in KEYWORD_MULTIPLIER.items():
        if keyword in task:
            multiplier *= factor

    predicted = base_time * multiplier * USER_BIAS
    return round(predicted, 2)

def update_bias(predicted, actual):
    global USER_BIAS
    USER_BIAS = actual / predicted
