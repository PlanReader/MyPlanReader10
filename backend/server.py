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
import stripe
import hashlib
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="MyPlanReader API", version="3.0.0")

# Stripe configuration
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')

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
payments_collection = db.payments
users_collection = db.users
projects_collection = db.projects

# ============================================
# USER AUTHENTICATION
# ============================================

class UserSignUp(BaseModel):
    email: str
    password: str
    name: Optional[str] = ""

class UserSignIn(BaseModel):
    email: str
    password: str

def hash_password(password: str) -> str:
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

@app.post("/api/auth/signup")
async def signup(user: UserSignUp):
    """Register a new user"""
    # Check if user exists
    existing = users_collection.find_one({"email": user.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_data = {
        "id": str(uuid.uuid4()),
        "email": user.email.lower(),
        "password": hash_password(user.password),
        "name": user.name or user.email.split("@")[0],
        "created_at": datetime.utcnow().isoformat()
    }
    users_collection.insert_one(user_data)
    
    return {
        "success": True,
        "user": {
            "id": user_data["id"],
            "email": user_data["email"],
            "name": user_data["name"]
        }
    }

@app.post("/api/auth/signin")
async def signin(credentials: UserSignIn):
    """Sign in a user"""
    user = users_collection.find_one({
        "email": credentials.email.lower(),
        "password": hash_password(credentials.password)
    })
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return {
        "success": True,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user.get("name", "")
        }
    }

@app.get("/api/auth/user/{user_id}")
async def get_user(user_id: str):
    """Get user by ID"""
    user = users_collection.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user.get("name", "")
    }

# ============================================
# USER PROJECTS
# ============================================

@app.get("/api/projects/{user_id}")
async def get_user_projects(user_id: str):
    """Get all projects for a user"""
    projects = list(projects_collection.find({"user_id": user_id}).sort("created_at", -1))
    
    result = []
    for p in projects:
        result.append({
            "id": p["id"],
            "filename": p.get("filename", "Unknown"),
            "status": p.get("status", "pending"),
            "trades": p.get("selected_trades", []),
            "total_fee": p.get("total_fee", 0),
            "donation_amount": 1.00,  # $1 to Tunnel to Towers
            "materials": p.get("materials"),
            "created_at": p.get("created_at")
        })
    
    return {"projects": result}

@app.get("/api/project/{project_id}")
async def get_project(project_id: str):
    """Get a specific project"""
    project = projects_collection.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {
        "id": project["id"],
        "user_id": project.get("user_id"),
        "filename": project.get("filename"),
        "status": project.get("status"),
        "trades": project.get("selected_trades", []),
        "total_fee": project.get("total_fee"),
        "donation_amount": 1.00,
        "materials": project.get("materials"),
        "page_count": project.get("page_count"),
        "created_at": project.get("created_at")
    }

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

def calculate_stucco_materials(sq_ft: float) -> Dict:
    """Calculate stucco materials - all values rounded UP to whole numbers"""
    # Stucco mix: 1 bag covers ~25 sq ft
    stucco_bags = math.ceil(sq_ft / 25)
    
    # Sand: 1 cubic ft per 10 sq ft
    sand_cubic_ft = math.ceil(sq_ft / 10)
    
    # Metal lath: 1 sheet (2.5 sq yd) covers ~22.5 sq ft
    metal_lath_sheets = math.ceil(sq_ft / 22.5)
    
    # Furring nails: 1 lb per 50 sq ft
    furring_nails_lbs = math.ceil(sq_ft / 50)
    
    # Corner bead: 1 per 8 linear ft of corners (estimate 1 per 100 sq ft)
    corner_beads = math.ceil(sq_ft / 100)
    
    # Bonding agent: 1 gallon per 200 sq ft
    bonding_agent_gal = math.ceil(sq_ft / 200)
    
    return {
        "stucco_bags": stucco_bags,
        "sand_cubic_ft": sand_cubic_ft,
        "metal_lath_sheets": metal_lath_sheets,
        "furring_nails_lbs": max(1, furring_nails_lbs),
        "corner_beads": max(1, corner_beads),
        "bonding_agent_gallons": max(1, bonding_agent_gal)
    }

