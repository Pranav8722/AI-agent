# backend/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.file_utils import save_file, load_excel, load_csv, load_pdf

from backend.query_agent import answer_question

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask_ai(payload: Question):
    return answer_question(payload.question, agg_threshold=50)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    fname = file.filename.lower()
    saved = save_file(file)
    ext = fname.split(".")[-1]
    try:
        if ext in ("csv",):
            cols = load_csv(saved)
        elif ext in ("xls", "xlsx"):
            cols = load_excel(saved)
        elif ext in ("pdf",):
            cols = load_pdf(saved)
        else:
            return {"error": f"Unsupported file type: {ext}"}
        return {"message": f"{file.filename} uploaded", "columns": cols}
    except Exception as e:
        return {"error": str(e)}
