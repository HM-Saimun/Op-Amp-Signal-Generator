def run():
    import numpy as np
    import matplotlib.pyplot as plt

    # --- Integrator Function ---
    def integrator(vin, R, C, dt):
        vout = np.zeros_like(vin)
        for i in range(1, len(vin)):
            vout[i] = vout[i-1] - (vin[i] / (R * C)) * dt
        return vout

    # --- User Inputs ---
    print("=== Integrator Circuit Simulator ===")
    R = float(input("Enter resistance R (Ohm): "))
    C = float(input("Enter capacitance C (Farad): "))
    Vin_amp = float(input("Enter input amplitude (V): "))

    print("\nChoose input signal type:")
    print("1. Sine wave")
    print("2. Square wave")
    print("3. Triangle wave")
    signal_type = input("Enter choice (1/2/3): ")

    # --- Time setup ---
    fs = 500  # Sampling frequency (Hz)
    t = np.linspace(0, 3, fs)  # 1 second duration
    f = 500  # Input frequency (Hz)
    dt = 1 / fs

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
    plt.show()

if __name__ == "__main__":
    run()
