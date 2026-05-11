from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List
from backend.core.database import get_db
from backend.schemas import schemas
from backend.models import models
from backend.services import excel_service

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/students", response_model=List[schemas.Student])
def get_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = db.query(models.Student).offset(skip).limit(limit).all()
    return students

@router.post("/students", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    # Check if student exists
    db_student = db.query(models.Student).filter(models.Student.student_code == student.student_code).first()
    if db_student:
        raise HTTPException(status_code=400, detail="Mã học sinh đã tồn tại")
    
    # Create student
    student_data = student.model_dump()
    vehicles_data = student_data.pop("vehicles", [])
    
    db_student = models.Student(**student_data)
    db.add(db_student)
    db.flush() # Get student id
    
    # Create vehicles
    for v_data in vehicles_data:
        db_vehicle = models.Vehicle(**v_data, student_id=db_student.id)
        db.add(db_vehicle)
    
    db.commit()
    db.refresh(db_student)
    return db_student

@router.put("/students/{student_id}", response_model=schemas.Student)
def update_student(student_id: int, student_update: schemas.StudentCreate, db: Session = Depends(get_db)):
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Không tìm thấy học sinh")
    
    # Update student info
    for key, value in student_update.model_dump(exclude={"vehicles"}).items():
        setattr(db_student, key, value)
    
    # Simple vehicle update (replace all for now)
    if student_update.vehicles:
        # Delete old
        db.query(models.Vehicle).filter(models.Vehicle.student_id == student_id).delete()
        # Add new
        for v_data in student_update.vehicles:
            db_vehicle = models.Vehicle(**v_data.model_dump(), student_id=student_id)
            db.add(db_vehicle)
            
    db.commit()
    db.refresh(db_student)
    return db_student

@router.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Không tìm thấy học sinh")
    
    db.delete(db_student)
    db.commit()
    return {"message": "Đã xóa học sinh và dữ liệu liên quan"}

@router.get("/template")
def get_excel_template(db: Session = Depends(get_db)):
    content = excel_service.create_template(db)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=template_hoc_sinh.xlsx"}
    )

@router.post("/import-excel")
async def import_excel(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file Excel (.xlsx, .xls)")
    
    content = await file.read()
    try:
        count = excel_service.import_students_from_excel(db, content)
        return {"message": f"Đã nhập thành công {count} bản ghi"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")

@router.get("/payment-status")
def get_payment_status(db: Session = Depends(get_db)):
    import datetime
    now = datetime.datetime.now()
    students = db.query(models.Student).all()
    results = []
    for s in students:
        vehicle = s.vehicles[0] if s.vehicles else None
        is_paid = False
        if vehicle:
            p = db.query(models.Payment).filter(
                models.Payment.vehicle_id == vehicle.id,
                models.Payment.month == now.month,
                models.Payment.year == now.year
            ).first()
            is_paid = p.is_paid if p else False
        
        results.append({
            "id": s.id,
            "student_code": s.student_code,
            "full_name": s.full_name,
            "class_name": s.class_name,
            "vehicle_type": vehicle.vehicle_type.value if vehicle else "---",
            "is_paid": is_paid
        })
    return results

@router.post("/payments/{student_id}/toggle")
def toggle_payment(student_id: int, db: Session = Depends(get_db)):
    import datetime
    now = datetime.datetime.now()
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student or not student.vehicles:
        return {"error": "Student or vehicle not found"}
    
    v_id = student.vehicles[0].id
    p = db.query(models.Payment).filter(
        models.Payment.vehicle_id == v_id,
        models.Payment.month == now.month,
        models.Payment.year == now.year
    ).first()
    
    if p:
        p.is_paid = not p.is_paid
    else:
        p = models.Payment(vehicle_id=v_id, month=now.month, year=now.year, is_paid=True)
        db.add(p)
    
    db.commit()
    return {"is_paid": p.is_paid}

@router.get("/access-logs")
async def get_access_logs(db: Session = Depends(get_db)):
    from backend.models.models import AccessLog, Vehicle, Student, Payment
    import datetime
    now = datetime.datetime.now()
    
    logs = db.query(AccessLog).order_by(AccessLog.timestamp.desc()).limit(100).all()
    results = []
    for log in logs:
        vehicle = db.query(Vehicle).filter(Vehicle.id == log.vehicle_id).first() if log.vehicle_id else None
        student = db.query(Student).filter(Student.id == vehicle.student_id).first() if vehicle else None
        
        is_paid = False
        if vehicle:
            p = db.query(Payment).filter(
                Payment.vehicle_id == vehicle.id,
                Payment.month == now.month,
                Payment.year == now.year
            ).first()
            is_paid = p.is_paid if p else False
        
        status_text = "Hợp lệ"
        if not vehicle:
            status_text = "Vãng lai"
        elif not is_paid:
            status_text = "Chưa đóng phí"
        else:
            status_text = "Đã đóng phí"
            
        results.append({
            "id": log.id,
            "timestamp": log.timestamp.strftime("%H:%M:%S %d/%m/%Y"),
            "image_path": log.image_path,
            "license_plate": vehicle.license_plate if vehicle else "Không rõ",
            "full_name": student.full_name if student else "Vãng lai",
            "vehicle_type": vehicle.vehicle_type.value if vehicle else "Xe máy",
            "is_registered": vehicle is not None,
            "is_paid": is_paid,
            "status_text": status_text
        })
    return results

@router.get("/dashboard-stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    from backend.models.models import Student, Vehicle, Payment, AccessLog
    from sqlalchemy import func
    import datetime
    now = datetime.datetime.now()
    
    total_students = db.query(Student).count()
    motorbikes = db.query(Vehicle).filter(Vehicle.vehicle_type == "MOTORBIKE").count()
    bicycles = db.query(Vehicle).filter(Vehicle.vehicle_type == "BICYCLE").count()
    
    # Paid stats for current month
    paid_count = db.query(Payment).filter(
        Payment.month == now.month,
        Payment.year == now.year,
        Payment.is_paid == True
    ).count()
    
    # Recent activity for chart (last 7 days)
    activity_data = []
    for i in range(6, -1, -1):
        date = (now - datetime.timedelta(days=i)).date()
        count = db.query(AccessLog).filter(func.date(AccessLog.timestamp) == date).count()
        activity_data.append({
            "date": date.strftime("%d/%m"),
            "count": count
        })
    
    # Recent 5 logs
    recent_logs = db.query(AccessLog).order_by(AccessLog.timestamp.desc()).limit(5).all()
    recent_logs_data = []
    for log in recent_logs:
        vehicle = db.query(Vehicle).filter(Vehicle.id == log.vehicle_id).first()
        recent_logs_data.append({
            "time": log.timestamp.strftime("%H:%M"),
            "plate": vehicle.license_plate if vehicle else "Vãng lai",
            "type": vehicle.vehicle_type.value if vehicle else "Xe máy"
        })
        
    return {
        "total_students": total_students,
        "motorbikes": motorbikes,
        "bicycles": bicycles,
        "paid_count": paid_count,
        "unpaid_count": max(0, total_students - paid_count),
        "activity_chart": activity_data,
        "recent_logs": recent_logs_data
    }
