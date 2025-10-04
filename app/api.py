from flask import Blueprint, request, jsonify, current_app
import uuid
from .tasks.runner import runner, TaskState, example_dilute
from .tasks.commands import start_process, cancel_process

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

    # optional: Layout-Infos entgegennehmen
    grid = params.get("grid")
    stock_volume = params.get("stockVolume")
    # Minimalvalidierung (nicht blockierend fürs MVP)
    if grid is not None and not isinstance(grid, list):
        return jsonify({"error": "grid must be a 2D list"}), 400
    if stock_volume is not None:
        try:
            float(stock_volume)
        except Exception:  # noqa: BLE001
            return jsonify({"error": "stockVolume must be a number"}), 400

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


@bp.route("/start", methods=["POST"])
def api_start():
    data = request.get_json(force=True, silent=True) or {}
    # Erwartete Felder: grid, factors (map), enabledRows (map/bool-list), stockVolume
    # Wir loggen serverseitig in commands.start_process
    result = start_process(data)
    return jsonify({"ok": True, **result})


@bp.route("/cancel", methods=["POST"])
def api_cancel():
    data = request.get_json(force=True, silent=True) or {}
    result = cancel_process(data)
    return jsonify({"ok": True, **result})

