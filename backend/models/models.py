from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Boolean, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.core.database import Base
import enum

class VehicleType(enum.Enum):
    MOTORBIKE = "MOTORBIKE"
    BICYCLE = "BICYCLE"

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_code = Column(String(20), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    class_name = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    vehicles = relationship("Vehicle", back_populates="owner")

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    license_plate = Column(String(20), nullable=True)
    tag_id = Column(String(50), nullable=True)
    color = Column(String(30))
    brand = Column(String(50))

    owner = relationship("Student", back_populates="vehicles")
    payments = relationship("Payment", back_populates="vehicle")
    logs = relationship("AccessLog", back_populates="vehicle")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    is_paid = Column(Boolean, default=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    vehicle = relationship("Vehicle", back_populates="payments")

class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    image_path = Column(String(255))
    direction = Column(String(10), default="IN")
    confidence_score = Column(Float)

    vehicle = relationship("Vehicle", back_populates="logs")