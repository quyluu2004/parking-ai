# PLAN: Giai đoạn 4 - Smart Trigger & Hiệu năng

Tối ưu hóa luồng nhận diện theo 4 bước logic của người dùng: Quan sát im lặng -> Kích hoạt vật thể -> Đọc & Gửi 1 lần -> Reset.

## 1. Mục tiêu
- Loại bỏ việc quét rập khuôn mỗi 2 giây.
- Tiết kiệm tài nguyên server (chỉ chạy OCR khi cần).
- Tránh thông báo lặp lại cho cùng một chiếc xe.

## 2. Các bước thực hiện

### Bước 1: Trạng thái quan sát im lặng (Frontend)
- **File**: `frontend/app.js`
- **Nội dung**: 
    - Tăng tần suất chụp frame lên (ví dụ: 1000ms) để nhạy bén hơn.
    - Triển khai thuật toán **Motion Detection** đơn giản (so sánh pixel giữa 2 frame).
    - Chỉ gọi API `/ai/detect` khi phát hiện có sự thay đổi lớn trong khung hình.

### Bước 2: Kích hoạt khi có vật thể (Backend)
- **File**: `ai/detect.py`
- **Nội dung**:
    - Phân tách quá trình: Chạy YOLO trước để tìm `motorcycle` hoặc `license_plate`.
    - Nếu không tìm thấy vật thể mục tiêu, trả về ngay lập tức kết quả trống (không chạy OCR).
    - OCR chỉ được kích hoạt khi YOLO xác nhận có vùng chứa biển số.

### Bước 3: Đọc và Gửi tín hiệu MỘT LẦN (Frontend/Backend)
- **File**: `frontend/app.js`
- **Nội dung**:
    - Sử dụng một biến `activePlate` để lưu biển số đang được nhận diện.
    - Chỉ cập nhật giao diện và âm thanh thông báo khi `biển số mới != activePlate`.
    - Nếu biển số giống nhau, chỉ cập nhật vị trí khung xanh (bbox) mà không gửi tín hiệu xác thực lại.

### Bước 4: Reset trạng thái (Frontend)
- **File**: `frontend/app.js`
- **Nội dung**:
    - Nếu trong 3 lần quét liên tiếp không thấy biển số nào, đặt `activePlate = null`.
    - Quay lại trạng thái "Quan sát im lặng".

## 3. Kiểm tra & Xác nhận (UAT)
- [ ] Màn hình "Đang chờ" không được nháy xanh/đỏ liên tục khi không có xe.
- [ ] Khi đưa xe vào, khung xanh hiện lên ngay lập tức (< 1s).
- [ ] Thông tin chủ xe chỉ hiện lên 1 lần, không bị nháy lại.
- [ ] Khi rút xe ra, màn hình quay về trạng thái "Đang chờ" sau tối đa 2 giây.

## 4. Rủi ro & Giải pháp
- **Rủi ro**: Motion detection quá nhạy (lá cây rung, ánh sáng thay đổi).
- **Giải pháp**: Điều chỉnh ngưỡng (threshold) thay đổi pixel và chỉ tập trung vào vùng trung tâm khung hình.