def calculate_exterior_paint_materials(sq_ft: float, coats: int = 2) -> Dict:
    """Calculate exterior paint materials - all values rounded UP to whole numbers"""
    total_coverage = sq_ft * coats
    
    # Exterior paint: 1 gallon covers ~300 sq ft (less than interior due to texture)
    paint_gallons = math.ceil(total_coverage / 300)
    
    # Exterior primer: 1 gallon covers ~350 sq ft
    primer_gallons = math.ceil(sq_ft / 350)
    
    # Caulk tubes: 1 per 50 linear ft of trim (estimate 1 per 100 sq ft)
    caulk_tubes = math.ceil(sq_ft / 100)
    
    # Rollers (exterior grade, 1 per 400 sq ft)
    rollers = math.ceil(sq_ft / 400)
    
    # Extension poles: 1 per 500 sq ft
    extension_poles = math.ceil(sq_ft / 500)
    
    # Painter's plastic (for protection): 1 roll per 200 sq ft
    plastic_rolls = math.ceil(sq_ft / 200)
    
    # Masking tape rolls
    tape_rolls = math.ceil(sq_ft / 75)
    
    return {
        "exterior_paint_gallons": paint_gallons,
        "exterior_primer_gallons": primer_gallons,
        "caulk_tubes": max(1, caulk_tubes),
        "exterior_rollers": max(1, rollers),
        "extension_poles": max(1, extension_poles),
        "plastic_rolls": max(1, plastic_rolls),
        "masking_tape_rolls": max(1, tape_rolls)
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
    """Create a new task with automatic material calculation"""
    now = datetime.utcnow().isoformat()
    
    # Calculate materials if trade and measurements provided
    materials = None
    if task.trade and task.measurements:
        materials = calculate_materials_for_trade(task.trade, task.measurements)
    
    task_data = {
        "id": str(uuid.uuid4()),
        "title": task.title,
        "description": task.description or "",
        "status": task.status,
        "priority": task.priority,
        "category": task.category or "General",
        "trade": task.trade,
        "due_date": task.due_date,
        "measurements": task.measurements,
        "materials": materials,
        "created_at": now,
        "updated_at": now
    }
    tasks_collection.insert_one(task_data)
    return task_helper(task_data)

@app.put("/api/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate):
    """Update an existing task with automatic material recalculation"""
    task = tasks_collection.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = {k: v for k, v in task_update.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    # Recalculate materials if measurements or trade changed
    trade = update_data.get("trade", task.get("trade"))
    measurements = update_data.get("measurements", task.get("measurements"))
    if trade and measurements:
        update_data["materials"] = calculate_materials_for_trade(trade, measurements)
    
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

# ============================================
# MATERIAL CALCULATION & SHOPPING LIST APIs
# ============================================

@app.post("/api/calculate-materials")
async def calculate_materials(calc: MaterialCalculation):
    """Calculate materials for a given trade and measurements - ALL ROUNDED UP"""
    materials = calculate_materials_for_trade(calc.trade, calc.measurements)
    return {
        "trade": calc.trade,
        "measurements": calc.measurements,
        "materials": materials,
        "note": "All quantities rounded UP to nearest whole number"
    }

@app.get("/api/shopping-list")
async def get_shopping_list(trade: Optional[str] = None):
    """
    Get aggregated shopping list from all tasks with materials.
    ALL quantities are WHOLE NUMBERS (rounded UP).
    """
    query = {"materials": {"$ne": None}}
    if trade:
        query["trade"] = trade
    
    # Aggregate all materials
    aggregated = {}
    tasks_with_materials = []
    
    for task in tasks_collection.find(query):
        if task.get("materials"):
            tasks_with_materials.append({
                "task_title": task["title"],
                "trade": task.get("trade"),
                "materials": task["materials"]
            })
            
            for item, qty in task["materials"].items():
                if isinstance(qty, (int, float)) and item != "note":
                    # Round UP and ensure whole number
                    whole_qty = math.ceil(qty)
                    aggregated[item] = aggregated.get(item, 0) + whole_qty
    
    # Ensure ALL final values are whole numbers (rounded UP)
    final_list = {}
    for item, qty in aggregated.items():
        final_list[item] = math.ceil(qty)  # Double-ensure whole numbers
    
    return {
        "shopping_list": final_list,
        "total_items": len(final_list),
        "tasks_included": len(tasks_with_materials),
        "breakdown_by_task": tasks_with_materials,
        "note": "All quantities are WHOLE NUMBERS (rounded UP)"
    }

@app.get("/api/export/shopping-list")
async def export_shopping_list_csv(trade: Optional[str] = None):
    """Export shopping list as CSV - ALL quantities as WHOLE NUMBERS"""
    # Get shopping list data
    query = {"materials": {"$ne": None}}
    if trade:
        query["trade"] = trade
    
    aggregated = {}
    for task in tasks_collection.find(query):
        if task.get("materials"):
            for item, qty in task["materials"].items():
                if isinstance(qty, (int, float)) and item != "note":
                    whole_qty = math.ceil(qty)
                    aggregated[item] = aggregated.get(item, 0) + whole_qty
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Item", "Quantity", "Unit"])
    
    # Define units for items
    units = {
        "drywall_sheets": "sheets",
        "studs": "pieces",
        "screws": "pieces",
        "joint_compound_gallons": "gallons",
        "tape_rolls": "rolls",
        "ductwork_linear_ft": "linear ft",
        "duct_tape_rolls": "rolls",
        "hangers": "pieces",
        "registers": "pieces",
        "flex_connectors": "pieces",
        "paint_gallons": "gallons",
        "primer_gallons": "gallons",
        "rollers": "pieces",
        "brushes": "pieces",
        "drop_cloths": "pieces",
        "painters_tape_rolls": "rolls",
        "wire_feet": "feet",
        "outlet_boxes": "pieces",
        "switch_boxes": "pieces",
        "wire_nuts": "pieces",
        "staples": "pieces",
        "outlets": "pieces",
        "switches": "pieces",
        "pipe_feet": "feet",
        "fittings": "pieces",
        "adhesive_units": "units",
        "fixtures": "pieces"
    }
    
    for item, qty in sorted(aggregated.items()):
        # Format item name nicely
        formatted_name = item.replace("_", " ").title()
        # Ensure whole number
        whole_qty = math.ceil(qty)
        unit = units.get(item, "units")
        writer.writerow([formatted_name, whole_qty, unit])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=shopping_list_{datetime.utcnow().strftime('%Y%m%d')}.csv"}
    )

@app.get("/api/export/tasks")
async def export_tasks_csv(trade: Optional[str] = None, status: Optional[str] = None):
    """Export tasks with materials as CSV - ALL material quantities as WHOLE NUMBERS"""
    query = {}
    if trade:
        query["trade"] = trade
    if status:
        query["status"] = status
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Title", "Trade", "Status", "Priority", "Due Date", "Materials Summary"])
    
    for task in tasks_collection.find(query).sort("created_at", -1):
        materials_summary = ""
        if task.get("materials"):
            # Format materials with WHOLE numbers only
            items = []
            for item, qty in task["materials"].items():
                if isinstance(qty, (int, float)) and item != "note":
                    whole_qty = math.ceil(qty)
                    items.append(f"{item.replace('_', ' ')}: {whole_qty}")
            materials_summary = "; ".join(items)
        
        writer.writerow([
            task["title"],
            task.get("trade", ""),
            task["status"],
            task["priority"],
            task.get("due_date", ""),
            materials_summary
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=tasks_export_{datetime.utcnow().strftime('%Y%m%d')}.csv"}
    )

# ============================================
# BLUEPRINT PROCESSING API
# ============================================

class BlueprintUpload(BaseModel):
    filename: str
    page_count: int
    selected_trades: List[str]  # e.g., ["Drywall", "Painting", "Stucco"]
    total_fee: float

@app.post("/api/process-blueprint")
async def process_blueprint(upload: BlueprintUpload):
    """
    Process uploaded blueprint and generate materials.
    Simulates parsing blueprint divisions and calculating whole-unit quantities.
    All material quantities are ROUNDED UP to whole numbers.
    """
    import random
    import time
    
    # Validate page count
    if upload.page_count > 25:
        raise HTTPException(status_code=400, detail="Maximum 25 pages allowed for single use")
    
    # Generate realistic measurements based on page count (more pages = larger project)
    base_sq_ft = upload.page_count * random.randint(150, 300)
    base_linear_ft = upload.page_count * random.randint(40, 80)
    wall_height = 8  # Standard wall height
    
    # Store the project
    project_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    all_materials = {}
    tasks_created = []
    
    for trade in upload.selected_trades:
        trade_lower = trade.lower()
        materials = {}
        
        if trade_lower == "drywall":
            # Calculate drywall materials based on linear footage
            materials = calculate_drywall_materials(base_linear_ft, wall_height)
            task_title = f"Drywall Takeoff - {upload.filename}"
            measurements = {"length_ft": base_linear_ft, "height_ft": wall_height}
            
        elif trade_lower == "painting":
            # Calculate interior painting materials
            materials = calculate_painting_materials(base_sq_ft, 2)
            task_title = f"Interior Painting - {upload.filename}"
            measurements = {"sq_ft": base_sq_ft, "coats": 2}
            
        elif trade_lower == "stucco":
            # Calculate stucco materials (typically 60% of wall area for exterior)
            stucco_sq_ft = math.ceil(base_sq_ft * 0.6)
            materials = calculate_stucco_materials(stucco_sq_ft)
            task_title = f"Stucco Work - {upload.filename}"
            measurements = {"sq_ft": stucco_sq_ft}
            
        elif trade_lower == "exterior paint":
            # Calculate exterior paint materials
            exterior_sq_ft = math.ceil(base_sq_ft * 0.5)
            materials = calculate_exterior_paint_materials(exterior_sq_ft, 2)
            task_title = f"Exterior Paint - {upload.filename}"
            measurements = {"sq_ft": exterior_sq_ft, "coats": 2}
        
        else:
            continue
        
        # Create task for this trade
        task_data = {
            "id": str(uuid.uuid4()),
            "title": task_title,
            "description": f"Auto-generated from blueprint: {upload.filename} ({upload.page_count} pages)",
            "status": "todo",
            "priority": "high",
            "category": "Work",
            "trade": trade,
            "due_date": None,
            "measurements": measurements,
            "materials": materials,
            "project_id": project_id,
            "created_at": now,
            "updated_at": now
        }
        
        tasks_collection.insert_one(task_data)
        tasks_created.append({
            "task_id": task_data["id"],
            "trade": trade,
            "materials": materials
        })
        
        # Aggregate materials
        for item, qty in materials.items():
            if isinstance(qty, (int, float)):
                all_materials[item] = all_materials.get(item, 0) + math.ceil(qty)
    
    # Ensure all final quantities are whole numbers
    final_materials = {k: math.ceil(v) for k, v in all_materials.items()}
    
    return {
        "success": True,
        "project_id": project_id,
        "filename": upload.filename,
        "page_count": upload.page_count,
        "trades_processed": upload.selected_trades,
        "total_fee": upload.total_fee,
        "tasks_created": len(tasks_created),
        "aggregated_materials": final_materials,
        "total_material_items": len(final_materials),
        "breakdown": tasks_created,
        "note": "All quantities are WHOLE NUMBERS (rounded UP)"
    }

@app.get("/api/pricing")
async def get_pricing():
    """Get current pricing for blueprint processing"""
    return {
        "base_trade": {
            "name": "Drywall",
            "price": 25.00,
            "included": True
        },
        "add_ons": [
            {"name": "Painting", "price": 10.00},
            {"name": "Stucco", "price": 10.00},
            {"name": "Exterior Paint", "price": 10.00}
        ],
        "max_pages": 25,
        "currency": "USD",
        "stripe_publishable_key": STRIPE_PUBLISHABLE_KEY
    }

# ============================================
# STRIPE PAYMENT ENDPOINTS
# ============================================

class CreateCheckoutSession(BaseModel):
    filename: str
    page_count: int
    selected_trades: List[str]
    total_amount: int  # Amount in cents
    success_url: str
    cancel_url: str

@app.post("/api/create-checkout-session")
async def create_checkout_session(data: CreateCheckoutSession):
    """Create a Stripe Checkout session for blueprint processing payment"""
    try:
        # Build line items based on selected trades
        line_items = []
        
        # Base Drywall trade
        line_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": "Blueprint Analysis - Drywall (Base)",
                    "description": f"Material takeoff for {data.filename} ({data.page_count} pages)",
                },
                "unit_amount": 2500,  # $25.00 in cents
            },
            "quantity": 1,
        })
        
        # Add-on trades
        addon_trades = [t for t in data.selected_trades if t != "Drywall"]
        for trade in addon_trades:
            line_items.append({
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Add-on: {trade} Analysis",
                        "description": f"{trade} material calculations",
                    },
                    "unit_amount": 1000,  # $10.00 in cents
                },
                "quantity": 1,
            })
        
        # Create payment record
        payment_id = str(uuid.uuid4())
        payment_record = {
            "id": payment_id,
            "filename": data.filename,
            "page_count": data.page_count,
            "selected_trades": data.selected_trades,
            "total_amount": data.total_amount,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        payments_collection.insert_one(payment_record)
        
        # Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=f"{data.success_url}?session_id={{CHECKOUT_SESSION_ID}}&payment_id={payment_id}",
            cancel_url=data.cancel_url,
            metadata={
                "payment_id": payment_id,
                "filename": data.filename,
                "page_count": str(data.page_count),
                "trades": ",".join(data.selected_trades)
            }
        )
        
        # Update payment record with session ID
        payments_collection.update_one(
            {"id": payment_id},
            {"$set": {"stripe_session_id": checkout_session.id}}
        )
        
        return {
            "session_id": checkout_session.id,
            "session_url": checkout_session.url,
            "payment_id": payment_id
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/verify-payment/{payment_id}")
async def verify_payment(payment_id: str, session_id: Optional[str] = None):
    """Verify payment status and return payment details"""
    try:
        # Find payment record
        payment = payments_collection.find_one({"id": payment_id})
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # If we have a session ID, verify with Stripe
        if session_id or payment.get("stripe_session_id"):
            sid = session_id or payment.get("stripe_session_id")
            try:
                session = stripe.checkout.Session.retrieve(sid)
                
                if session.payment_status == "paid":
                    # Update payment status
                    payments_collection.update_one(
                        {"id": payment_id},
                        {"$set": {
                            "status": "paid",
                            "paid_at": datetime.utcnow().isoformat(),
                            "stripe_payment_intent": session.payment_intent
                        }}
                    )
                    
                    return {
                        "verified": True,
                        "status": "paid",
                        "payment_id": payment_id,
                        "filename": payment.get("filename"),
                        "page_count": payment.get("page_count"),
                        "selected_trades": payment.get("selected_trades"),
                        "total_amount": payment.get("total_amount")
                    }
                else:
                    return {
                        "verified": False,
                        "status": session.payment_status,
                        "payment_id": payment_id
                    }
            except stripe.error.StripeError:
                pass
        
        return {
            "verified": payment.get("status") == "paid",
            "status": payment.get("status", "pending"),
            "payment_id": payment_id,
            "filename": payment.get("filename"),
            "selected_trades": payment.get("selected_trades")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stripe-config")
async def get_stripe_config():
    """Get Stripe publishable key for frontend"""
    return {
        "publishable_key": STRIPE_PUBLISHABLE_KEY
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
