const API_URL = "https://timesense.onrender.com/";

function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  if (!email || !password) {
    alert("Please enter email and password");
    return;
  }

  fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        // 🔑 THIS IS THE IMPORTANT PART
        localStorage.setItem("user_id", data.user_id);

        // Redirect to dashboard
        window.location.href = "index.html";
      } else {
        alert("Invalid email or password");
      }
    })
    .catch(err => {
      alert("Login failed. Backend not reachable.");
      console.error(err);
    });
}
