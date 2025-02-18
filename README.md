# py-wordfinder

Python version of Wordfinder

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

The CLI allows you to load, filter, and manipulate word lists.

#### Commands

- `exclude <letters>`: Exclude words containing any of the specified letters.
- `length <number>`: Filter words by the specified length.
- `contains <substring>`: Filter words containing the specified substring.
- `pattern <pattern>`: Filter words matching the specified pattern.
- `save <filename>`: Save the current list of words to the specified file.
- `list`: Display the current list of words.
- `reset`: Reset the words to the original list from the file.
- `help`: Display the available commands and their descriptions.
- `exit`: Exit the program.

#### Example

To start the CLI with the default word list and filter words of length 5:
```sh
python src/wordfinder/cli.py
```

# FastAPI

The FastAPI application provides endpoints to filter and manipulate word lists.  

## Endpoints
GET /: Root endpoint.
GET /exclude_letters: Exclude words containing any of the specified letters.
GET /filter_by_length: Filter words by the specified length.
GET /contains_letters: Filter words containing the specified substring.
GET /filter_by_pattern: Filter words matching the specified pattern.

###Example
To start the FastAPI server in development mode:
```sh
poetry run fastapi dev api.py
```
You can then access the API documentation at http://127.0.0.1:8000/docs. 