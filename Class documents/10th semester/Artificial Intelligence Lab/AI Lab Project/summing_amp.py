def run(inputs=None, output_prefix=None):
    import numpy as np
    import matplotlib.pyplot as plt

    # ------------------- USER INPUT -------------------
    if inputs is None:
        n = int(input("Enter number of input signals: "))

        Vi_amps = []
        Ri = []

        for i in range(n):
            amp = float(input(f"Enter amplitude of Vin{i+1} (V): "))
            resistance = float(input(f"Enter resistor Ri{i+1} (Ohm): "))
            Vi_amps.append(amp)
            Ri.append(resistance)

        Rf = float(input("Enter feedback resistor Rf (Ohm): "))
        Vcc_pos = float(input("Enter +Vcc (V): "))
        Vcc_neg = float(input("Enter -Vee (V): "))
        f = float(input("Enter frequency of input signals (Hz): "))
        RL = float(input("Enter load resistor RL (Ohm): "))
    else:
        n = len(inputs["Vi_amps"])
        Vi_amps = inputs["Vi_amps"]
        Ri = inputs["Ri"]
        Rf = inputs["Rf"]
        Vcc_pos = inputs["Vcc_pos"]
        Vcc_neg = inputs["Vcc_neg"]
        f = inputs["f"]
        RL = inputs["RL"]

    # ------------------- SIGNAL GENERATION -------------------
    t = np.linspace(0, 2 / f, 1000)

    # Generate all input sine waves
    Vin = []
    for amp in Vi_amps:
        Vin.append(amp * np.sin(2 * np.pi * f * t))

    # Ideal output of inverting summing amplifier
    Vo_ideal = np.zeros_like(t)
    for i in range(n):
        Vo_ideal += (Vin[i] / Ri[i])
    Vo_ideal = -Rf * Vo_ideal

    # Peak value (will be shown in text box)
    Vo_peak = -Rf * sum(Vi_amps[i] / Ri[i] for i in range(n))

    # Clipping (saturation)
    Vo = np.clip(Vo_ideal, Vcc_neg, Vcc_pos)

    # Load current
    IL = Vo / RL

    # ------------------- PLOTTING -------------------
    plt.figure(figsize=(12, 7))

    # Plot all input waveforms
    for i in range(n):
        plt.plot(t, Vin[i], label=f"Vin{i+1}")

    # Plot outputs
    plt.plot(t, Vo_ideal, '--', label="Ideal Output", alpha=0.6)
    plt.plot(t, Vo, linewidth=2, label="Actual Output (Clipped)")

    plt.axhline(Vcc_pos, color='r', linestyle=':', label=f"+{Vcc_pos}V Rail")
    plt.axhline(Vcc_neg, color='r', linestyle=':', label=f"{Vcc_neg}V Rail")

    # Add Vout_peak to legend as a dummy line
    plt.plot([], [], ' ', label=f"Vout_peak = {Vo_peak:.3f} V")

    plt.title("Inverting Summing Amplifier Output")
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (V)")
    plt.legend(loc="upper left")
    plt.grid(True)

    plt.tight_layout()
    if output_prefix:
        plt.savefig(f"{output_prefix}-voltage.png", dpi=150, bbox_inches="tight")
        plt.close()
    else:
        plt.show()

    # ------------------- Load Current Plot -------------------
    plt.figure(figsize=(10, 4))
    plt.plot(t, IL, label="Load Current IL = Vo / RL", color="green", linewidth=2)
    plt.axhline(0, color='black', linewidth=1)
    plt.title("Load Current Waveform")
    plt.xlabel("Time (s)")
    plt.ylabel("Current (A)")
    plt.legend()
    plt.grid(True)
    if output_prefix:
        plt.savefig(f"{output_prefix}-current.png", dpi=150, bbox_inches="tight")
        plt.close()
    else:
        plt.show()

    # ------------------- PRINT RESULTS -------------------
    if inputs is None:
        print("\n=== RESULTS ===")
        print(f"Ideal Output Peak Voltage = {Vo_peak:.4f} V")
        if np.any(Vo_ideal > Vcc_pos) or np.any(Vo_ideal < Vcc_neg):
            print("⚠️ Output SATURATED (Clipped)")
        else:
            print("✅ Output within limits")
    return {
        "output_peak_voltage_v": float(Vo_peak),
        "actual_output_peak_v": float(np.max(np.abs(Vo))),
        "load_current_peak_a": float(np.max(np.abs(IL))),
        "clipped": bool(
            np.any(Vo_ideal > Vcc_pos) or np.any(Vo_ideal < Vcc_neg)
        ),
        "time_s": t.tolist(),
        "input_voltage_v": [signal.tolist() for signal in Vin],
        "ideal_output_voltage_v": Vo_ideal.tolist(),
        "output_voltage_v": Vo.tolist(),
        "load_current_a": IL.tolist(),
    }

if __name__ == "__main__":
    run()
