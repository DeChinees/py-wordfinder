from sqlmodel import SQLModel, Field, Session, create_engine, select, inspect, text
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
import os, sys, re, logging, argparse
from wordfinder import exclude_letters, filter_by_length, contains_letters, filter_by_pattern

# Configure logging
logging.basicConfig(level=logging.INFO)

# Database setup
SQLITE_FILE_NAME = "words.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"
engine = create_engine(SQLITE_URL, echo=False)


class BaseWordModel(SQLModel, table=True):
    """Base database table for storing words."""
    id: int = Field(default=None, primary_key=True)
    word: str = Field(index=True)


def set_word_model_table_name(table_name: str):
    """Create a dynamic Word model class with a specified table name."""
    Base = declarative_base(metadata=SQLModel.metadata)

    class DynamicWordModel(Base):
        __tablename__ = table_name
        __table_args__ = {'extend_existing': True}
        id = Column(Integer, primary_key=True)
        word = Column(String, index=True)

    return DynamicWordModel


def fill_database(filename: str, table_name: str):
    """Fill database, dynamically creating/repopulating table."""
    DynamicWord = set_word_model_table_name(table_name)  # Create a dynamic Word model class
    DynamicWord.__table__.create(engine, checkfirst=True)  # Create the table if it doesn't exist

    with Session(engine) as session:
        if table_name in inspect(engine).get_table_names():
            session.exec(text(f"DELETE FROM {table_name}"))
            session.commit()

        valid_word_pattern = re.compile(r'^[a-zA-Z]+$')
        words_to_add = {}

        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                word = line.strip().upper()
                if valid_word_pattern.match(word) and word not in words_to_add:
                    words_to_add[word] = DynamicWord(word=word)  # Use DynamicWord

        session.add_all(words_to_add.values())  # Add the DynamicWord objects
        session.commit()

    print(f"Database table '{table_name}' has been filled with words from '{filename}'.")


def check_database_and_table(table_name: str):
    """Check if the database file and table exist, and whether the table contains data."""
    DynamicWord = set_word_model_table_name(table_name)  # Set the table name for the Word model
    try:
        # Check if the table exists
        inspector = inspect(engine)  # Use SQLAlchemy's inspector
        if table_name not in inspector.get_table_names():
            raise ValueError(f"Table '{table_name}' does not exist.")

        # Check if the table has data
        with Session(engine) as session:
            result = session.exec(select(DynamicWord).limit(1)).first()  # Check for at least one record
            if not result:
                raise ValueError(f"Table '{table_name}' exists but contains no data.")

    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        print("Database and/or table can be populated by providing command arguments --filename --language")
        sys.exit(1)


def load_words(language: str, length: int):
    """Load words from the database table named `language` and return them as a list."""
    DynamicWord = set_word_model_table_name(language)  # Set the table name for the Word model
    with Session(engine) as session:
        words = session.exec(select(DynamicWord.word).where(DynamicWord.__tablename__ == language)).all()
        return [word for word in words if len(word) == length]


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

    if not os.path.exists(SQLITE_FILE_NAME) and not args.filename:
        print(f"Error: Database {SQLITE_FILE_NAME} file does not exist.")
        print(f"Database can be populated by providing command arguments --filename --language")
        sys.exit(1)
    elif args.filename:
        fill_database(args.filename, args.language)

    check_database_and_table(args.language)

    # Read the words from the file and filter out words that are not 5 characters long
    words = load_words(args.language, args.length)

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