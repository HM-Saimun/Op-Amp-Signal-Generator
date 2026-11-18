import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from web_app import create_app


def quantity(value, unit):
    return {"value": value, "unit": unit}


class WebAppTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        root = Path(self.temporary_directory.name)
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE": str(root / "history.db"),
                "OUTPUT_DIR": str(root / "plots"),
                "OPEN_MATPLOTLIB_WINDOW": False,
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_runs_all_amplifiers_and_persists_waveforms_and_plots(self):
        runs = [
            (
                "inverting",
                {
                    "R": quantity(10, "kOhm"),
                    "Rf": quantity(100, "kOhm"),
                    "Vin_amp": quantity(0.5, "V"),
                    "Vcc_pos": quantity(12, "V"),
                    "Vcc_neg": quantity(-12, "V"),
                    "RL": quantity(10, "kOhm"),
                },
                2,
            ),
            (
                "non_inverting",
                {
                    "R1": quantity(10, "kOhm"),
                    "R2": quantity(90, "kOhm"),
                    "Vcc_pos": quantity(12, "V"),
                    "Vcc_neg": quantity(-12, "V"),
                    "Vi_amp": quantity(0.5, "V"),
                    "RL": quantity(10, "kOhm"),
                },
                2,
            ),
            (
                "integrator",
                {
                    "R": quantity(10, "kOhm"),
                    "C": quantity(100, "nF"),
                    "Vin_amp": quantity(1, "V"),
                    "signal_type": "1",
                },
                1,
            ),
            (
                "differentiator",
                {
                    "R": quantity(10, "kOhm"),
                    "C": quantity(100, "nF"),
                    "Vin_amp": quantity(1, "V"),
                    "signal_type": "1",
                },
                1,
            ),
            (
                "summing",
                {
                    "signal_count": 2,
                    "Vin1_amp": quantity(0.5, "V"),
                    "Ri1": quantity(10, "kOhm"),
                    "Vin2_amp": quantity(0.25, "V"),
                    "Ri2": quantity(20, "kOhm"),
                    "Rf": quantity(100, "kOhm"),
                    "Vcc_pos": quantity(12, "V"),
                    "Vcc_neg": quantity(-12, "V"),
                    "f": 50,
                    "RL": quantity(10, "kOhm"),
                },
                2,
            ),
        ]

        for kind, inputs, expected_plots in runs:
            response = self.client.post(
                "/api/simulate",
                json={"amplifier": kind, "inputs": inputs},
            )
            self.assertEqual(response.status_code, 200, response.get_json())
            record = response.get_json()
            self.assertEqual(len(record["image_urls"]), expected_plots)
            for url in record["image_urls"]:
                image_response = self.client.get(url)
                self.assertEqual(image_response.status_code, 200)
                self.assertTrue(image_response.data.startswith(b"\x89PNG"))
                image_response.close()

        history = self.client.get("/api/history").get_json()
        self.assertEqual(len(history), len(runs))
        with self.app.app_context():
            from flask import current_app

            connection = sqlite3.connect(current_app.config["DATABASE"])
            try:
                stored = connection.execute(
                    "SELECT outputs_json FROM simulation_history "
                    "WHERE amplifier = 'Inverting amplifier'"
                ).fetchone()
            finally:
                connection.close()
        outputs = json.loads(stored[0])
        self.assertEqual(len(outputs["output_voltage_v"]), 1000)
        self.assertIn("load_current_a", outputs)
        full_record = self.client.get(
            f"/api/history/{history[0]['id']}"
        ).get_json()
        self.assertIn("output_voltage_v", full_record["outputs"])

    def test_rejects_zero_resistance_without_creating_a_session(self):
        response = self.client.post(
            "/api/simulate",
            json={
                "amplifier": "inverting",
                "inputs": {
                    "R": quantity(0, "ohm"),
                    "Rf": quantity(100, "kOhm"),
                    "Vin_amp": quantity(0.5, "V"),
                    "Vcc_pos": quantity(12, "V"),
                    "Vcc_neg": quantity(-12, "V"),
                    "RL": quantity(10, "kOhm"),
                },
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("greater than zero", response.get_json()["error"])
        self.assertEqual(self.client.get("/api/history").get_json(), [])

    def test_integrator_and_differentiator_follow_selected_waveform(self):
        waveforms = {"1": "Sine wave", "2": "Square wave", "3": "Triangle wave"}
        component_inputs = {
            "R": quantity(10, "kOhm"),
            "C": quantity(100, "nF"),
            "Vin_amp": quantity(1, "V"),
        }

        for kind in ("integrator", "differentiator"):
            outputs_by_waveform = {}
            for signal_type, signal_name in waveforms.items():
                response = self.client.post(
                    "/api/simulate",
                    json={
                        "amplifier": kind,
                        "inputs": {**component_inputs, "signal_type": signal_type},
                    },
                )
                self.assertEqual(response.status_code, 200, response.get_json())
                record = response.get_json()
                self.assertEqual(record["outputs"]["signal_type"], signal_name)

                full_record = self.client.get(
                    f"/api/history/{record['id']}"
                ).get_json()
                outputs_by_waveform[signal_name] = full_record["outputs"]

            input_waveforms = [
                outputs["input_voltage_v"]
                for outputs in outputs_by_waveform.values()
            ]
            self.assertEqual(len({tuple(waveform) for waveform in input_waveforms}), 3)
            output_waveforms = [
                outputs["output_voltage_v"]
                for outputs in outputs_by_waveform.values()
            ]
            self.assertEqual(len({tuple(waveform) for waveform in output_waveforms}), 3)
            self.assertTrue(
                all(len(waveform) == 1000 for waveform in input_waveforms)
            )

    def test_simulation_opens_matplotlib_window_when_enabled(self):
        self.app.config["OPEN_MATPLOTLIB_WINDOW"] = True
        inputs = {
            "R": quantity(10, "kOhm"),
            "Rf": quantity(100, "kOhm"),
            "Vin_amp": quantity(0.5, "V"),
            "Vcc_pos": quantity(12, "V"),
            "Vcc_neg": quantity(-12, "V"),
            "RL": quantity(10, "kOhm"),
        }

        with patch("web_app.subprocess.Popen") as popen:
            response = self.client.post(
                "/api/simulate",
                json={"amplifier": "inverting", "inputs": inputs},
            )

        self.assertEqual(response.status_code, 200, response.get_json())
        self.assertIsNone(response.get_json()["plot_window_error"])
        self.assertEqual(popen.call_count, 1)
        command = popen.call_args.args[0]
        self.assertEqual(command[1], str(Path(__file__).with_name("matplotlib_window.py")))
        self.assertEqual(command[2], "inverting")


if __name__ == "__main__":
    unittest.main()
