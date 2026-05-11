# Yêu cầu dự án: Hệ thống Quản lý Xe Trường học

## Vai trò người dùng
- **Bảo vệ**: Xem luồng camera trực tiếp và các cảnh báo xác thực tại cổng.
- **Quản trị viên (Nhân viên trường)**: Quản lý danh sách học sinh, đăng ký xe và trạng thái đóng phí.
- **Học sinh (Gián tiếp)**: Cung cấp thông tin xe và nhận tem/đăng ký gửi xe.

## Yêu cầu chức năng

### 1. Đăng ký xe (Admin)
- [ ] Admin có thể nhập danh sách học sinh (từ Excel/CSV).
- [ ] Admin có thể liên kết một hoặc nhiều biển số xe với một học sinh.
- [ ] Admin có thể đánh dấu trạng thái phí tháng là "Đã đóng" hoặc "Chưa đóng".

### 2. Nhận diện & Giám sát AI (Thời gian thực)
- [ ] Hệ thống phải bắt được biển số xe từ luồng RTSP của camera.
- [ ] Thời gian xử lý hình ảnh phải dưới 2 giây để tránh ùn tắc cổng.
- [ ] Hệ thống phải trả về kết quả "Hợp lệ" (Xanh) hoặc "Chưa đăng ký/Chưa đóng phí" (Đỏ).

### 3. Giao diện bảo vệ
- [ ] Dashboard phải hiển thị ảnh chụp nhỏ của biển số vừa nhận diện.
- [ ] Dashboard phải có âm thanh cảnh báo hoặc nháy đỏ cho các xe "Không hợp lệ".
- [ ] Bảo vệ có thể nhấn nút "Ghi đè thủ công" để cho phép xe vào trong các trường hợp đặc biệt.

### 4. Hệ thống xe đạp (Đề xuất)
- [ ] Tạo mã QR cho từng xe đạp đã đăng ký.
- [ ] Sử dụng camera đặt thấp hoặc thiết bị quét cầm tay để quét mã QR xe đạp.

## Yêu cầu phi chức năng
- **Độ tin cậy**: Hệ thống phải hoạt động ngoại tuyến (mạng nội bộ) nếu mất internet.
- **Hiệu năng**: Nhận diện AI phải xử lý tốt trong giờ cao điểm (7:00 - 7:30 sáng) với ~800 lượt xe.
- **Khả năng mở rộng**: Hỗ trợ ít nhất 2 luồng camera đồng thời.

## Ràng buộc kỹ thuật
- **Phần cứng**: Chạy trên "Server cá nhân" (Thông số CPU/GPU sẽ được xác định cụ thể).
- **Lưu trữ**: Lưu trữ nhật ký/hình ảnh trong ít nhất 30 ngày.
