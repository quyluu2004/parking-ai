# Công nghệ sử dụng (Tech Stack)

## Backend
- **Ngôn ngữ**: Python 3.10+
- **Framework**: FastAPI (Hiệu năng cao, async)
- **Database**: SQLAlchemy ORM (SQLite cho dev, tương thích PostgreSQL cho prod)
- **Tiện ích**: 
  - `python-multipart` cho upload file.
  - `jinja2` cho template (nếu cần).
  - `uvicorn` làm server engine.

## AI & Computer Vision
- **YOLOv8**: Nhận diện vật thể (Xe máy, Biển số).
- **EasyOCR**: Trích xuất ký tự từ ảnh biển số.
- **OpenCV**: Xử lý luồng video và camera.

## Frontend
- **Giao diện**: HTML5, CSS3 (Vanilla), FontAwesome 6.
- **Logic**: JavaScript (ES6+), Fetch API.
- **Biểu đồ**: HTML5 Canvas (Vẽ biểu đồ động).

## Hạ tầng & Triển khai
- **Hệ điều hành**: Windows (Hiện tại), Linux (Khuyến nghị).
- **Lưu trữ**: Local storage cho ảnh nhật ký (`vehicle_ai_logs`).
