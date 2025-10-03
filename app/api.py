from flask import Blueprint, request, jsonify, current_app
import uuid
from .tasks.runner import runner, TaskState, example_dilute

bp = Blueprint("api", __name__, url_prefix="/api")

@bp.route("/ping")
def ping():
    return {"status": "ok"}

@bp.route("/run", methods=["POST"])
def run_program():
    data = request.get_json(force=True, silent=True) or {}
    program = data.get("program")
    params = data.get("params", {})
    if program != "dilute":
        return jsonify({"error": "unknown program"}), 400
    task_id = str(uuid.uuid4())
    state = TaskState(name=program, params=params)
    runner.start_task(task_id, example_dilute, state)
    return {"task_id": task_id}

@bp.route("/status/<task_id>")
def status(task_id: str):
    st = runner.get(task_id)
    if not st:
        return jsonify({"error": "not found"}), 404
    return vars(st)

@bp.route("/tasks")
def tasks():
    return runner.list_states()

