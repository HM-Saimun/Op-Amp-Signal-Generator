import json
import math
import sqlite3
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
from flask import Flask, current_app, g, jsonify, render_template, request, send_from_directory, url_for

matplotlib.use("Agg")

import differentiator
import integrator
import inverting_amp
import non_inverting_amp
import summing_amp


PROJECT_DIR = Path(__file__).resolve().parent
RESISTANCE_UNITS = {"ohm": 1, "kOhm": 1e3, "MOhm": 1e6}
VOLTAGE_UNITS = {"V": 1, "mV": 1e-3}
CAPACITANCE_UNITS = {
    "F": 1,
    "mF": 1e-3,
    "uF": 1e-6,
    "nF": 1e-9,
    "pF": 1e-12,
}
AMPLIFIERS = {
    "inverting": ("Inverting amplifier", inverting_amp),
    "non_inverting": ("Non-inverting amplifier", non_inverting_amp),
    "integrator": ("Integrator", integrator),
    "differentiator": ("Differentiator", differentiator),
    "summing": ("Summing amplifier", summing_amp),
}


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=str(PROJECT_DIR / "simulation_history.db"),
        OUTPUT_DIR=str(PROJECT_DIR / "output_signals"),
        OPEN_MATPLOTLIB_WINDOW=True,
    )
    if test_config:
        app.config.update(test_config)

    @app.teardown_appcontext
    def close_database(_error=None):
        database = g.pop("database", None)
        if database is not None:
            database.close()

    @app.get("/")
    def home():
        return render_template("index.html")

    @app.get("/outputs/<path:filename>")
    def output_file(filename):
        return send_from_directory(current_app.config["OUTPUT_DIR"], filename)

    @app.get("/api/history")
    def history():
        rows = get_database().execute(
            """
            SELECT id, created_at, amplifier, inputs_json, outputs_json, image_urls_json
            FROM simulation_history
            ORDER BY created_at DESC
            """
        ).fetchall()
        return jsonify(
            [
                {
                    "id": row["id"],
                    "created_at": row["created_at"],
                    "amplifier": row["amplifier"],
                    "inputs": json.loads(row["inputs_json"]),
                    "outputs": summarize_outputs(json.loads(row["outputs_json"])),
                    "image_urls": json.loads(row["image_urls_json"]),
                }
                for row in rows
            ]
        )

    @app.get("/api/history/<run_id>")
    def history_record(run_id):
        row = get_database().execute(
            """
            SELECT id, created_at, amplifier, inputs_json, outputs_json, image_urls_json
            FROM simulation_history
            WHERE id = ?
            """,
            (run_id,),
        ).fetchone()
        if row is None:
            return jsonify({"error": "Simulation session not found."}), 404
        return jsonify(
            {
                "id": row["id"],
                "created_at": row["created_at"],
                "amplifier": row["amplifier"],
                "inputs": json.loads(row["inputs_json"]),
                "outputs": json.loads(row["outputs_json"]),
                "image_urls": json.loads(row["image_urls_json"]),
            }
        )

    @app.post("/api/simulate")
    def simulate():
        try:
            amplifier = request.get_json()
            if not isinstance(amplifier, dict):
                raise ValueError("Request body must be a JSON object.")
            kind = amplifier.get("amplifier")
            if kind not in AMPLIFIERS:
                raise ValueError("Select a valid amplifier.")
            raw_inputs, simulation_inputs = parse_inputs(kind, amplifier.get("inputs"))
        except (KeyError, TypeError, ValueError) as error:
            return jsonify({"error": str(error)}), 400

        kind = amplifier["amplifier"]
        label, simulator = AMPLIFIERS[kind]
        run_id = (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            + f"_{kind}_{uuid.uuid4().hex[:8]}"
        )
        output_dir = Path(current_app.config["OUTPUT_DIR"])
        output_dir.mkdir(parents=True, exist_ok=True)
        output_prefix = output_dir / run_id

        outputs = simulator.run(
            inputs=simulation_inputs,
            output_prefix=str(output_prefix),
        )
        plot_window_error = None
        if current_app.config["OPEN_MATPLOTLIB_WINDOW"]:
            try:
                gui_python = Path(sys.executable).with_name("pythonw.exe")
                executable = (
                    str(gui_python)
                    if sys.platform == "win32" and gui_python.is_file()
                    else sys.executable
                )
                subprocess.Popen(
                    [
                        executable,
                        str(PROJECT_DIR / "matplotlib_window.py"),
                        kind,
                        json.dumps(simulation_inputs),
                    ],
                    cwd=str(PROJECT_DIR),
                    creationflags=(
                        0
                        if executable != sys.executable
                        else getattr(subprocess, "CREATE_NO_WINDOW", 0)
                    ),
                )
            except OSError as error:
                current_app.logger.exception("Could not open Matplotlib window.")
                plot_window_error = (
                    "Simulation completed, but the Matplotlib window could not open."
                )
        suffixes = (
            ["-output.png"]
            if kind in ("integrator", "differentiator")
            else ["-voltage.png", "-current.png"]
        )
        image_urls = [
            url_for("output_file", filename=f"{run_id}{suffix}")
            for suffix in suffixes
        ]
        created_at = datetime.now(timezone.utc).isoformat()
        database = get_database()
        database.execute(
            """
            INSERT INTO simulation_history
                (id, created_at, amplifier, inputs_json, outputs_json, image_urls_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                created_at,
                label,
                json.dumps(raw_inputs),
                json.dumps(outputs, allow_nan=False),
                json.dumps(image_urls),
            ),
        )
        database.commit()
        return jsonify(
            {
                "id": run_id,
                "created_at": created_at,
                "amplifier": label,
                "inputs": raw_inputs,
                "outputs": summarize_outputs(outputs),
                "image_urls": image_urls,
                "plot_window_error": plot_window_error,
            }
        )

    return app


def get_database():
    if "database" not in g:
        database_path = Path(current_app.config["DATABASE"])
        database_path.parent.mkdir(parents=True, exist_ok=True)
        g.database = sqlite3.connect(database_path)
        g.database.row_factory = sqlite3.Row
        g.database.execute(
            """
            CREATE TABLE IF NOT EXISTS simulation_history (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                amplifier TEXT NOT NULL,
                inputs_json TEXT NOT NULL,
                outputs_json TEXT NOT NULL,
                image_urls_json TEXT NOT NULL
            )
            """
        )
        g.database.commit()
    return g.database


def initialize_database(app):
    with app.app_context():
        get_database()


def parse_quantity(inputs, key, scales, minimum=None, positive=False):
    quantity = inputs[key]
    if not isinstance(quantity, dict):
        raise ValueError(f"{key} must include a value and unit.")
    value = float(quantity["value"])
    unit = quantity["unit"]
    if not math.isfinite(value):
        raise ValueError(f"{key} must be a finite number.")
    if unit not in scales:
        raise ValueError(f"{key} has an unsupported unit.")
    normalized = value * scales[unit]
    if not math.isfinite(normalized):
        raise ValueError(f"{key} is outside the supported numeric range.")
    if positive and normalized <= 0:
        raise ValueError(f"{key} must be greater than zero.")
    if minimum is not None and normalized < minimum:
        raise ValueError(f"{key} must be at least {minimum}.")
    return normalized, {"value": value, "unit": unit}


def parse_number(inputs, key, minimum=None, positive=False):
    value = float(inputs[key])
    if not math.isfinite(value):
        raise ValueError(f"{key} must be a finite number.")
    if positive and value <= 0:
        raise ValueError(f"{key} must be greater than zero.")
    if minimum is not None and value < minimum:
        raise ValueError(f"{key} must be at least {minimum}.")
    return value


def parse_inputs(kind, inputs):
    if not isinstance(inputs, dict):
        raise ValueError("Inputs must be a JSON object.")
    raw = {}
    values = {}

    def quantity(key, units, minimum=None, positive=False):
        value, raw[key] = parse_quantity(inputs, key, units, minimum, positive)
        values[key] = value

    def number(key, minimum=None, positive=False):
        values[key] = parse_number(inputs, key, minimum, positive)
        raw[key] = values[key]

    if kind == "inverting":
        for key in ("R", "Rf", "RL"):
            quantity(key, RESISTANCE_UNITS, positive=True)
        quantity("Vin_amp", VOLTAGE_UNITS, 0)
        quantity("Vcc_pos", VOLTAGE_UNITS)
        quantity("Vcc_neg", VOLTAGE_UNITS)
    elif kind == "non_inverting":
        for key in ("R1", "R2", "RL"):
            quantity(key, RESISTANCE_UNITS, positive=True)
        quantity("Vi_amp", VOLTAGE_UNITS, 0)
        quantity("Vcc_pos", VOLTAGE_UNITS)
        quantity("Vcc_neg", VOLTAGE_UNITS)
    elif kind in ("integrator", "differentiator"):
        quantity("R", RESISTANCE_UNITS, positive=True)
        quantity("C", CAPACITANCE_UNITS, positive=True)
        quantity("Vin_amp", VOLTAGE_UNITS, 0)
        signal_type = inputs["signal_type"]
        if signal_type not in ("1", "2", "3"):
            raise ValueError("Select a valid input signal.")
        values["signal_type"] = signal_type
        raw["signal_type"] = signal_type
    elif kind == "summing":
        count_value = float(inputs["signal_count"])
        if not math.isfinite(count_value) or not count_value.is_integer():
            raise ValueError("The number of input signals must be a whole number.")
        count = int(count_value)
        if count < 1 or count > 8:
            raise ValueError("Use between 1 and 8 input signals.")
        amplitudes = []
        resistors = []
        raw["signal_count"] = count
        for index in range(1, count + 1):
            amp_key = f"Vin{index}_amp"
            resistor_key = f"Ri{index}"
            amplitude, raw[amp_key] = parse_quantity(
                inputs, amp_key, VOLTAGE_UNITS, 0
            )
            resistance, raw[resistor_key] = parse_quantity(
                inputs, resistor_key, RESISTANCE_UNITS, positive=True
            )
            amplitudes.append(amplitude)
            resistors.append(resistance)
        quantity("Rf", RESISTANCE_UNITS, positive=True)
        quantity("Vcc_pos", VOLTAGE_UNITS)
        quantity("Vcc_neg", VOLTAGE_UNITS)
        number("f", positive=True)
        quantity("RL", RESISTANCE_UNITS, positive=True)
        values.update({"Vi_amps": amplitudes, "Ri": resistors})
    else:
        raise ValueError("Select a valid amplifier.")

    if "Vcc_pos" in values and values["Vcc_neg"] >= values["Vcc_pos"]:
        raise ValueError("The negative supply rail must be below the positive rail.")

    return raw, values


def summarize_outputs(outputs):
    return {
        key: value
        for key, value in outputs.items()
        if not isinstance(value, (list, dict))
    }


app = create_app()


if __name__ == "__main__":
    initialize_database(app)
    Path(app.config["OUTPUT_DIR"]).mkdir(parents=True, exist_ok=True)
    app.run(host="127.0.0.1", port=5500, debug=False)
