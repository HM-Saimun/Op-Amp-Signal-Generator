def run():
    import numpy as np
    import matplotlib.pyplot as plt

    # ------------------- USER INPUT -------------------
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
    plt.show()

    # ------------------- PRINT RESULTS -------------------
    print("\n=== RESULTS ===")
    print(f"Ideal Output Peak Voltage = {Vo_peak:.4f} V")
    if np.any(Vo_ideal > Vcc_pos) or np.any(Vo_ideal < Vcc_neg):
        print("⚠️ Output SATURATED (Clipped)")
    else:
        print("✅ Output within limits")

if __name__ == "__main__":
    run()
