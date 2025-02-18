from sqlmodel import SQLModel, Field, Session, create_engine, select, inspect
import argparse
import logging
import os, sys, re
from wordfinder import exclude_letters, filter_by_length, contains_letters, filter_by_pattern

# Configure logging
logging.basicConfig(level=logging.INFO)

# Database setup
SQLITE_FILE_NAME = "words.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"
engine = create_engine(SQLITE_URL, echo=True)

class Word(SQLModel, table=True):
    """Database table for storing words."""
    id: int = Field(default=None, primary_key=True)
    word: str = Field(index=True)

def fill_database(filename: str, table_name: str):
    """Read file and fill the database table with words and removing words with numbers and special characters.
    Converts all words to uppercase and removes duplicates.
    """
    # Dynamically set the table name
    Word.__tablename__ = table_name

    # Create database and tables
    SQLModel.metadata.create_all(engine)

    # Check if the table exists and drop it if it does
    with Session(engine) as session:
        if inspect(engine).has_table(table_name):
            session.exec(f"DROP TABLE {table_name}")
            session.commit()

    # Create the table again
    SQLModel.metadata.create_all(engine)

    # Load words from the file
    valid_word_pattern = re.compile(r'^[a-zA-Z]+$')
    with open(filename, 'r', encoding='utf-8') as file:
        words = [line.strip().upper() for line in file if valid_word_pattern.match(line.strip())]

    # Insert words into the table
    with Session(engine) as session:
        for word in set(words):
            db_word = Word(word=word)
            session.add(db_word)
        session.commit()

    print(f"Database table '{table_name}' has been filled with words from '{filename}'.")

def check_database_and_table(table_name: str):
    """Check if the database and table exist"""
    try:
        # Check if the database file exists
        if not os.path.exists(SQLITE_FILE_NAME):
            raise Exception("Database does not exist.")

        # Check if the table exists
        with Session(engine) as session:
            table_exists = engine.has_table(table_name)
            if not table_exists:
                raise Exception(f"Table {table_name} does not exist.")

            # Check if the table has some data
            result = session.exec(select(Word).where(Word.__tablename__ == table_name)).first()
            if not result:
                raise Exception(f"Table {table_name} does not exist or has no data.")
    except Exception as e:
        print(e)
        print("Database and/or table can be populated by providing command arguments --filename --language")
        sys.exit(1)

def load_words(language: str, length: int):
    """Load words from the database table named `language` and return them as a list."""
    with Session(engine) as session:
        words = session.exec(select(Word.word).where(Word.__tablename__ == language)).all()
        return [word for word in words if len(word) == length]

def help():
    """Display the available commands and their descriptions."""
    commands = {
        "exclude <letters>": exclude_letters.__doc__,
        "length <number>": filter_by_length.__doc__,
        "contains <substring>": contains_letters.__doc__,
        "pattern <pattern>": filter_by_pattern.__doc__,
        "save <filename>": write_words.__doc__,
        "list": "Display the current list of words.",
        "reset": "Reset the words to the original list from the file.",
        "exit": "Exit the program."
    }

    help_text = "Available commands:\n"
    for command, description in commands.items():
        # Split the description into lines to handle multi-line docstrings
        description_lines = description.strip().splitlines()

        help_text += f"- {command}:\n"  # Start with the command
        for line in description_lines:
            help_text += f"  {line.strip()}\n"  # Indent each line of the description

    print(help_text)

def main():
    parser = argparse.ArgumentParser(description="Word Finder CLI")
    parser.add_argument('-f', '--filename', nargs='?', default='', type=str,  help="The filename to load words from")
    parser.add_argument( '-l', '--length', nargs='?', default=5, type=int, help="The length of the words to filter")
    parser.add_argument('-L', '--language', nargs='?', default='nl', type=lambda s: s.lower(), help="Language of the wordlist")
    args = parser.parse_args()

    if args.filename:
        fill_database(args.filename, args.filename)

    check_database_and_table(args.language)

    # Read the words from the file and filter out words that are not 5 characters long
    words = load_words(args.filename, args.language, args.length)

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

            elif command.startswith("save "):
                _, filename = command.split(" ", 1)
                words = load_words(args.filename)
                write_words(words, filename)

            elif command == "list":
                print(f"Words: {words}")

            elif command == "reset":
                words = load_words(args.filename)
                print(f"Words reset to {args.filename} list.")

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