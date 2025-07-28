from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, date
from enum import Enum


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Enums
class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Task Models
class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    priority: TaskPriority = TaskPriority.MEDIUM

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None

class DashboardStats(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    overdue_tasks: int
    today_tasks: int


# Helper functions
def task_dict_to_model(task_dict):
    if task_dict:
        # Convert due_date string back to date object if it exists
        if task_dict.get('due_date'):
            task_dict['due_date'] = datetime.fromisoformat(task_dict['due_date']).date()
        # Convert datetime strings back to datetime objects
        if task_dict.get('created_at'):
            task_dict['created_at'] = datetime.fromisoformat(task_dict['created_at'])
        if task_dict.get('updated_at'):
            task_dict['updated_at'] = datetime.fromisoformat(task_dict['updated_at'])
        return Task(**task_dict)
    return None

def task_model_to_dict(task):
    task_dict = task.dict()
    # Convert date objects to ISO format strings for MongoDB storage
    if task_dict.get('due_date'):
        task_dict['due_date'] = task_dict['due_date'].isoformat()
    if task_dict.get('created_at'):
        task_dict['created_at'] = task_dict['created_at'].isoformat()
    if task_dict.get('updated_at'):
        task_dict['updated_at'] = task_dict['updated_at'].isoformat()
    return task_dict


# Task Routes
@api_router.post("/tasks", response_model=Task)
async def create_task(task_input: TaskCreate):
    task_dict = task_input.dict()
    task = Task(**task_dict)
    task_dict = task_model_to_dict(task)
    await db.tasks.insert_one(task_dict)
    return task

@api_router.get("/tasks", response_model=List[Task])
async def get_tasks():
    tasks = await db.tasks.find().to_list(1000)
    return [task_dict_to_model(task) for task in tasks]

@api_router.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    task = await db.tasks.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_dict_to_model(task)

@api_router.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate):
    update_data = {k: v for k, v in task_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    # Convert date to ISO format for storage
    if update_data.get('due_date'):
        update_data['due_date'] = update_data['due_date'].isoformat()
    
    result = await db.tasks.update_one(
        {"id": task_id}, 
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    updated_task = await db.tasks.find_one({"id": task_id})
    return task_dict_to_model(updated_task)

@api_router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    result = await db.tasks.delete_one({"id": task_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}

# Dashboard Routes
@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    today = date.today()
    
    # Get all tasks
    all_tasks = await db.tasks.find().to_list(1000)
    tasks = [task_dict_to_model(task) for task in all_tasks]
    
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
    pending_tasks = len([t for t in tasks if t.status != TaskStatus.COMPLETED])
    
    # Calculate overdue tasks
    overdue_tasks = len([
        t for t in tasks 
        if t.due_date and t.due_date < today and t.status != TaskStatus.COMPLETED
    ])
    
    # Calculate today's tasks
    today_tasks = len([
        t for t in tasks 
        if t.due_date and t.due_date == today
    ])
    
    return DashboardStats(
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,
        today_tasks=today_tasks
    )

@api_router.get("/dashboard/recent-tasks", response_model=List[Task])
async def get_recent_tasks():
    tasks = await db.tasks.find().sort("created_at", -1).limit(5).to_list(5)
    return [task_dict_to_model(task) for task in tasks]

@api_router.get("/dashboard/upcoming-tasks", response_model=List[Task])
async def get_upcoming_tasks():
    today = date.today().isoformat()
    tasks = await db.tasks.find({
        "due_date": {"$gte": today},
        "status": {"$ne": "completed"}
    }).sort("due_date", 1).limit(5).to_list(5)
    return [task_dict_to_model(task) for task in tasks]

# Calendar Routes
@api_router.get("/calendar/tasks")
async def get_calendar_tasks(month: Optional[int] = None, year: Optional[int] = None):
    today = date.today()
    target_month = month or today.month
    target_year = year or today.year
    
    # Get start and end dates for the month
    start_date = date(target_year, target_month, 1)
    if target_month == 12:
        end_date = date(target_year + 1, 1, 1)
    else:
        end_date = date(target_year, target_month + 1, 1)
    
    # Query tasks for the date range
    tasks = await db.tasks.find({
        "due_date": {
            "$gte": start_date.isoformat(),
            "$lt": end_date.isoformat()
        }
    }).to_list(1000)
    
    return [task_dict_to_model(task) for task in tasks]


# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Time Management API"}


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()