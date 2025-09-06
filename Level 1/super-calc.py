def read_number(prompt):
    while True:
        raw_input = input(prompt)
        try:
            return float(raw_input)
        except ValueError:
            print("Please enter a valid number.")


a = read_number("First number: ")
b = read_number("Second number: ")

print(f"You chose {a} and {b}")

print(f"Sum: {a + b}")
print(f"Difference: {a - b}")
print(f"Product: {a * b}")
print(f"Quotient: {a / b}")
if b != 0:
    print(f"Quotient: {a / b}")
else:
    print("Quotient: undefined (division by zero)")
