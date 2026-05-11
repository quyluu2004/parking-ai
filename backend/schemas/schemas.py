from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class VehicleBase(BaseModel):
    vehicle_type: str
    license_plate: Optional[str] = None
    tag_id: Optional[str] = None
    color: Optional[str] = None
    brand: Optional[str] = None

class VehicleCreate(VehicleBase):
    pass

class Vehicle(VehicleBase):
    id: int
    student_id: int

    class Config:
        from_attributes = True

class StudentBase(BaseModel):
    student_code: str
    full_name: str
    class_name: Optional[str] = None

class StudentCreate(StudentBase):
    vehicles: Optional[List[VehicleCreate]] = []

class Student(StudentBase):
    id: int
    created_at: datetime
    vehicles: List[Vehicle] = []

    class Config:
        from_attributes = True

class PaymentBase(BaseModel):
    month: int
    year: int
    is_paid: bool = False

class AccessLogBase(BaseModel):
    timestamp: datetime
    image_path: str
    direction: str
    confidence_score: float
