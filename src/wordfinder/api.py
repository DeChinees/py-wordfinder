from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from sqlmodel import create_engine, Session, text
from uuid import uuid4
import os
import time

# Database setup
SQLITE_FILE_NAME = os.path.join(os.path.dirname(__file__), 'data', "words.db")
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"
engine = create_engine(SQLITE_URL, echo=False)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=str(uuid4()), max_age=600)

# In-memory session storage (expires in 10 min)
SESSION_STORE = {}

def get_session(request: Request):
    session_id = request.session.get("session_id")
    if not session_id:
        session_id = str(uuid4())
        request.session["session_id"] = session_id
        SESSION_STORE[session_id] = {"created": time.time(), "words": []}
    return session_id

@app.get("/")
async def read_root():
    return {"message": "Welcome to WordFinder!"}

@app.get("/search/")
async def search_words(
    request: Request,
    lang: str,
    length: int = None,
    exclude: str = "",
    include: str = "",
    pattern: str = ""
):
    """Search for words in the database based on filters.
        - lang: Language to search for (NL, EN)
        - length: Word length
        - exclude: Exclude letters
        - include: Include letters
        - pattern: Word pattern (e.g., "A__LE")
        - word_count: Maximum number of words to return
    """
    from .wordfinder import WordFilter
    session_id = get_session(request)
    word_filter = WordFilter()

    # Validate the requested language
    valid_tables = ["NL", "EN"]  # Extend this if you add more languages
    if lang.upper() not in valid_tables:
        return {"error": "Invalid language. Choose from: " + ", ".join(valid_tables)}

    # Dynamically select table based on language
    table_name = lang.upper()
    with Session(engine) as session:
        #query = f"SELECT word FROM {table_name}"  # Unsafe, better with SQLModel reflection
        result = session.exec(text(f"SELECT word FROM {table_name}")).all()
        words = [row[0] for row in result]

    # Apply filters
    if length:
        words = word_filter.by_length(words, length)
    if exclude:
        words = word_filter.exclude_letters(words, exclude.upper())
    if include:
        words = word_filter.include_letters(words, include.upper())
    if pattern:
        words = word_filter.by_pattern(words, pattern.upper())

    # Store results in session
    SESSION_STORE[session_id]["words"] = words
    SESSION_STORE[session_id]["created"] = time.time()

    return {"session_id": session_id,
            "words": words,
            "language": table_name,
            "included_letters": word_filter.included_letters,
            "excluded_letters": word_filter.excluded_letters,
            "pattern": word_filter.pattern,
            "count": word_filter.word_count}


@app.get("/results/")
async def get_results(request: Request):
    session_id = get_session(request)
    if session_id in SESSION_STORE:
        return {"session_id": session_id, "words": SESSION_STORE[session_id]["words"]}
    return {"message": "No active session."}

@app.get("/reset/")
async def reset_session(request: Request):
    session_id = get_session(request)
    SESSION_STORE[session_id] = {"created": time.time(), "words": []}
    return {"message": "Session reset."}