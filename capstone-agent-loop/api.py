from fastapi import FastAPI
from pydantic import BaseModel
from agent import run_agent

app = FastAPI()

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask(payload: Question):
    answer = run_agent(payload.question)
    return {"answer": answer}