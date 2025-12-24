const API_URL = "https://timesense.onrender.com";

function signup() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  if (!email || !password) {
    alert("Please fill all fields");
    return;
  }

  fetch(`${API_URL}/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        alert("Signup successful! Please login.");
        window.location.href = "login.html";
      } else {
        alert("User already exists.");
      }
    })
    .catch(err => {
      alert("Signup failed. Check backend.");
      console.error(err);
    });
}
