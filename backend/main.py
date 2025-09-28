from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os
from backend.query_agent import answer_question, process_uploaded_file

app = FastAPI()

# CORS settings
origins = [
    "https://ai-agent-six-brown.vercel.app",  # Your frontend URL
    "http://localhost:3000"  # Optional for local testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/")
def root():
    return {"message": "Backend is live!"}


# Ask SQL question endpoint
@app.post("/ask")
async def ask(question: dict):
    try:
        user_question = question.get("question")
        if not user_question:
            raise HTTPException(status_code=400, detail="Question is required.")
        response = answer_question(user_question)
        return response
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# File upload endpoint
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        if not file:
            raise HTTPException(status_code=400, detail="File is required.")

        upload_dir = "uploaded_files"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the file
        response = process_uploaded_file(file_path)
        return response
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
