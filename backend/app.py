from flask import Flask, request, jsonify
from flask_cors import CORS
from logic import predict_time, update_bias

app = Flask(__name__)
CORS(app)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    task = data["task"]
    category = data["category"]

    predicted_time = predict_time(task, category)

    return jsonify({
        "predicted_time": predicted_time
    })

@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.json
    update_bias(data["predicted"], data["actual"])

    return jsonify({"status": "bias updated"})

if __name__ == "__main__":
    app.run(debug=True)
