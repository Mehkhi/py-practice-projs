OPS = ("add", "sub", "mul", "div", "quit")

ALIASES = {
    "1": "add", "add": "add", "+": "add",
    "2": "sub", "sub": "sub", "-": "sub",
    "3": "mul", "mul": "mul", "*": "mul",
    "4": "div", "div": "div", "/": "div",
    "q": "quit", "quit": "quit", "x": "quit", "exit": "quit",
}

def normalize_command(raw): # Accept any text, normalize, and map to an operation
    if raw is None:
        return None
    token = raw.strip().lower()
    if not token: # empty after trimming spaces
        return None
    return ALIASES.get(token)

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
if b != 0:
    print(f"Quotient: {a / b}")
else:
    print("Quotient: undefined (division by zero)")
