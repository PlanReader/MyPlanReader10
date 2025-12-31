from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import os
import uuid
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Notion-Style Task Manager API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/taskmanager')
client = MongoClient(MONGO_URL)
db = client.taskmanager
tasks_collection = db.tasks

# Pydantic models
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = ""
    status: str = Field(default="todo")  # todo, in_progress, completed
    priority: str = Field(default="medium")  # low, medium, high
    category: Optional[str] = "General"
    trade: Optional[str] = None  # Drywall, HVAC, Painting, Electrical, Plumbing, General, etc.
    due_date: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    trade: Optional[str] = None
    due_date: Optional[str] = None

class Task(BaseModel):
    id: str
    title: str
    description: str
    status: str
    priority: str
    category: str
    trade: Optional[str]
    due_date: Optional[str]
    created_at: str
    updated_at: str

# Helper function to convert MongoDB document to Task
def task_helper(task) -> dict:
    return {
        "id": task["id"],
        "title": task["title"],
        "description": task.get("description", ""),
        "status": task["status"],
        "priority": task["priority"],
        "category": task.get("category", "General"),
        "trade": task.get("trade"),
        "due_date": task.get("due_date"),
        "created_at": task["created_at"],
        "updated_at": task["updated_at"]
    }

# API Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Task Manager API is running"}

@app.get("/api/tasks", response_model=List[Task])
async def get_tasks(status: Optional[str] = None, priority: Optional[str] = None, category: Optional[str] = None, trade: Optional[str] = None):
    """Get all tasks with optional filtering"""
    query = {}
    if status:
        query["status"] = status
    if priority:
        query["priority"] = priority
    if category:
        query["category"] = category
    if trade:
        query["trade"] = trade
    
    tasks = []
    for task in tasks_collection.find(query).sort("created_at", -1):
        tasks.append(task_helper(task))
    return tasks

@app.get("/api/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """Get a single task by ID"""
    task = tasks_collection.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_helper(task)

@app.post("/api/tasks", response_model=Task)
async def create_task(task: TaskCreate):
    """Create a new task"""
    now = datetime.utcnow().isoformat()
    task_data = {
        "id": str(uuid.uuid4()),
        "title": task.title,
        "description": task.description or "",
        "status": task.status,
        "priority": task.priority,
        "category": task.category or "General",
        "due_date": task.due_date,
        "created_at": now,
        "updated_at": now
    }
    tasks_collection.insert_one(task_data)
    return task_helper(task_data)

@app.put("/api/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate):
    """Update an existing task"""
    task = tasks_collection.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = {k: v for k, v in task_update.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    tasks_collection.update_one({"id": task_id}, {"$set": update_data})
    updated_task = tasks_collection.find_one({"id": task_id})
    return task_helper(updated_task)

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a task"""
    result = tasks_collection.delete_one({"id": task_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully", "id": task_id}

@app.patch("/api/tasks/{task_id}/complete")
async def complete_task(task_id: str):
    """Mark a task as completed"""
    task = tasks_collection.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    new_status = "completed" if task["status"] != "completed" else "todo"
    tasks_collection.update_one(
        {"id": task_id},
        {"$set": {"status": new_status, "updated_at": datetime.utcnow().isoformat()}}
    )
    updated_task = tasks_collection.find_one({"id": task_id})
    return task_helper(updated_task)

@app.get("/api/dashboard")
async def get_dashboard():
    """Get dashboard statistics"""
    total = tasks_collection.count_documents({})
    todo = tasks_collection.count_documents({"status": "todo"})
    in_progress = tasks_collection.count_documents({"status": "in_progress"})
    completed = tasks_collection.count_documents({"status": "completed"})
    
    # Priority breakdown
    high_priority = tasks_collection.count_documents({"priority": "high"})
    medium_priority = tasks_collection.count_documents({"priority": "medium"})
    low_priority = tasks_collection.count_documents({"priority": "low"})
    
    # Get overdue tasks (due_date is in the past and status is not completed)
    now = datetime.utcnow().isoformat()
    overdue_tasks = []
    for task in tasks_collection.find({"status": {"$ne": "completed"}, "due_date": {"$ne": None}}):
        if task.get("due_date") and task["due_date"] < now[:10]:
            overdue_tasks.append(task_helper(task))
    
    # Get categories with counts
    categories = {}
    for task in tasks_collection.find():
        cat = task.get("category", "General")
        categories[cat] = categories.get(cat, 0) + 1
    
    return {
        "total_tasks": total,
        "status_breakdown": {
            "todo": todo,
            "in_progress": in_progress,
            "completed": completed
        },
        "priority_breakdown": {
            "high": high_priority,
            "medium": medium_priority,
            "low": low_priority
        },
        "overdue_count": len(overdue_tasks),
        "overdue_tasks": overdue_tasks[:5],  # Return only first 5 overdue
        "categories": categories,
        "completion_rate": round((completed / total * 100), 1) if total > 0 else 0
    }

@app.get("/api/categories")
async def get_categories():
    """Get all unique categories"""
    categories = tasks_collection.distinct("category")
    return {"categories": categories if categories else ["General"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
