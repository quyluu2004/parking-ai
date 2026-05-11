from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import admin, ai_router, camera
from backend.core.database import engine, Base
from dotenv import load_dotenv
import os
import uvicorn

# Load environment variables
load_dotenv()

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="School Vehicle Management AI System")

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles

# Cấu hình đường dẫn lưu trữ bên ngoài dự án để tránh Live Server reload
HOME_DIR = os.path.expanduser("~")
LOGS_DIR = os.path.join(HOME_DIR, "vehicle_ai_logs")
os.makedirs(LOGS_DIR, exist_ok=True)
print(f"[*] Ảnh log sẽ được lưu tại: {LOGS_DIR}")

# Include Routers
app.include_router(admin.router)
app.include_router(ai_router.router)
app.include_router(camera.router)

# Mount static files
# Mount ảnh log từ thư mục bên ngoài
app.mount("/static/logs", StaticFiles(directory=LOGS_DIR), name="static_logs")
# Mount các file tĩnh khác (nếu có)
os.makedirs("backend/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

@app.get("/")
async def root():
    return {"message": "Welcome to School Vehicle Management API"}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
