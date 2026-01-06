def run():
    import numpy as np
    import matplotlib.pyplot as plt

    # --- User Inputs ---
    R1 = float(input("Enter the value of R1 (Ohm): "))
    R2 = float(input("Enter the value of R2 (Ohm): "))
    Vcc_pos = float(input("Enter the positive supply voltage (+Vcc in V): "))
    Vcc_neg = float(input("Enter the negative supply voltage (-Vee in V): "))
    Vi_amp = float(input("Enter the amplitude of input voltage Vi (V): "))
    RL = float(input("Enter the load resistor value (Ohm): "))

    # --- Amplifier Gain (Non-Inverting Amplifier) ---
    Av = 1 + (R2 / R1)

    # --- Time and Input Signal ---
    t = np.linspace(0, 2 * np.pi, 1000)
    Vi = Vi_amp * np.sin(t)

    # --- Ideal Output (before clipping) ---
    Vo_ideal = Av * Vi

    # --- Apply supply voltage limits (clipping) ---
    Vo = np.clip(Vo_ideal, Vcc_neg, Vcc_pos)

    # --- Load Current ---
    IL = Vo / RL  # Ohm's Law: I = V / R

    # --- Plot Input and Output Voltages ---
    plt.figure(figsize=(10, 6))
    plt.plot(t, Vi, label=f'Input Voltage Vi ({Vi_amp}sinωt)', linewidth=2)
    plt.plot(t, Vo_ideal, '--', label='Ideal Output (No Clipping)', alpha=0.7)
    plt.plot(t, Vo, label='Actual Output (With Clipping)', linewidth=2)
    plt.axhline(Vcc_pos, color='r', linestyle=':', label=f'+{Vcc_pos}V Rail')
    plt.axhline(Vcc_neg, color='r', linestyle=':', label=f'{Vcc_neg}V Rail')
    plt.title('Non-Inverting Amplifier Output with Clipping')
    plt.xlabel('Time (rad)')
    plt.ylabel('Voltage (V)')
    plt.legend()
    plt.grid(True)
    plt.show()

    # --- Plot Load Current ---
    plt.figure(figsize=(10, 4))
    plt.plot(t, IL, label='Load Current iL = Vo / RL', color='green', linewidth=2)
    plt.axhline(0, color='black', linewidth=1)
    plt.title('Load Current Waveform')
    plt.xlabel('Time (rad)')
    plt.ylabel('Current (A)')
    plt.legend()
    plt.grid(True)
    plt.show()

    # --- Display Information ---
    print(f"\nAmplifier Gain (Av) = {Av:.2f}")
    print(f"Input Amplitude = {Vi_amp} V")
    print(f"Ideal Output Peak = {abs(Av * Vi_amp):.2f} V")
    print(f"Supply Rails: +{Vcc_pos} V / {Vcc_neg} V")
    if np.any(Vo_ideal > Vcc_pos) or np.any(Vo_ideal < Vcc_neg):
        print("⚠️ Output is CLIPPED (Saturation occurred).")
    else:
        print("✅ Output is within saturation limits.")

if __name__ == "__main__":
    run()
