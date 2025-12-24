const API_URL = "https://timesense.onrender.com/";

function login() {
  fetch(`${API_URL}/login`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      email: email.value,
      password: password.value
    })
  })
  .then(r => r.json())
  .then(d => {
    if (d.success) {
      localStorage.setItem("user_id", d.user_id);
      window.location.href = "index.html";
    } else {
      alert("Invalid credentials");
    }
  });
}
