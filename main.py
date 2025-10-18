from fastapi import FastAPI, HTTPException
from bson import ObjectId, errors
from model import Todo
from database import db
from schemas import TodoCreate, TodoOut

app = FastAPI()
collection = db["todos"]

# 🔧 Helper to convert MongoDB document → JSON-safe dict
def todo_helper(todo) -> dict:
    return {
        "id": str(todo["_id"]),
        "title": todo["title"],
        "description": todo.get("description"),
        "completed": todo.get("completed", False),
    }

# 🟢 Create a new TODO
@app.post("/todo", response_model=TodoOut)
async def create_todo(todo: TodoCreate):
    todo_dict = todo.dict()
    result = await collection.insert_one(todo_dict)
    created_todo = await collection.find_one({"_id": result.inserted_id})
    return todo_helper(created_todo)

# 🟡 Get all TODOs
@app.get("/todo", response_model=list[TodoOut])
async def get_all_todos():
    todos = []
    async for todo in collection.find():
        todos.append(todo_helper(todo))
    return todos

# 🔵 Get a specific TODO
@app.get("/todo/{todo_id}", response_model=TodoOut)
async def get_todo(todo_id: str):
    try:
        oid = ObjectId(todo_id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID or Not Found")

    todo = await collection.find_one({"_id": oid})
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    return todo_helper(todo)

# 🟣 Update a TODO
@app.put("/todo/{todo_id}", response_model=TodoOut)
async def update_todo(todo_id: str, todo: TodoCreate):
    try:
        oid = ObjectId(todo_id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID or Not Found")

    result = await collection.update_one({"_id": oid}, {"$set": todo.dict()})
    if result.modified_count == 1:
        updated_todo = await collection.find_one({"_id": oid})
        return todo_helper(updated_todo)

    raise HTTPException(status_code=404, detail="Todo not found")

# 🔴 Delete a TODO
@app.delete("/todo/{todo_id}")
async def delete_todo(todo_id: str):
    try:
        oid = ObjectId(todo_id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    result = await collection.delete_one({"_id": oid})
    if result.deleted_count == 1:
        return {"detail": "Todo deleted"}

    raise HTTPException(status_code=404, detail="Todo not found")
