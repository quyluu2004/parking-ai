# Kiến trúc hệ thống (Architecture)

## Tổng quan luồng dữ liệu
1. **Input**: Camera RTSP hoặc Upload ảnh qua `camera.py`.
2. **AI Processing**: `ai_router.py` sử dụng YOLO/EasyOCR để trích xuất biển số.
3. **Validation**: Đối soát biển số với DB `Students` & `Vehicles`.
4. **Logging**: Ghi nhận lượt ra vào vào `AccessLog` và lưu ảnh vào đĩa.
5. **Dashboard**: `app.js` fetch dữ liệu từ `/admin/dashboard-stats` để hiển thị.

## Các module chính
- `backend/main.py`: Entry point của FastAPI.
- `backend/api/camera.py`: Quản lý luồng stream và "Safe Frame".
- `backend/api/ai_router.py`: Pipeline AI xử lý ảnh.
- `backend/api/admin.py`: Các API quản lý nghiệp vụ (Học sinh, Phí, Thống kê).
- `backend/models/models.py`: Định nghĩa schema cơ sở dữ liệu.
- `frontend/app.js`: Logic điều khiển giao diện người dùng.

## Lưu trữ
- **DB**: `data/vehicle_system.db` (SQLite).
- **Logs**: `C:\Users\<User>\vehicle_ai_logs` (Ảnh chụp biển số).
