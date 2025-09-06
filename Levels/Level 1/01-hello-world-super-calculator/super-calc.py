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

def main():
    # Show menu everytime and normalize input to a canonical command
    while True:
        (print)("\nChoose operation:")
        print(" 1) Add(+)")
        print(" 2) Subtract(-)")
        print(" 3) Multiply(*)")
        print(" 4) Divide(/)")
        print(" q) Quit")
        raw= input("Your choice: ")
        cmd = normalize_command(raw)
        if cmd is None:
            print("Invalid choice. Try 1, 2, 3, 4, '+', '-', '*', '/', 'q', 'x', 'quit', 'exit'")
            continue
        if cmd == "quit":
            print("Goodbye!")
            break
        a = read_number("First number: ")
        b = read_number("Second number: ")
        print(f"You chose {cmd} with {a} and {b}")
        if cmd == "add":
            print(f"Result: {a} + {b} = {a + b}")
        elif cmd == "sub":
            print(f"Result: {a} - {b} = {a - b}")
        elif cmd == "mul":
            print(f"Result: {a} * {b} = {a * b}")
        elif cmd == "div":
            if b != 0:
                print(f"Result: {a} / {b} = {a / b}")
            else:
                print("Result: undefined (division by zero)")

def read_number(prompt):
    while True:
        raw_input = input(prompt)
        try:
            return float(raw_input)
        except ValueError:
            print("Please enter a valid number.")


if __name__ == "__main__":
    main()
