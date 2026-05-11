# Kế hoạch Giai đoạn 1: Nền tảng & Quản lý dữ liệu

**Mục tiêu**: Xây dựng hệ thống backend cơ bản, cơ sở dữ liệu và chức năng quản lý học sinh/xe để sẵn sàng cho việc tích hợp AI.

## 1. Thiết lập cấu trúc Backend
- [ ] Tổ chức lại thư mục `backend/` theo kiến trúc Service-based.
- [ ] Cấu hình kết nối Database (SQLAlchemy + Pydantic settings).

## 2. Định nghĩa Mô hình dữ liệu (Models)
- [ ] Tạo file `models.py` với các bảng: `Student`, `Vehicle`, `Payment`, `AccessLog`.
- [ ] Thiết lập quan hệ (Relationship) giữa các bảng.

## 3. Chức năng Quản lý Học sinh & Xe (Admin)
- [ ] Xây dựng API CRUD (Thêm, Sửa, Xóa, Xem) cho Học sinh.
- [ ] Xây dựng API liên kết phương tiện (Xe máy/Xe đạp) với học sinh.

## 4. Xử lý nhập liệu từ Excel
- [ ] Cài đặt `pandas` và `openpyxl`.
- [ ] Xây dựng Service `excel_service.py` để đọc file Excel và đẩy dữ liệu vào Database.
- [ ] Tạo endpoint `/admin/import-excel` để upload file.

## 5. Xác minh (Verification)
- [ ] Kiểm tra việc tạo bảng trong database.
- [ ] Test thử việc nhập 10-20 dòng từ file Excel mẫu.
- [ ] Kiểm tra xem ảnh upload có được lưu đúng vào thư mục `uploads/` không.

---

**Điều kiện hoàn thành**:
- Có thể đăng ký học sinh và xe qua API.
- Có thể nhập danh sách từ Excel mà không lỗi.
- Database hiển thị đúng thông tin đã nhập.
