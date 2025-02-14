from fastapi import FastAPI
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}