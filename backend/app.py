# app.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from tutor import Tutor
from courses import get_courses, get_modules, get_module_content
import os

app = FastAPI()
tutor = Tutor()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    index_file_path = os.path.join("frontend", "dist", "index.html")
    with open(index_file_path, "r") as file:
        return HTMLResponse(content=file.read(), status_code=200)

@app.get("/courses")
def read_courses():
    courses = get_courses()
    return {"courses": courses} if courses else {"courses": []}

@app.post("/message")
async def handle_message(request: Request):
    data = await request.json()
    user_message = data.get("message", "").strip()
    
    if not user_message:
        raise HTTPException(status_code=400, detail="Empty message")
    
    response = tutor.process_user_message(user_message)
    return {"response": response}

@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_frontend(full_path: str):
    file_path = os.path.join("frontend", "dist", full_path)
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return HTMLResponse(content=file.read(), status_code=200)
    else:
        index_file_path = os.path.join("frontend", "dist", "index.html")
        with open(index_file_path, "r") as file:
            return HTMLResponse(content=file.read(), status_code=200)
    
# To run the app:
# uvicorn app:app --reload
