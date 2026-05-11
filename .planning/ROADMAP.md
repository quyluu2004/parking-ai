# Lộ trình phát triển (Roadmap): Hệ thống Quản lý Xe Trường học

## Cột mốc 1: MVP - Kiểm soát xe máy bằng AI
Tập trung vào giá trị cốt lõi: Nhận diện xe máy và cảnh báo cho bảo vệ.

### Giai đoạn 1: Nền tảng & Quản lý dữ liệu
- [ ] Khởi tạo Backend (Python/FastAPI) và Cơ sở dữ liệu (PostgreSQL).
- [ ] Xây dựng giao diện Admin để đăng ký Học sinh & Xe.
- [ ] Triển khai chức năng nhập dữ liệu từ file Excel.

### Giai đoạn 2: Lõi AI - Nhận diện biển số (LPR)
- [ ] Tích hợp luồng RTSP từ Camera.
- [ ] Triển khai quy trình xử lý YOLO + OCR để trích xuất biển số.
- [ ] Tối ưu hóa tốc độ xử lý cho lưu lượng xe lớn.

### Giai đoạn 3: Trạm bảo vệ & Cảnh báo thời gian thực
- [ ] Xây dựng Dashboard cho bảo vệ (Giao diện Web).
- [ ] Triển khai WebSocket để cập nhật trạng thái "Xanh/Đỏ" thời gian thực.
- [ ] Triển khai thử nghiệm trên Server cá nhân.

## Cột mốc 2: Mở rộng - Xe đạp & Báo cáo

### Giai đoạn 4: AI cho Xe đạp & Phương tiện khác
- [ ] Xây dựng mô hình AI nhận diện "thẻ số ảo" (OCR) hoặc đặc điểm xe (Re-ID).
- [ ] Cấu hình luồng camera riêng cho khu vực xe đạp.
- [ ] Tích hợp nhật ký xe đạp vào bảng điều khiển chung và hệ thống thu phí.

### Giai đoạn 5: Báo cáo & Tối ưu hiệu năng
- [ ] Tạo các báo cáo thu phí tháng.
- [ ] Kiểm tra hiệu năng trong giờ cao điểm (7:00 - 7:30 sáng).
- [ ] Hoàn thiện hệ thống và thiết lập quy trình sao lưu dữ liệu.

---

## Đề xuất phần cứng (Hardware Proposal)
- **Camera**: 
    - 2x Camera IP 2MP/4MP hỗ trợ Global Shutter (chuyên dụng cho nhận diện biển số).
    - 1x Camera góc rộng (giám sát tổng thể).
    - 1x Camera tập trung khu vực xe đạp (nhận diện thẻ số/Re-ID).
- **Server**: 
    - Máy tính cấu hình tối thiểu Intel i5/i7 (thế hệ 12+) hoặc AMD Ryzen 5+.
    - **Card đồ họa NVIDIA** (RTX 3060 hoặc tốt hơn) là rất quan trọng để chạy AI mượt mà.
    - 16GB RAM, 512GB SSD.
