def run(inputs=None, output_prefix=None):
    import numpy as np
    import matplotlib.pyplot as plt

    # --- Integrator Function ---
    def integrator(vin, R, C, dt):
        vout = np.zeros_like(vin)
        for i in range(1, len(vin)):
            vout[i] = vout[i-1] - (vin[i] / (R * C)) * dt
        return vout

    # --- User Inputs ---
    if inputs is None:
        print("=== Integrator Circuit Simulator ===")
        R = float(input("Enter resistance R (Ohm): "))
        C = float(input("Enter capacitance C (Farad): "))
        Vin_amp = float(input("Enter input amplitude (V): "))

        print("\nChoose input signal type:")
        print("1. Sine wave")
        print("2. Square wave")
        print("3. Triangle wave")
        signal_type = input("Enter choice (1/2/3): ")
    else:
        R = inputs["R"]
        C = inputs["C"]
        Vin_amp = inputs["Vin_amp"]
        signal_type = inputs["signal_type"]

    # --- Time setup ---
    fs = 1000
    f = 5
    t = np.linspace(0, 1, fs, endpoint=False)
    dt = t[1] - t[0]

    # --- Generate selected waveform ---
    if signal_type == '1':
        vin = Vin_amp * np.sin(2 * np.pi * f * t)
        signal_name = "Sine wave"
    elif signal_type == '2':
        vin = Vin_amp * np.sign(np.sin(2 * np.pi * f * t))
        signal_name = "Square wave"
    elif signal_type == '3':
        vin = Vin_amp * (2 * np.abs(2 * (t * f % 1) - 1) - 1)  # Triangle wave
        signal_name = "Triangle wave"
    else:
        print("Invalid choice! Defaulting to Sine wave.")
        vin = Vin_amp * np.sin(2 * np.pi * f * t)
        signal_name = "Sine wave"

    # --- Get integrator output ---
    vout = integrator(vin, R, C, dt)

    # --- Plot results ---
    plt.figure(figsize=(10, 6))
    plt.plot(t, vin, label=f"Input ({signal_name})", color='blue')
    plt.plot(t, vout, label="Output (Integrated Signal)", color='red')
    plt.title(f"Integrator Output for {signal_name}")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Voltage (V)")
    plt.grid(True)
    plt.legend()
    if output_prefix:
        plt.savefig(f"{output_prefix}-output.png", dpi=150, bbox_inches="tight")
        plt.close()
    else:
        plt.show()
    return {
        "signal_type": signal_name,
        "output_peak_v": float(np.max(np.abs(vout))),
        "time_s": t.tolist(),
        "input_voltage_v": vin.tolist(),
        "output_voltage_v": vout.tolist(),
    }

if __name__ == "__main__":
    run()
