from fastapi import FastAPI, HTTPException, Request
from bson import ObjectId, errors
from database import db
from schemas import TodoCreate, TodoOut
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI()
collection = db["todos"]

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Helper: convert MongoDB document to dict
def todo_helper(todo) -> dict:
    return {
        "id": str(todo["_id"]),
        "title": todo["title"],
        "description": todo.get("description"),
        "completed": todo.get("completed", False),
    }

# Create
@app.post("/todo", response_model=TodoOut)
async def create_todo(todo: TodoCreate):
    todo_dict = todo.dict()
    result = await collection.insert_one(todo_dict)
    created_todo = await collection.find_one({"_id": result.inserted_id})
    return todo_helper(created_todo)

# Read all
@app.get("/todo", response_model=list[TodoOut])
async def get_all_todos():
    todos = []
    async for todo in collection.find():
        todos.append(todo_helper(todo))
    return todos

# Read one
@app.get("/todo/{todo_id}", response_model=TodoOut)
async def get_todo(todo_id: str):
    try:
        oid = ObjectId(todo_id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID")
    todo = await collection.find_one({"_id": oid})
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo_helper(todo)

# Update
@app.put("/todo/{todo_id}", response_model=TodoOut)
async def update_todo(todo_id: str, todo: TodoCreate):
    try:
        oid = ObjectId(todo_id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await collection.update_one({"_id": oid}, {"$set": todo.dict()})
    if result.modified_count == 1:
        updated_todo = await collection.find_one({"_id": oid})
        return todo_helper(updated_todo)
    raise HTTPException(status_code=404, detail="Todo not found")

# Delete
@app.delete("/todo/{todo_id}")
async def delete_todo(todo_id: str):
    try:
        oid = ObjectId(todo_id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = await collection.delete_one({"_id": oid})
    if result.deleted_count == 1:
        return {"detail": "Todo deleted"}
    raise HTTPException(status_code=404, detail="Todo not found")
