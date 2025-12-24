from flask import Flask, request, jsonify
from flask_cors import CORS
from logic import predict_time, learn

app = Flask(__name__)
CORS(app)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    predicted = predict_time(data["task"], data["category"])
    return jsonify({"predicted_time": predicted})

@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.json
    learn(
        predicted=data["predicted"],
        actual=data["actual"],
        task=data["task"]
    )
    return jsonify({"status": "learning updated"})

@app.route("/")
def home():
    return "TimeSense backend running"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
