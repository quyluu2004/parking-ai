import cv2
import threading
import time
import os
import numpy as np
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/camera", tags=["Camera"])
CAMERA_SOURCE = os.getenv("CAMERA_SOURCE", "0")

class CameraManager:
    _cap = None
    _frame = None
    _lock = threading.Lock()
    _is_running = False
    _thread = None
    _status = "STILL" # STILL, RUNNING, ERROR

    @classmethod
    def get_capture_source(cls):
        if CAMERA_SOURCE.isdigit():
            return int(CAMERA_SOURCE)
        return CAMERA_SOURCE

    @classmethod
    def _capture_loop(cls):
        print("[*] Luồng đọc Camera đã khởi động.")
        while cls._is_running:
            if cls._cap is None or not cls._cap.isOpened():
                source = cls.get_capture_source()
                # Thử các backend phổ biến nhất trước
                backends = [cv2.CAP_DSHOW, None, cv2.CAP_MSMF]
                found = False
                
                for backend in backends:
                    if found or not cls._is_running: break
                    indices = [source] + [i for i in range(5) if i != source]
                    for i in indices:
                        if not cls._is_running: break
                        try:
                            print(f"[*] Thử Camera {i} với {backend}...")
                            cap = cv2.VideoCapture(i, backend) if backend is not None else cv2.VideoCapture(i)
                            if cap.isOpened():
                                # Chờ một chút để camera ổn định
                                time.sleep(0.5)
                                ret, _ = cap.read()
                                if ret:
                                    cls._cap = cap
                                    cls._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                                    cls._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                                    cls._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                                    found = True
                                    print(f"[+] Đã kết nối Camera {i}")
                                    break
                                cap.release()
                        except Exception as e:
                            print(f"[!] Lỗi khi thử camera {i}: {e}")
                
                if not found:
                    time.sleep(2)
                    continue

            try:
                success, frame = cls._cap.read()
                if success:
                    with cls._lock:
                        cls._frame = frame.copy()
                else:
                    print("[!] Mất kết nối camera. Đang khởi tạo lại...")
                    if cls._cap: cls._cap.release()
                    cls._cap = None
                    time.sleep(1)
            except Exception as e:
                print(f"[!] Lỗi trong vòng lặp đọc: {e}")
                cls._cap = None
            
            time.sleep(0.01) # Tăng tốc độ đọc lên mức tối đa (~60-100fps nội bộ)

    @classmethod
    def start(cls):
        with cls._lock:
            if not cls._is_running:
                cls._is_running = True
                cls._thread = threading.Thread(target=cls._capture_loop, daemon=True)
                cls._thread.start()

    @classmethod
    def stop(cls):
        cls._is_running = False
        if cls._thread:
            cls._thread.join(timeout=1)
        if cls._cap:
            cls._cap.release()
        cls._cap = None
        cls._frame = None

    @classmethod
    def get_latest_frame(cls):
        with cls._lock:
            if cls._frame is not None:
                return cls._frame.copy()
            return None

def gen_frames():
    CameraManager.start()
    
    # Tạo một frame "Đang tải" để tránh Stream bị lỗi khi mới bật
    loading_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(loading_frame, "DANG KET NOI CAMERA...", (150, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    while True:
        frame = CameraManager.get_latest_frame()
        if frame is None:
            frame = loading_frame
            
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if ret:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        
        time.sleep(0.04) # ~25 FPS cho stream

@router.get("/stream")
async def video_stream():
    return StreamingResponse(gen_frames(), 
                            media_type='multipart/x-mixed-replace; boundary=frame')

@router.post("/reset")
async def reset_camera():
    CameraManager.stop()
    time.sleep(1)
    CameraManager.start()
    return {"status": "ok"}
