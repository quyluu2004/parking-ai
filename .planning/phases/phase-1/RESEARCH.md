# Nghiên cứu Giai đoạn 1: Nền tảng & Quản lý dữ liệu

## 1. Lưu trữ Hình ảnh
- **Quyết định**: Không lưu ảnh trực tiếp vào database (BLOB).
- **Giải pháp**: Lưu ảnh vào thư mục hệ thống (`uploads/`) và chỉ lưu đường dẫn (path) vào MySQL.
- **Thư viện**: Sử dụng `FastAPI.UploadFile` để xử lý file tải lên hiệu quả.

## 2. Nhập dữ liệu từ Excel
- **Thư viện**: `Pandas` kết hợp với `openpyxl`.
- **Kỹ thuật**: 
    - Sử dụng `BackgroundTasks` của FastAPI để xử lý việc đọc Excel nhằm tránh chặn (block) luồng chính của API.
    - Sử dụng `bulk_insert_mappings` của SQLAlchemy để tăng tốc độ ghi dữ liệu vào database.

## 3. Kiến trúc Backend
- **Framework**: FastAPI (Async).
- **ORM**: SQLAlchemy 2.0 với `AsyncSession`.
- **Validation**: Pydantic v2 cho dữ liệu đầu vào/đầu ra.
- **Migration**: Sử dụng `Alembic` để quản lý các thay đổi schema database (tùy chọn nhưng khuyến nghị).

## 4. Bảo mật
- Kiểm tra loại file (MIME type) khi upload ảnh.
- Giới hạn kích thước file upload.

## 5. Cấu trúc thư mục đề xuất
- `app/models/`: Định nghĩa các bảng database.
- `app/schemas/`: Định nghĩa Pydantic models.
- `app/api/`: Các endpoint của hệ thống.
- `app/core/`: Cấu hình database, cài đặt chung.
- `app/services/`: Logic xử lý nghiệp vụ (Excel, Image processing).
