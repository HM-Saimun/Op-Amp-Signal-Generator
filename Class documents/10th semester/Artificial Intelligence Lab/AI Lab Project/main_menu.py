import inverting_amp
import non_inverting_amp
import integrator
import differentiator
import summing_amp

def show_menu():
    print("\n=== Artificial Intelligence Lab Project ===")
    print("1. Inverting Amplifier")
    print("2. Non-Inverting Amplifier")
    print("3. Integrator")
    print("4. Differentiator")
    print("5. Summing Amplifier")
    print("0. Exit")

while True:
    show_menu()
    choice = input("Select an option (0–5): ")

    if choice == "1":
        inverting_amp.run()

    elif choice == "2":
        non_inverting_amp.run()

    elif choice == "3":
        integrator.run()

    elif choice == "4":
        differentiator.run()

    elif choice == "5":
        summing_amp.run()

    elif choice == "0":
        print("Exiting project...")
        break

    else:
        print("Invalid selection. Please try again.")
