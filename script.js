const API_URL = "https://timesense.onrender.com";

function predictTime() {
  const task = document.getElementById("task").value;
  const category = document.getElementById("category").value;

  fetch(`${API_URL}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ task, category })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById("result").innerText =
      "Predicted Time: " + data.predicted_time + " minutes";
  });
}
