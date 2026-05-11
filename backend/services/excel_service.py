import pandas as pd
from sqlalchemy.orm import Session
from backend.models.models import Student, Vehicle, VehicleType
import io

def create_template(db: Session):
    # Fetch all students and their vehicles
    students = db.query(Student).all()
    
    data = []
    if not students:
        # Add an example row if DB is empty
        data.append({
            "Mã học sinh": "HS001",
            "Họ tên": "Nguyen Van A",
            "Lớp": "10A1",
            "Loại xe": "MOTORBIKE",
            "Biển số hoặc Mã thẻ": "29-X1 12345",
            "Màu sắc": "Đen",
            "Hãng xe": "Honda"
        })
    else:
        for s in students:
            if not s.vehicles:
                data.append({
                    "Mã học sinh": s.student_code,
                    "Họ tên": s.full_name,
                    "Lớp": s.class_name,
                    "Loại xe": "",
                    "Biển số hoặc Mã thẻ": "",
                    "Màu sắc": "",
                    "Hãng xe": ""
                })
            else:
                for v in s.vehicles:
                    data.append({
                        "Mã học sinh": s.student_code,
                        "Họ tên": s.full_name,
                        "Lớp": s.class_name,
                        "Loại xe": v.vehicle_type.value,
                        "Biển số hoặc Mã thẻ": v.license_plate if v.vehicle_type.value == "MOTORBIKE" else v.tag_id,
                        "Màu sắc": v.color or "",
                        "Hãng xe": v.brand or ""
                    })

    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='DanhSachXe')
    
    return output.getvalue()

def import_students_from_excel(db: Session, file_content: bytes):
    try:
        # Read Excel file
        df = pd.read_excel(io.BytesIO(file_content))
        
        # Required columns mapping
        col_map = {
            "Mã học sinh": "student_code",
            "Họ tên": "full_name",
            "Lớp": "class_name",
            "Loại xe": "vehicle_type",
            "Biển số hoặc Mã thẻ": "plate_tag"
        }
        
        # Check for required columns
        for col in col_map.keys():
            if col not in df.columns:
                raise ValueError(f"File Excel thiếu cột bắt buộc: '{col}'")

        # Phase 1: Validation (Check everything before saving)
        for index, row in df.iterrows():
            line_num = index + 2
            if pd.isna(row["Mã học sinh"]):
                raise ValueError(f"Dòng {line_num}: 'Mã học sinh' không được để trống.")
            if pd.isna(row["Họ tên"]):
                raise ValueError(f"Dòng {line_num}: 'Họ tên' không được để trống.")
            
            v_type = str(row["Loại xe"]).upper().strip()
            if v_type not in ["MOTORBIKE", "BICYCLE"]:
                raise ValueError(f"Dòng {line_num}: 'Loại xe' phải là 'MOTORBIKE' hoặc 'BICYCLE'. Nhận được: '{v_type}'")
            
            if pd.isna(row["Biển số hoặc Mã thẻ"]):
                raise ValueError(f"Dòng {line_num}: 'Biển số hoặc Mã thẻ' không được để trống.")

        # Phase 2: Insertion (Only if all rows are valid)
        imported_count = 0
        for _, row in df.iterrows():
            s_code = str(row['Mã học sinh']).strip()
            # Check if student exists
            student = db.query(Student).filter(Student.student_code == s_code).first()
            if not student:
                student = Student(
                    student_code=s_code,
                    full_name=str(row['Họ tên']).strip(),
                    class_name=str(row['Lớp']).strip() if not pd.isna(row['Lớp']) else ""
                )
                db.add(student)
                db.flush() # Get student ID
            
            v_type = str(row['Loại xe']).upper().strip()
            v_val = str(row['Biển số hoặc Mã thẻ']).strip()
            
            # Check if vehicle already exists
            existing_v = db.query(Vehicle).filter(
                (Vehicle.license_plate == v_val) | (Vehicle.tag_id == v_val)
            ).first()
            
            if not existing_v:
                new_vehicle = Vehicle(
                    student_id=student.id,
                    vehicle_type=VehicleType(v_type),
                    license_plate=v_val if v_type == 'MOTORBIKE' else None,
                    tag_id=v_val if v_type == 'BICYCLE' else None,
                    color=str(row.get('Màu sắc', '')) if not pd.isna(row.get('Màu sắc')) else "",
                    brand=str(row.get('Hãng xe', '')) if not pd.isna(row.get('Hãng xe')) else ""
                )
                db.add(new_vehicle)
            
            imported_count += 1
        
        db.commit()
        return imported_count
    except Exception as e:
        db.rollback()
        raise e
