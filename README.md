# py-wordfinder

Python version of Wordfinder

# Table of Contents

- [py-wordfinder](#py-wordfinder)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Command Line Interface (CLI)](#command-line-interface-cli)
      - [Command Line Arguments](#command-line-arguments)
      - [Commands](#commands)
  - [FastAPI](#fastapi)
    - [Endpoints](#endpoints)
    - [Example](#example)
  - [Frontend Installation and Setup](#frontend-installation-and-setup)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/DeChinees/py-wordfinder.git
    cd py-wordfinder
    ```

2. Install Poetry if you haven't already:
    ```sh
    curl -sSL https://install.python-poetry.org | python3 -
    ```

3. Install the required dependencies using Poetry:
    ```sh
    poetry install
    ```

4. Activate the virtual environment:
    ```sh
    poetry shell
    ```

## Usage

### Command Line Interface (CLI)

The CLI allows you to add new list, filter, and manipulate word lists.
The default wordlist is Dutch (NL) and can be found in the `data` directory. The data is stored in a SQLite database.

To start the CLI with the default Dutch words and filter words of a length of 5:
```sh
python src/wordfinder/cli.py

## or ## 

poetry run python src/wordfinder/cli.py
```

To start the CLI with English words and only have words with a length of 10:
```sh
python src/wordfinder/cli.py -lang EN -l 10

## or ## 

poetry run python src/wordfinder/cli.py -lang EN -l 10 
```
To list available languages:
```sh
python src/wordfinder/cli.py -list

## or ## 

poetry run python src/wordfinder/cli.py -list
```
#### Command Line Arguments

- \`-f, --filename <filename>\`: Specify the filename to load the word list from a text file to the database.
- \`-lang, --language <language>\`: Specify the language of the word list (e.g., en, es, nl).
- \`-l, --length <number>\`: Filter words by the specified length. Default value is 5. Set the value 0, to disable length filter.
- \`-list, --list-languages\`: List available languages.
- \`-h, --help\`: Display the help message.


### Commands

- `exclude <letters>`: Exclude words containing any of the specified letters.
- `include <substring>`: Filter words containing the specified substring.
- `length <number>`: Filter words by the specified length.
- `pattern <pattern>`: Filter words matching the specified pattern.
- `list`: Display the current list of words.
- `reset`: Reset the words to the original list from the file.
- `help`: Display the available commands and their descriptions.
- `exit`: Exit the program.


# FastAPI

The FastAPI application provides endpoints to filter and manipulate word lists.  

## Endpoints
GET /: Root endpoint.
GET /exclude_letters: Exclude words containing any of the specified letters.
GET /filter_by_length: Filter words by the specified length.
GET /contains_letters: Filter words containing the specified substring.
GET /filter_by_pattern: Filter words matching the specified pattern.

### Example
To start the FastAPI server in development mode:
```sh
poetry run fastapi dev api.py
```
You can then access the API documentation at http://127.0.0.1:8000/docs. 

## Frontend Installation and Setup

To set up and start the frontend of the project, follow these steps:

1. Navigate to the `frontend` directory:
    ```sh
    cd src/frontend
    ```

2. Install the required npm dependencies:
    ```sh
    npm install
    ```

3. Start the development server:
    ```sh
    npm start
    ```

This will run the app in development mode. Open [http://localhost:3000](http://localhost:3000) to view it in your browser. The page will reload when you make changes, and you may also see any lint errors in the console.
