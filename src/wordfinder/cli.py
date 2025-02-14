import logging
import re
from wordfinder import exclude_letters, filter_by_length, contains_letters, filter_by_pattern

# Configure logging
logging.basicConfig(level=logging.INFO)


def load_words(filename: str):
    """Load words from a file into a list, removing words with numbers and special characters.
    Converts all words to uppercase."""
    valid_word_pattern = re.compile(r'^[a-zA-Z]+$')  # Only letters allowed (no digits or special characters)

    with open(filename, 'r', encoding='utf-8') as file:
        return [line.strip().upper() for line in file if valid_word_pattern.match(line.strip())]


def help():
    """Display the available commands and their descriptions."""
    commands = {
        "exclude <letters>": exclude_letters.__doc__,
        "length <number>": filter_by_length.__doc__,
        "contains <substring>": contains_letters.__doc__,
        "pattern <pattern>": filter_by_pattern.__doc__,
        "list": "Display the current list of words.",
        "reset": "Reset the words to the original list from the file.",
        "exit": "Exit the program."
    }

    help_text = "Available commands:\n"
    for command, description in commands.items():
        help_text += f"- {command}: {description}\n"

    print(help_text)


def main():
    # Read the words from the file and filter out words that are not 5 characters long
    words = load_words('en-wordlist.txt')
    words = filter_by_length(words, 5)

    try:
        while True:
            command = input("Enter command: ").strip().lower()

            if command.startswith("exclude "):
                _, letters = command.split(" ", 1)
                words = exclude_letters(words, letters.upper())
                print(f"Updated words: {words}")

            elif command.startswith("length "):
                _, length = command.split(" ", 1)
                if length.isdigit():
                    words = filter_by_length(words, int(length))
                    print(f"Updated words: {words}")
                else:
                    print("Error: Length must be a number.")

            elif command.startswith("contains "):
                _, substring = command.split(" ", 1)
                words = contains_letters(words, substring.upper())
                print(f"Updated words: {words}")

            elif command.startswith("pattern "):
                _, pattern = command.split(" ", 1)
                words = filter_by_pattern(words, pattern.upper())
                print(f"Updated words: {words}")

            elif command == "list":
                print(f"Words: {words}")

            elif command == "reset":
                words = load_words('wordlist.txt')
                print(f"Words reset to original list.")

            elif command == "help":
                help()

            elif command == "exit":
                print("Exiting program.")
                break

            else:
                print("Unknown command. Type 'help' to see the list of available commands.")

    except KeyboardInterrupt:
        logging.info("Application stopped by user.")


if __name__ == "__main__":
    main()