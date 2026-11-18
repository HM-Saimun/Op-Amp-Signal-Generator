# Op-Amp Signal Studio

Run the browser-based simulator from this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
npm run dev
```

Open <http://127.0.0.1:5500>. Select an amplifier, enter its component and voltage values, and run a simulation. The original terminal menu is still available with `.\.venv\Scripts\python.exe main_menu.py`.

Each run is recorded in `simulation_history.db`, including its inputs and computed waveform samples. Plots are saved as identifiable PNG files in `output_signals/` and linked from the history table.

The web app also opens the simulator's Matplotlib window automatically for each run. Set `OPEN_MATPLOTLIB_WINDOW` to `False` in the Flask app configuration to disable it.
