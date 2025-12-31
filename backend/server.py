from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
import os
import uuid
import math
import csv
import io
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
materials_collection = db.materials

# ============================================
# MATERIAL CALCULATION FORMULAS (All rounded UP)
# ============================================

def calculate_drywall_materials(length_ft: float, height_ft: float = 8.0) -> Dict:
    """Calculate drywall materials - all values rounded UP to whole numbers"""
    sq_ft = length_ft * height_ft
    
    # Drywall sheets (4x8 = 32 sq ft per sheet)
    sheets = math.ceil(sq_ft / 32)
    
    # Studs: one every 16 inches (1.33 ft) plus 1 for start
    stud_count = math.ceil(length_ft / 1.33) + 1
    
    # Screws: approximately 32 per sheet
    screws = math.ceil(sheets * 32)
    
    # Joint compound (1 gallon per 100 sq ft)
    joint_compound_gal = math.ceil(sq_ft / 100)
    
    # Tape (1 roll per 500 sq ft)
    tape_rolls = math.ceil(sq_ft / 500)
    
    return {
        "drywall_sheets": sheets,
        "studs": stud_count,
        "screws": screws,
        "joint_compound_gallons": joint_compound_gal,
        "tape_rolls": max(1, tape_rolls)
    }

def calculate_hvac_materials(sq_ft_coverage: float, num_vents: int = 1) -> Dict:
    """Calculate HVAC materials - all values rounded UP to whole numbers"""
    # Ductwork: 1 linear ft per 10 sq ft of coverage
    ductwork_ft = math.ceil(sq_ft_coverage / 10)
    
    # Duct tape rolls (1 per 50 ft of ductwork)
    duct_tape = math.ceil(ductwork_ft / 50)
    
    # Hangers (1 per 4 ft of ductwork)
    hangers = math.ceil(ductwork_ft / 4)
    
    # Registers/vents
    registers = math.ceil(num_vents)
    
    # Flex duct connectors
    connectors = math.ceil(num_vents * 2)
    
    return {
        "ductwork_linear_ft": ductwork_ft,
        "duct_tape_rolls": max(1, duct_tape),
        "hangers": hangers,
        "registers": registers,
        "flex_connectors": connectors
    }

def calculate_painting_materials(sq_ft: float, coats: int = 2) -> Dict:
    """Calculate painting materials - all values rounded UP to whole numbers"""
    total_coverage = sq_ft * coats
    
    # Paint: 1 gallon covers ~350 sq ft
    paint_gallons = math.ceil(total_coverage / 350)
    
    # Primer: 1 gallon covers ~400 sq ft (single coat)
    primer_gallons = math.ceil(sq_ft / 400)
    
    # Rollers (1 per 500 sq ft)
    rollers = math.ceil(sq_ft / 500)
    
    # Brushes (1 per 200 sq ft for edges)
    brushes = math.ceil(sq_ft / 200)
    
    # Drop cloths (1 per 100 sq ft of floor)
    drop_cloths = math.ceil(sq_ft / 100)
    
    # Painter's tape rolls (1 per 60 linear ft, estimate 1 roll per 50 sq ft)
    tape_rolls = math.ceil(sq_ft / 50)
    
    return {
        "paint_gallons": paint_gallons,
        "primer_gallons": primer_gallons,
        "rollers": max(1, rollers),
        "brushes": max(1, brushes),
        "drop_cloths": max(1, drop_cloths),
        "painters_tape_rolls": max(1, tape_rolls)
    }

def calculate_electrical_materials(num_outlets: int, num_switches: int, wire_runs_ft: float) -> Dict:
    """Calculate electrical materials - all values rounded UP to whole numbers"""
    # Wire: add 20% for waste
    wire_ft = math.ceil(wire_runs_ft * 1.2)
    
    # Boxes (1 per outlet + 1 per switch)
    boxes = math.ceil(num_outlets + num_switches)
    
    # Wire nuts (10 per box)
    wire_nuts = math.ceil(boxes * 10)
    
    # Staples (1 per 2 ft of wire)
    staples = math.ceil(wire_ft / 2)
    
    return {
        "wire_feet": wire_ft,
        "outlet_boxes": math.ceil(num_outlets),
        "switch_boxes": math.ceil(num_switches),
        "wire_nuts": wire_nuts,
        "staples": staples,
        "outlets": math.ceil(num_outlets),
        "switches": math.ceil(num_switches)
    }

