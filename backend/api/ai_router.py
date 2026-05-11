from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import os
import shutil
import uuid
import tempfile
from thefuzz import fuzz
from ai.detect import VehicleDetector
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.models import Vehicle, Student, AccessLog, Payment
import datetime

router = APIRouter(prefix="/ai", tags=["AI Recognition"])
detector = VehicleDetector()

# Global throttle for logging
LAST_LOGGED = {}

# Move upload dir outside of project to prevent Live Server reload
UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "vehicle_ai_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/detect")
async def detect_vehicle(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Save temp file
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    temp_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Lưu ảnh Debug vào thư mục TEMP để tránh Live Server tự reload trang
        debug_save_path = os.path.join(UPLOAD_DIR, "debug_capture.jpg")
        shutil.copy(temp_path, debug_save_path)
        print(f"[*] Đã lưu ảnh Debug tại thư mục TEMP: {debug_save_path}")

        # Run AI Detection
        results = detector.detect_and_ocr(temp_path)
        
        if not results:
            print("[!] AI không tìm thấy bất kỳ vật thể nào trong ảnh.")
            return {"results": [], "message": "No vehicle detected"}
        
        # Match with database using Fuzzy Matching
        enriched_results = []
        registered_vehicles = db.query(Vehicle).all()

        for res in results:
            detected_plate = res.get('license_plate', "")
            if detected_plate:
                detected_plate = detected_plate.upper()
                print(f"[*] AI đọc được biển số: {detected_plate}")
            else:
                print(f"[*] AI thấy vật thể ({res['label']}) nhưng không đọc được chữ.")

            best_match = None
            highest_score = 0
            
            for vehicle in registered_vehicles:
                if detected_plate and vehicle.license_plate:
                    score = fuzz.ratio(detected_plate, vehicle.license_plate.upper())
                    if score > highest_score:
                        highest_score = score
                        best_match = vehicle
            
            final_plate = detected_plate
            owner_info = None
            is_registered = False

            if best_match and highest_score >= 75:
                is_registered = True
                final_plate = best_match.license_plate  # Dùng biển số trong DB làm chuẩn hiển thị
                student = db.query(Student).filter(Student.id == best_match.student_id).first()
                if student:
                    owner_info = {
                        "name": student.full_name,
                        "class": student.class_name,
                        "student_code": student.student_code
                    }
            
            is_paid = False
            if best_match:
                now = datetime.datetime.now()
                p = db.query(Payment).filter(
                    Payment.vehicle_id == best_match.id,
                    Payment.month == now.month,
                    Payment.year == now.year
                ).first()
                is_paid = p.is_paid if p else False

            enriched_results.append({
                **res,
                "license_plate": final_plate,
                "is_registered": is_registered,
                "is_paid": is_paid,
                "owner": owner_info
            })

            # Save to Access Logs with Throttling
            if final_plate:
                now = datetime.datetime.now()
                if final_plate not in LAST_LOGGED or (now - LAST_LOGGED[final_plate]) > datetime.timedelta(seconds=30):
                    log_img_name = f"log_{final_plate}_{now.strftime('%H%M%S')}.jpg"
                    
                    # Lưu vào thư mục bên ngoài dự án để tránh Live Server reload
                    HOME_DIR = os.path.expanduser("~")
                    EXT_LOGS_DIR = os.path.join(HOME_DIR, "vehicle_ai_logs")
                    os.makedirs(EXT_LOGS_DIR, exist_ok=True)
                    log_img_path = os.path.join(EXT_LOGS_DIR, log_img_name)
                    
                    shutil.copy(temp_path, log_img_path)
                    
                    new_log = AccessLog(
                        vehicle_id=best_match.id if best_match else None,
                        image_path=f"/static/logs/{log_img_name}",
                        direction="IN",
                        confidence_score=res.get('confidence', 0.0)
                    )
                    db.add(new_log)
                    db.commit()
                    LAST_LOGGED[final_plate] = now
            
        return {
            "results": enriched_results,
            "image_id": file_id
        }
    finally:
        # We might want to keep the image for logging, but for now we'll delete it later
        pass
