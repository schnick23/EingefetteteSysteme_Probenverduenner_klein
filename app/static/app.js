async function startProgram() {
  const factor = parseInt(document.getElementById('factor').value, 10);
  const volume = parseFloat(document.getElementById('volume').value);
  const res = await fetch('/api/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ program: 'dilute', params: { factor, volume } })
  });
  const data = await res.json();
  if (data.task_id) {
    console.log('Task gestartet', data.task_id);
    refreshTasks();
  } else {
    alert('Fehler: ' + JSON.stringify(data));
  }
}

async function refreshTasks() {
  const res = await fetch('/api/tasks');
  const tasks = await res.json();
  const container = document.getElementById('tasks');
  container.innerHTML = '';
  Object.entries(tasks).forEach(([id, st]) => {
    const div = document.createElement('div');
    div.className = 'task';
    div.textContent = `${id} => ${st.name} ${st.progress}% (${st.state})`;
    container.appendChild(div);
  });
}

setInterval(refreshTasks, 2000);

document.getElementById('startBtn').addEventListener('click', startProgram);
refreshTasks();
