from sqlmodel import SQLModel, Field, Session, create_engine, select, inspect, text
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
import os
import sys
import re
import logging
import argparse
from wordfinder import WordFilter

# Configure logging
logging.basicConfig(level=logging.INFO)

# Database setup
SQLITE_FILE_NAME = os.path.join(os.path.dirname(__file__), 'data', "words.db")
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"
engine = create_engine(SQLITE_URL, echo=False)
NAMES = os.path.join(os.path.dirname(__file__), 'dict', 'names.txt')

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

    # Load names from names.txt into a set
    with open(NAMES, 'r', encoding='utf-8') as file:
        names_set = {line.strip().upper() for line in file}

    with Session(engine) as session:
        if table_name in inspect(engine).get_table_names():
            session.exec(text(f"DELETE FROM {table_name}"))
            session.commit()

        valid_word_pattern = re.compile(r'^[a-zA-Z]+$')
        words_to_add = {}

        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                word = line.strip().upper()
                if valid_word_pattern.match(word) and word not in words_to_add and word not in names_set:
                    words_to_add[word] = DynamicWord(word=word)  # Use DynamicWord

        session.add_all(words_to_add.values())  # Add the DynamicWord objects
        session.commit()

    print(f"Database table '{table_name}' has been filled with words from '{filename}', excluding names from 'names.txt'.")

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
    if length == 0:
        print(f"Loading all words for the language '{language}'.")
    else:
        print(f"Loading words of length {length} for the language '{language}'.")
    DynamicWord = set_word_model_table_name(language)  # Set the table name for the Word model
    with Session(engine) as session:
        words = session.exec(select(DynamicWord.word).where(DynamicWord.__tablename__ == language)).all()
        return [word for word in words if len(word) == length]

def usage():
    usage_text = """
    Usage: python src/wordfinder/cli.py [OPTIONS]

    Options:
      -f, --filename <filename>    Specify the filename to load words from a text file to the database.
      -lang, --language <language> Specify the language of the words (e.g., EN, NL).
      -l, --length <number>        Filter words by the specified length. Default value is 5. Set the value 0, to disable length filter.
      -list --list-languages       List available languages.
      -h, --help                   Display this help message.

    Examples:
      To start the CLI with the default Dutch words and filter words of a length of 5:
        python src/wordfinder/cli.py

      To start the CLI with English words and only have words with a length of 10:
        python src/wordfinder/cli.py -lang EN -l 10

      To list available languages:
        python src/wordfinder/cli.py -list
    """
    print(usage_text)

def help():
    """Display the available commands and their descriptions."""
    commands = {
        "include <substring>": WordFilter.include_letters.__doc__,
        "exclude <letters>": WordFilter.exclude_letters.__doc__,
        "length <number>": WordFilter.by_length.__doc__,
        "pattern <pattern>": WordFilter.by_pattern.__doc__,
        "list": "Display the current list of words.",
        "reset": "Reset the words to the original list from the file.",
        "exit": "Exit the program."
    }

    help_text = "Available commands:\n"
    for command, description in commands.items():
        if description is not None:
            # Split the description into lines to handle multi-line docstrings
            description_lines = description.strip().splitlines()

            help_text += f"- {command}:\n"  # Start with the command
            for line in description_lines:
                help_text += f"  {line.strip()}\n"  # Indent each line of the description
        else:
            help_text += f"- {command}: No description available.\n"

    print(help_text)


def main():
    parser = argparse.ArgumentParser(description="Word Finder CLI")
    parser.add_argument('-f', '--filename', nargs='?', default='', type=str,  help="The filename that contains the words")
    parser.add_argument('-lang', '--language', nargs='?', default='', type=lambda s: s.lower(), help="Language of the wordlist (e.g., en, es, nl)") # We dont set a default here, because we need to handle filename in conjunction with language
    parser.add_argument('-l', '--length', nargs='?', default=5, type=int, help="The length of the words to filter")
    parser.add_argument('-list', '--list-languages', action='store_true', help="List available languages")
    args = parser.parse_args()

    if not os.path.exists(SQLITE_FILE_NAME) and not args.filename:
        print(f"Error: Database {SQLITE_FILE_NAME} file does not exist.")
        print("Database can be populated by providing command arguments --filename --language")
        usage()
        sys.exit(1)
    elif args.filename:
        if not args.language:
            print("Error: When providing a filename, you must also provide the language abbreviation. e.g. --language [en | nl | es]")
            usage()
            sys.exit(1)
        fill_database(args.filename, args.language)

    if not args.language:
        args.language = "nl" # Default language

    if args.length < 0:
        print("Error: Length must be a positive number.")
        usage()
        sys.exit(1)

    if args.list_languages:
        inspector = inspect(engine)
        print("Available languages:", inspector.get_table_names())
        usage_text = """
        To start the CLI with the default Dutch words with the default words of a length of 5:
          python src/wordfinder/cli.py -lang nl
        """
        print(usage_text)
        sys.exit(0)

    check_database_and_table(args.language)

    words = load_words(args.language, args.length)
    word_filter = WordFilter()

    try:
        while True:
            print(f"Total words: {word_filter.word_count}")
            print(f"Excluded letters: {''.join(sorted(word_filter.excluded_letters))}")
            print(f"Included letters: {''.join(sorted(word_filter.included_letters))}")
            print(f"Pattern e.g. d??my: {word_filter.pattern}")
            print("Hint: Type 'help' to see the list of available commands.")
            command = input("Enter command: ").strip().lower()

            if command.startswith("exclude "):
                _, letters = command.split(" ", 1)
                words = word_filter.exclude_letters(words, letters.upper())

            elif command.startswith("include "):
                _, substring = command.split(" ", 1)
                words = word_filter.include_letters(words, substring.upper())

            elif command.startswith("length "):
                _, length = command.split(" ", 1)
                if length.isdigit():
                    words = word_filter.by_length(words, int(length))
                else:
                    print("Error: Length must be a number.")

            elif command.startswith("pattern "):
                _, pattern = command.split(" ", 1)
                words = word_filter.by_pattern(words, pattern.upper())

            elif command == "list":
                print(f"Words: {words}")

            elif command == "reset":
                words = load_words(args.language, args.length)
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