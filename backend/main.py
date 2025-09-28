from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.query_agent import answer_question  # your existing backend logic

app = FastAPI(title="AI Agent Backend")

# Allow frontend to communicate with backend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve React frontend
app.mount("/", StaticFiles(directory="../frontend/build", html=True), name="frontend")

# Example API route
@app.get("/api/hello")
def hello():
    return {"message": "Hello from FastAPI!"}

# Your existing API routes
# Make sure to prefix with /api to avoid conflict with React routes
@app.post("/api/question")
def ask_question(question: str):
    try:
        answer = answer_question(question)  # your existing function
        return {"question": question, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
