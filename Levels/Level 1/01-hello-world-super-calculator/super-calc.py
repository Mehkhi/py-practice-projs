OPS = ("add", "sub", "mul", "div", "m+", "m-", "mr", "quit")

ALIASES = {
    "1": "add", "add": "add", "+": "add",
    "2": "sub", "sub": "sub", "-": "sub",
    "3": "mul", "mul": "mul", "*": "mul",
    "4": "div", "div": "div", "/": "div",
    "m+": "m+", "m-": "m-", "mr": "mr", "recall": "mr",
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
    memory = 0.0
    last_result = None
    # Show menu everytime and normalize input to a canonical command
    while True:
        (print)("\nChoose operation:")
        print(" 1) Add(+)")
        print(" 2) Subtract(-)")
        print(" 3) Multiply(*)")
        print(" 4) Divide(/)")
        print(" m+) Add last result to memory")
        print(" m-) Subtract last result from memory")
        print(" mr) Recall memory")
        print(" q) Quit")
        raw= input("Your choice: ")
        cmd = normalize_command(raw)
        if cmd is None:
            print("Invalid choice. Try 1, 2, 3, 4, '+', '-', '*', '/', 'm+', 'm-', 'mr', 'q', 'x', 'quit', 'exit'")
            continue
        if cmd == "quit":
            print("Goodbye!")
            break
        # Handle memory commands without asking for new numbers
        if cmd in ("m+", "m-", "mr"):
            if cmd == "m+":
                if last_result is None:
                    print("No last result to add. Perform a calculation first.")
                else:
                    memory += last_result
                    print(f"Memory updated: memory = {memory}")
            elif cmd == "m-":
                if last_result is None:
                    print("No last result to subtract. Perform a calculation first.")
                else:
                    memory -= last_result
                    print(f"Memory updated: memory = {memory}")
            else:
                print(f"Memory recall: {memory}")
            continue
        a = read_number("First number: ")
        b = read_number("Second number: ")
        print(f"You chose {cmd} with {a} and {b}")
        if cmd == "add":
            last_result = a + b
            print(f"Result: {a} + {b} = {last_result}")
        elif cmd == "sub":
            last_result = a - b
            print(f"Result: {a} - {b} = {last_result}")
        elif cmd == "mul":
            last_result = a * b
            print(f"Result: {a} * {b} = {last_result}")
        elif cmd == "div":
            if b != 0:
                last_result = a / b
                print(f"Result: {a} / {b} = {last_result}")
            else:
                last_result = None
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
