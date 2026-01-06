def run():
    import numpy as np
    import matplotlib.pyplot as plt

    # --- User Inputs ---
    R = float(input("Enter the value of R (Ohm): "))
    Rf = float(input("Enter the value of Rf (Ohm): "))
    Vin_amp = float(input("Enter the amplitude of Vin (V): "))
    Vcc_pos = float(input("Enter the positive supply voltage (+Vcc in V): "))
    Vcc_neg = float(input("Enter the negative supply voltage (-Vee in V): "))
    RL = float(input("Enter the load resistor value (Ohm): "))

    
    Av = -Rf / R  # Gain for inverting amplifier
    t = np.linspace(0, 2 * np.pi, 1000)
    Vin = Vin_amp * np.sin(t)
    Vout_ideal = Av * Vin
    Vout = np.clip(Vout_ideal, Vcc_neg, Vcc_pos)
    IL = Vout / RL  
    
    
    # Ohm's law for load current

    # --- Plot Input and Output Voltages ---
    plt.figure(figsize=(10, 6))
    plt.plot(t, Vin, label='Input Voltage Vin', linewidth=2)
    plt.plot(t, Vout_ideal, '--', label='Ideal Output (No Clipping)', alpha=0.7)
    plt.plot(t, Vout, label='Actual Output (With Clipping)', linewidth=2)
    plt.axhline(Vcc_pos, color='r', linestyle=':', label=f'+{Vcc_pos}V Rail')
    plt.axhline(Vcc_neg, color='r', linestyle=':', label=f'{Vcc_neg}V Rail')
    plt.title('Inverting Amplifier Output with Clipping')
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
    print(f"Input Amplitude = {Vin_amp} V")
    print(f"Ideal Output Peak = {abs(Av * Vin_amp):.2f} V")
    print(f"Supply Rails: +{Vcc_pos} V / {Vcc_neg} V")
    if np.any(Vout_ideal > Vcc_pos) or np.any(Vout_ideal < Vcc_neg):
        print("⚠️ Output is CLIPPED (Saturation occurred).")
    else:
        print("✅ Output is within saturation limits.")
    print(f"Load Resistor (RL) = {RL} Ohm")
    print(f"Maximum Load Current = {np.max(np.abs(IL)):.2f} A")

if __name__ == "__main__":
    run()
