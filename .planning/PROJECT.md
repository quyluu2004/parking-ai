# Dự án: Hệ thống Quản lý Xe Trường học (Ứng dụng AI)

## Tổng quan
Hệ thống quản lý xe thông minh dành cho trường THPT nhằm tự động hóa việc thu phí tháng và giám sát xe vào cổng cho khoảng 800 xe máy và xe đạp hàng ngày. Hệ thống sử dụng camera AI để nhận diện biển số xe (LPR) và cung cấp phản hồi xác thực thời gian thực cho bảo vệ.

## Giá trị cốt lõi
Tối ưu hóa việc thu phí gửi xe và tăng cường an ninh trường học bằng cách thay thế việc ghi chép thủ công bằng nhận diện AI tự động.

## Ngữ cảnh
- **Đối tượng**: Trường THPT.
- **Lưu lượng**: ~800 xe máy mỗi ngày.
- **Trạng thái hiện tại**: Quản lý thủ công hoặc chưa có hệ thống số hóa.
- **Hạ tầng**: Server cá nhân (tại trường), Camera IP hỗ trợ AI.

## Yêu cầu

### Đang thực hiện (Giả thuyết)
- [ ] **Nhận diện biển số AI**: Quét biển số xe máy tại cổng và đối soát với cơ sở dữ liệu.
- [ ] **Bảng điều khiển bảo vệ**: Hiển thị trạng thái "Hợp lệ" (xanh) hoặc "Cần xử lý" (đỏ) dựa trên trạng thái đăng ký.
- [ ] **Quản lý Học sinh - Xe**: Giao diện nhập liệu để liên kết học sinh với biển số xe tương ứng.
- [ ] **Quản lý phí tháng**: Theo dõi trạng thái đóng tiền và thông báo cho bảo vệ nếu xe chưa đóng phí hoặc chưa đăng ký.
- [ ] **Chiến lược quản lý xe đạp**: Triển khai định danh bằng tem mã QR cho xe đạp.
- [ ] **Ghi nhật ký thủ công**: Cho phép bảo vệ ghi nhận các trường hợp xe khách hoặc xe mượn/hỏng.

### Ngoài phạm vi (Out of Scope)
- **Giám sát đầu ra**: Hệ thống hiện tại chưa quản lý xe lúc ra.
- **Tích hợp cổng thanh toán trực tuyến**: Phiên bản đầu tiên sẽ cập nhật trạng thái đóng tiền thủ công bởi quản trị viên.

## Các quyết định chính

| Quyết định | Lý do | Kết quả |
|----------|-----------|---------|
| Server cá nhân | Tiết kiệm chi phí và toàn quyền kiểm soát việc triển khai mô hình AI. | Tại chỗ (On-premise) |
| QR cho xe đạp | Xe đạp không có biển số; tem dán rẻ và bền cho học sinh. | Đề xuất |
| Kiến trúc Docker | Đảm bảo dễ dàng triển khai và cập nhật trên server cá nhân. | Đã lập kế hoạch |

## Công nghệ đề xuất (Proposed Tech Stack)
- **Backend**: Python (FastAPI/Flask) xử lý AI + Node.js/Spring Boot quản lý nghiệp vụ.
- **AI**: YOLOv8/v10 nhận diện biển số + OCR (Tesseract hoặc EasyOCR).
- **Frontend**: React/Vite cho Dashboard bảo vệ và Panel Admin.
- **Cơ sở dữ liệu**: PostgreSQL hoặc MySQL.
- **Phần cứng**: Camera IP chuẩn (hỗ trợ RTSP) + GPU NVIDIA (khuyến nghị).

## Sự tiến hóa
Tài liệu này sẽ tiến hóa sau mỗi giai đoạn và cột mốc của dự án.

---
*Cập nhật lần cuối: 07/05/2026 sau khi khởi tạo*
