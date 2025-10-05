import threading
import time
from typing import Dict, Optional, Callable, Any

class TaskState:
    def __init__(self, name: str, params: dict):
        self.name = name
        self.params = params
        self.progress = 0
        self.state = "running"  # running|finished|error|stopped
        self.message = ""
        self.cancel_requested = False

class TaskRunner:
    def __init__(self):
        self._tasks: Dict[str, TaskState] = {}
        self._lock = threading.Lock()

    def start_task(self, task_id: str, func: Callable[[TaskState], None], state: TaskState):
        with self._lock:
            self._tasks[task_id] = state
        t = threading.Thread(target=self._run_wrapper, args=(task_id, func), daemon=True)
        t.start()

    def _run_wrapper(self, task_id: str, func: Callable[[TaskState], None]):
        state = self._tasks[task_id]
        try:
            func(state)
            if state.state == "running":
                state.state = "finished"
        except Exception as e:  # pylint: disable=broad-except
            state.state = "error"
            state.message = str(e)

    def get(self, task_id: str) -> Optional[TaskState]:
        return self._tasks.get(task_id)

    def list_states(self) -> Dict[str, Any]:
        return {k: vars(v) for k, v in self._tasks.items()}

    def request_cancel(self, task_id: str) -> bool:
        st = self._tasks.get(task_id)
        if not st:
            return False
        st.cancel_requested = True
        st.message = st.message or ""
        if st.state == "running":
            st.message = (st.message + " | ").strip(" | ") + "Abbruch angefordert"
        return True

runner = TaskRunner()

def example_dilute(state: TaskState):
    total_steps = 20
    for i in range(total_steps):
        time.sleep(0.1)
        state.progress = int(((i + 1) / total_steps) * 100)
    # Ende -> state.state wird im Wrapper auf finished gesetzt
