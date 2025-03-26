# app.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from tutor import Tutor
from courses import get_courses, get_modules, get_module_content

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

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

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
    
# To run the app:
# uvicorn app:app --reload
