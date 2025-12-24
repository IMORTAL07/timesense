const API_URL = "https://timesense.onrender.com/";

let tasks = [];

function addTask() {
  const text = document.getElementById("taskText").value;
  const category = document.getElementById("category").value;

  fetch(`${API_URL}/predict`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ task: text, category })
  })
  .then(res => res.json())
  .then(data => {
    const task = {
      id: Date.now(),
      text,
      category,
      predicted: data.predicted_time,
      elapsed: 0,
      timer: null,
      startTime: null
    };
    tasks.push(task);
    renderTasks();
  });
}

function renderTasks() {
  const container = document.getElementById("taskList");
  container.innerHTML = "";

  tasks.forEach(task => {
    const div = document.createElement("div");
    div.className = "task-card";

    div.innerHTML = `
      <div class="task-header">
        <span>${task.text}</span>
        <span>⏳ Est: ${task.predicted} min</span>
      </div>

      <div class="timer" id="timer-${task.id}">
        Elapsed: ${Math.floor(task.elapsed / 60)} min
      </div>

      <button class="small" onclick="startTimer(${task.id})">Start</button>
      <button class="small" onclick="stopTimer(${task.id})">Stop</button>
      <button class="small" onclick="completeTask(${task.id})">Complete</button>
    `;

    container.appendChild(div);
  });
}

function startTimer(id) {
  const task = tasks.find(t => t.id === id);
  if (task.timer) return;

  task.startTime = Date.now();
  task.timer = setInterval(() => {
    task.elapsed += 1;
    document.getElementById(`timer-${id}`).innerText =
      `Elapsed: ${Math.floor(task.elapsed / 60)} min`;
  }, 1000);
}

function stopTimer(id) {
  const task = tasks.find(t => t.id === id);
  clearInterval(task.timer);
  task.timer = null;
}

function completeTask(id) {
  const task = tasks.find(t => t.id === id);
  stopTimer(id);

  const actualMinutes = Math.ceil(task.elapsed / 60);

  fetch(`${API_URL}/feedback`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      predicted: task.predicted,
      actual: actualMinutes
    })
  });

  tasks = tasks.filter(t => t.id !== id);
  renderTasks();
}
