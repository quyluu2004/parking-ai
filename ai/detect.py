import cv2
import easyocr
from ultralytics import YOLO
import numpy as np
import os

class VehicleDetector:
    def __init__(self):
        # Sử dụng model nano để chạy nhanh trên CPU
        self.model = YOLO('yolov8n.pt') 
        self.ocr_detector = easyocr.Reader(['en'], gpu=False)

    def format_and_correct_plate(self, text):
        """
        Hậu xử lý văn bản OCR để sửa lỗi nhận diện sai chữ/số phổ biến
        Dựa trên cấu trúc biển số Việt Nam: XX-Y1 NNN.NN
        """
        # Xóa các ký tự lạ, chỉ giữ lại chữ, số và dấu gạch/chấm
        clean_text = "".join([c for c in text if c.isalnum() or c in "-. "])
        
        # Sửa lỗi phổ biến: 6 thành G, 0 thành D/Q... tại vị trí chữ cái
        # Giả định cấu trúc biển số xe máy: 2 số đầu - 1 chữ + 1 số
        # Ví dụ: 59-62 -> 59-G2
        
        if len(clean_text) >= 4:
            # Tách phần đầu (ví dụ 59-G2)
            parts = clean_text.split()
            first_part = parts[0]
            
            # Nếu phần đầu có dạng 2 số + gạch/khoảng cách + (chữ/số) + 1 số
            # Ta sửa ký tự thứ 4 (nếu là số 6 -> G, 0 -> D, 8 -> B...)
            new_first_part = list(first_part)
            
            # Tìm vị trí ký tự series (thường là ký tự thứ 3 hoặc 4)
            # Ví dụ: 59G2 (vị trí 2), 59-G2 (vị trí 3)
            series_idx = -1
            if len(new_first_part) >= 3:
                if new_first_part[2].isdigit() == False: # Có dấu gạch/cách ở vị trí 2
                    series_idx = 3
                else:
                    series_idx = 2
            
            if series_idx != -1 and series_idx < len(new_first_part):
                char = new_first_part[series_idx]
                mapping = {
                    '6': 'G',
                    '0': 'D',
                    '8': 'B',
                    '5': 'S',
                    '4': 'A',
                    '1': 'L'
                }
                if char in mapping:
                    print(f"[AI] Tự động sửa lỗi OCR: {char} -> {mapping[char]}")
                    new_first_part[series_idx] = mapping[char]
            
            clean_text = "".join(new_first_part)
            if len(parts) > 1:
                clean_text += " " + " ".join(parts[1:])
                
        return clean_text

    def detect_and_ocr(self, image_path):
        if not os.path.exists(image_path):
            print(f"[!] File không tồn tại: {image_path}")
            return []
        
        img = cv2.imread(image_path)
        if img is None: 
            print(f"[!] Không thể đọc ảnh: {image_path}")
            return []
        
        results = self.model(img, verbose=False)
        detections = []
        
        for r in results:
            for box in r.boxes:
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                label = self.model.names[cls_id]
                
                # CHỈ tập trung vào Xe máy và Ô tô
                if label not in ['motorcycle', 'car', 'bus', 'truck']:
                    continue

                if conf < 0.45: continue # Tăng ngưỡng để tránh nhận diện "tùm lum"
                
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                print(f"[AI] Phát hiện: {label} ({conf:.2f})")

                # Chạy OCR cho vùng ảnh này
                roi = img[y1:y2, x1:x2]
                plate_text = None
                if roi.size > 0:
                    # Phóng to vùng biển số để dễ đọc hơn
                    roi_resized = cv2.resize(roi, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                    ocr_res = self.ocr_detector.readtext(roi_resized, detail=0)
                    if ocr_res:
                        # Ghép các dòng lại và xử lý hậu kỳ
                        raw_text = " ".join(ocr_res).upper()
                        plate_text = self.format_and_correct_plate(raw_text)

                # CHỈ thêm vào danh sách nếu đọc được biển số
                if plate_text:
                    detections.append({
                        "bbox": [x1, y1, x2, y2],
                        "label": label,
                        "confidence": conf,
                        "license_plate": plate_text
                    })
        
        return detections
