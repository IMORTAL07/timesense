const API_URL = "https://YOUR-RENDER-URL.onrender.com";

/* =====================================
   Authentication Guard
===================================== */
const user_id = localStorage.getItem("user_id");
if (!user_id) {
  window.location.href = "login.html";
}

/* =====================================
   Persistent Task Storage (Per User)
===================================== */
const STORAGE_KEY = `tasks_${user_id}`;
let tasks = JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];

/* =====================================
   Utility Functions
===================================== */
function saveTasks() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
}

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs}s`;
}

/* =====================================
   Add Task
===================================== */
function addTask() {
  const taskText = document.getElementById("taskText").value.trim();
  const category = document.getElementById("category").value;

  if (!taskText) {
    alert("Please enter a task description");
    return;
  }

  fetch(`${API_URL}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: user_id,
      task: taskText,
      category: category
    })
  })
    .then(res => res.json())
    .then(data => {
      const task = {
        id: Date.now(),
        text: taskText,
        category: category,
        predicted: data.predicted_time,
        elapsed: 0,
        running: false,
        intervalId: null
      };

      tasks.push(task);
      saveTasks();
      renderTasks();

      document.getElementById("taskText").value = "";
    })
    .catch(() => alert("Prediction service unavailable"));
}

/* =====================================
   Render Dashboard
===================================== */
function renderTasks() {
  const container = document.getElementById("taskList");
  container.innerHTML = "";

  tasks.forEach(task => {
    const card = document.createElement("div");
    card.className = "task-card";

    card.innerHTML = `
      <div class="task-header">
        <strong>${task.text}</strong>
        <span class="estimate">Est: ${task.predicted} min</span>
      </div>

      <div class="timer" id="timer-${task.id}">
        Elapsed: ${formatTime(task.elapsed)}
      </div>

      <div class="task-controls">
        <button onclick="startTimer(${task.id})">Start</button>
        <button onclick="stopTimer(${task.id})">Stop</button>
        <button onclick="completeTask(${task.id})">Complete</button>
        <button onclick="deleteTask(${task.id})" style="color:#dc2626;">
          Delete
        </button>
      </div>
    `;

    container.appendChild(card);
  });
}

/* =====================================
   Timer Controls
===================================== */
function startTimer(id) {
  const task = tasks.find(t => t.id === id);
  if (!task || task.running) return;

  task.running = true;

  task.intervalId = setInterval(() => {
    task.elapsed += 1;

    const timerEl = document.getElementById(`timer-${id}`);
    if (timerEl) {
      timerEl.innerText = `Elapsed: ${formatTime(task.elapsed)}`;
    }

    saveTasks();
  }, 1000);
}

function stopTimer(id) {
  const task = tasks.find(t => t.id === id);
  if (!task || !task.running) return;

  clearInterval(task.intervalId);
  task.intervalId = null;
  task.running = false;
  saveTasks();
}

/* =====================================
   Complete Task → Learning Trigger
===================================== */
function completeTask(id) {
  const task = tasks.find(t => t.id === id);
  if (!task) return;

  stopTimer(id);

  const actualMinutes = Math.max(1, Math.ceil(task.elapsed / 60));

  fetch(`${API_URL}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: user_id,
      predicted: task.predicted,
      actual: actualMinutes,
      task: task.text
    })
  });

  tasks = tasks.filter(t => t.id !== id);
  saveTasks();
  renderTasks();
}

/* =====================================
   Delete Task (No Learning)
===================================== */
function deleteTask(id) {
  const task = tasks.find(t => t.id === id);
  if (!task) return;

  stopTimer(id);
  tasks = tasks.filter(t => t.id !== id);
  saveTasks();
  renderTasks();
}

/* =====================================
   Logout (Optional but Useful)
===================================== */
function logout() {
  localStorage.removeItem("user_id");
  localStorage.removeItem(STORAGE_KEY);
  window.location.href = "login.html";
}

/* =====================================
   Initialize on Page Load
===================================== */
renderTasks();
