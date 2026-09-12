def get_positive_float(prompt: str) -> float:
    """Keep asking until the user provides a valid positive number."""
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
        except ValueError:
            print("  ⚠ Please enter a valid number (e.g. 68.5). Try again.\n")
            continue

        if value <= 0:
            print("  ⚠ Value must be a positive number greater than zero. Try again.\n")
            continue

        return value


def calculate_bmi(weight_kg: float, height_m: float) -> float:
    return weight_kg / (height_m ** 2)


def classify_bmi(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def main():
    print("=" * 45)
    print("           BMI CALCULATOR")
    print("=" * 45)

    while True:
        weight = get_positive_float("Enter your weight in kg: ")
        height = get_positive_float("Enter your height in meters (e.g. 1.75): ")

        bmi = calculate_bmi(weight, height)
        category = classify_bmi(bmi)

        print("\n" + "-" * 45)
        print(f"  Your BMI is: {bmi:.2f}")
        print(f"  Category   : {category}")
        print("-" * 45)

        again = input("\nCalculate another BMI? (y/n): ").strip().lower()
        print()
        if again != "y":
            print("Thanks for using the BMI Calculator. Stay healthy!")
            break


if __name__ == "__main__":
    main()
