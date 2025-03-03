from fastapi import FastAPI, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlmodel import create_engine, Session, text
from uuid import uuid4
from pydantic import BaseModel
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

# CORS settings
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    lang: str
    length: int = None
    exclude: str = ""
    include: str = ""
    pattern: str = ""


def get_session(request: Request, session_id: str = Header(None)):
    if session_id and session_id in SESSION_STORE:
        return session_id
    session_id = str(uuid4())
    request.session["session_id"] = session_id
    SESSION_STORE[session_id] = {"created": time.time(), "words": []}
    return session_id


@app.get("/")
async def read_root():
    return {"message": "Welcome to WordFinder!"}


@app.post("/search/")
async def search_words(
    request: Request,
    search_request: SearchRequest,
    session_id: str = Header(None)
):
    """Search for words in the database based on filters.
        - lang: Language to search for (NL, EN)
        - length: Word length
        - exclude: Exclude letters
        - include: Include letters
        - pattern: Word pattern (e.g., "A__LE")
    """
    from .wordfinder import WordFilter
    session_id = get_session(request, session_id)
    word_filter = WordFilter()

    # Validate the requested language
    valid_tables = ["NL", "EN"]  # Extend this if you add more languages
    if search_request.lang.upper() not in valid_tables:
        return {"error": "Invalid language. Choose from: " + ", ".join(valid_tables)}

    # Dynamically select table based on language
    table_name = search_request.lang.upper()
    with Session(engine) as session:
        result = session.exec(text(f"SELECT word FROM {table_name}")).all()
        words = [row[0] for row in result]

    # Apply filters
    if search_request.length:
        words = word_filter.by_length(words, search_request.length)
    if search_request.exclude:
        words = word_filter.exclude_letters(words, search_request.exclude.upper())
    if search_request.include:
        words = word_filter.include_letters(words, search_request.include.upper())
    if search_request.pattern:
        words = word_filter.by_pattern(words, search_request.pattern.upper())

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


@app.post("/results/")
async def get_results(request: Request, session_id: str = Header(None)):
    session_id = get_session(request, session_id)
    if session_id in SESSION_STORE:
        return {"session_id": session_id, "words": SESSION_STORE[session_id]["words"]}
    return {"message": "No active session."}


@app.post("/reset/")
async def reset_session(request: Request, session_id: str = Header(None)):
    session_id = get_session(request, session_id)
    SESSION_STORE[session_id] = {"created": time.time(), "words": []}
    return {"message": "Session reset."}