from flask import Flask, request, jsonify
from flask_cors import CORS
from logic import predict_time, learn
from auth import create_user, authenticate_user

app = Flask(__name__)
CORS(app)

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    success = create_user(data["email"], data["password"])
    return jsonify({"success": success})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user_id = authenticate_user(data["email"], data["password"])
    return jsonify({"success": bool(user_id), "user_id": user_id})

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    time = predict_time(
        data["user_id"],
        data["task"],
        data["category"]
    )
    return jsonify({"predicted_time": time})

@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.json
    learn(
        data["user_id"],
        data["predicted"],
        data["actual"],
        data["task"]
    )
    return jsonify({"status": "learning updated"})

@app.route("/")
def home():
    return "TimeSense backend running"

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
