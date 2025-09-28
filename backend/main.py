# backend/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from backend.query_agent import answer_question
from backend.file_utils import execute_sql, generate_plot

app = FastAPI()

# Allow frontend domain (replace '*' with your deployed frontend URL later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ai-agent-six-brown.vercel.app/"],  # <-- update this when frontend deployed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def ask_question(payload: dict):
    question = payload.get("question")
    sql, answer, result, plot = answer_question(question)
    return {"sql": sql, "answer": answer, "result": result, "plot": plot}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    return await execute_sql(file)
