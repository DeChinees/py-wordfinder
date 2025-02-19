from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.sessions import SessionMiddleware
from sqlmodel import SQLModel, create_engine, Field, Session, select
from uuid import uuid4

from wordfinder import exclude_letters, filter_by_length, contains_letters, filter_by_pattern

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=str(uuid4()))

@app.get("/")
async def read_root():
    return {"message": "Welcome to WordFinder!"}

@app.get("/exclude_letters")
def exclude_letters_endpoint(words: List[str] = Query(...), letters: str = Query(...)):
    words_list = words.split(",")
    result = exclude_letters(words_list, letters)
    return {"result": result}

@app.get("/filter_by_length")
def filter_by_length_endpoint(words: List[str] = Query(...), exact_length: int = Query(...)):
    words_list = words.split(",")
    result = filter_by_length(words_list, exact_length)
    return {"result": result}

@app.get("/contains_letters")
def contains_letters_endpoint(words: List[str] = Query(...), substring: str = Query(...)):
    words_list = words.split(",")
    result = contains_letters(words_list, substring)
    return {"result": result}

@app.get("/filter_by_pattern")
def filter_by_pattern_endpoint(words: List[str] = Query(...), pattern: str = Query(...)):
    words_list = words.split(",")
    result = filter_by_pattern(words_list, pattern)
    return {"result": result}




from fastapi import FastAPI
from fastapi.middleware.sessions import SessionMiddleware
from uuid import uuid4

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=str(uuid4()))  # Important for session management

# Database setup
SQLITE_FILE_NAME = "words.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

engine = create_engine(SQLITE_URL, echo=False)  # echo=False for production

class Word(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    word: str = Field(index=True)  # Index for faster searching

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
async def startup_event():
    create_db_and_tables()
    # Here you would typically load your 5MB word list into the database.
    # For demonstration, let's add a few words:
    with Session(engine) as session:
        if session.exec(select(Word)).first() is None: #check if database is empty
            words = ["apple", "banana", "orange", "grape", "kiwi", "apricot", "avocado", "blueberry", "cherry", "cranberry"] #sample words
            for word in words:
                db_word = Word(word=word)
                session.add(db_word)
            session.commit()



def get_session():
    with Session(engine) as session:
        yield session

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
    <head><title>Word Search</title></head>
    <body>
    <h1>Word Search</h1>
    <form method="GET" action="/search">
        <input type="text" name="q" placeholder="Enter word">
        <button type="submit">Search</button>
    </form>
    </body>
    </html>
    """

@app.get("/search")
async def search_words(request: Request, q: str, session: Session = Depends(get_session)):
    user_id = request.session.get("user_id")
    if not user_id:
        user_id = str(uuid4())
        request.session["user_id"] = user_id

    # Check for previous results in the session
    previous_results = request.session.get(f"results_{user_id}", [])

    if q and q not in previous_results:  # New search term
        results = session.exec(select(Word).where(Word.word.startswith(q))).all()
        results_words = [word.word for word in results]
        request.session[f"results_{user_id}"] = results_words #store results in session
    else: # q is empty or same as previous search
        results_words = previous_results

    return {"results": results_words} # return results, even if empty



@app.on_event("shutdown")
async def shutdown_event():
    # Clean up user-specific data (if needed).
    # In this example, sessions are handled by the middleware, so no database cleanup is required.
    # If you were storing user-specific data in the database, you would clean it up here.
    pass