from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from backend.query_agent import answer_question, handle_file_upload  # your existing logic

app = FastAPI()

# Serve React build folder
app.mount("/", StaticFiles(directory="frontend/build", html=True), name="frontend")

# API route to ask SQL questions
@app.post("/ask")
async def ask(data: dict):
    question = data.get("question")
    if not question:
        return JSONResponse(content={"sql": None, "answer": "No question provided", "result": None})
    response = answer_question(question)
    return response

# API route to handle file upload
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        result = await handle_file_upload(file)
        return result
    except Exception as e:
        return JSONResponse(content={"error": str(e)})
