from flask import Blueprint, request, jsonify, current_app
import uuid
from .tasks.runner import runner, TaskState, example_dilute
from .tasks.commands import start_process, cancel_process, check_factors, run_real_workflow

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
    # check factors
    checkfactors = check_factors(data)
    if isinstance(checkfactors, tuple) and checkfactors[0] is False:
        return jsonify({"error": checkfactors[1]}), 400
    # Nur validieren und aufbereitete Daten zurückgeben; Prozess noch NICHT starten
    return jsonify({"ok": True, "data": data})


@bp.route("/confirm_start", methods=["POST"])
def api_confirm_start():
    payload = request.get_json(force=True, silent=True) or {}
    data = payload.get("data") or payload
    # Start der eigentlichen Logik + paralleler Fortschritts-Task
    start_process(data)
    task_id = str(uuid.uuid4())
    state = TaskState(name="workflow", params=data)
    runner.start_task(task_id, lambda s: run_real_workflow(s, data), state)
    return jsonify({"ok": True, "task_id": task_id})


@bp.route("/cancel", methods=["POST"])
def api_cancel():
    data = request.get_json(force=True, silent=True) or {}
    task_id = data.get("task_id")
    runner_ack = False
    if task_id:
        runner_ack = runner.request_cancel(task_id)
    result = cancel_process(data)
    return jsonify({"ok": True, "cancel_ack": runner_ack, **result})