def calculate_plumbing_materials(pipe_runs_ft: float, num_fixtures: int) -> Dict:
    """Calculate plumbing materials - all values rounded UP to whole numbers"""
    # Pipe: add 15% for fittings and waste
    pipe_ft = math.ceil(pipe_runs_ft * 1.15)
    
    # Fittings (estimate 3 per fixture + 1 per 10 ft of pipe)
    fittings = math.ceil((num_fixtures * 3) + (pipe_ft / 10))
    
    # Hangers (1 per 4 ft)
    hangers = math.ceil(pipe_ft / 4)
    
    # Solder/glue (1 unit per 20 fittings)
    adhesive = math.ceil(fittings / 20)
    
    return {
        "pipe_feet": pipe_ft,
        "fittings": fittings,
        "hangers": hangers,
        "adhesive_units": max(1, adhesive),
        "fixtures": math.ceil(num_fixtures)
    }

def calculate_general_materials(description: str) -> Dict:
    """Generic material placeholder"""
    return {
        "note": "Custom materials - add manually",
        "items": 0
    }

# Pydantic models
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = ""
    status: str = Field(default="todo")  # todo, in_progress, completed
    priority: str = Field(default="medium")  # low, medium, high
    category: Optional[str] = "General"
    trade: Optional[str] = None  # Drywall, HVAC, Painting, Electrical, Plumbing, General, etc.
    due_date: Optional[str] = None
    measurements: Optional[Dict] = None  # For material calculations

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    trade: Optional[str] = None
    due_date: Optional[str] = None
    measurements: Optional[Dict] = None

class Task(BaseModel):
    id: str
    title: str
    description: str
    status: str
    priority: str
    category: str
    trade: Optional[str]
    due_date: Optional[str]
    measurements: Optional[Dict]
    materials: Optional[Dict]
    created_at: str
    updated_at: str

# Material calculation request model
class MaterialCalculation(BaseModel):
    trade: str
    measurements: Dict

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
        "measurements": task.get("measurements"),
        "materials": task.get("materials"),
        "created_at": task["created_at"],
        "updated_at": task["updated_at"]
    }

def calculate_materials_for_trade(trade: str, measurements: Dict) -> Dict:
    """Calculate materials based on trade type - ALL VALUES ROUNDED UP"""
    if not trade or not measurements:
        return None
    
    trade_lower = trade.lower()
    
    if trade_lower == "drywall":
        length = float(measurements.get("length_ft", 0))
        height = float(measurements.get("height_ft", 8))
        return calculate_drywall_materials(length, height)
    
    elif trade_lower == "hvac":
        sq_ft = float(measurements.get("sq_ft_coverage", 0))
        vents = int(measurements.get("num_vents", 1))
        return calculate_hvac_materials(sq_ft, vents)
    
    elif trade_lower == "painting":
        sq_ft = float(measurements.get("sq_ft", 0))
        coats = int(measurements.get("coats", 2))
        return calculate_painting_materials(sq_ft, coats)
    
    elif trade_lower == "electrical":
        outlets = int(measurements.get("num_outlets", 0))
        switches = int(measurements.get("num_switches", 0))
        wire_ft = float(measurements.get("wire_runs_ft", 0))
        return calculate_electrical_materials(outlets, switches, wire_ft)
    
    elif trade_lower == "plumbing":
        pipe_ft = float(measurements.get("pipe_runs_ft", 0))
        fixtures = int(measurements.get("num_fixtures", 0))
        return calculate_plumbing_materials(pipe_ft, fixtures)
    
    else:
        return calculate_general_materials(str(measurements))

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
        "trade": task.trade,
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

@app.get("/api/trades")
async def get_trades():
    """Get all unique trades"""
    trades = tasks_collection.distinct("trade")
    # Filter out None values and return default trades if empty
    trades = [t for t in trades if t]
    default_trades = ["Drywall", "HVAC", "Painting", "Electrical", "Plumbing", "General"]
    all_trades = list(set(default_trades + trades))
    all_trades.sort()
    return {"trades": all_trades}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
