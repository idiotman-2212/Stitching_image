# 🔬 Hardware Setup Guide - Manual Slide Scanner

## 📋 Thiết bị dự kiến

### 1. Camera Kính Hiển Vi
**Euromex DC.5000F** (Hà Lan)
- Kết nối USB với máy tính
- Độ phân giải cao
- Hỗ trợ live streaming
- Tương thích với Windows/Mac/Linux

**Nhà cung cấp**: Công ty TNHH Thiết Bị Song Long
- Địa chỉ: Tòa nhà Tân Kỷ Nguyên, lầu 4, 43 Tản Đà, P.10, Q.5, TP.HCM
- Hotline: 0908.285.230 (Zalo) - 0902.802.330 (Zalo)
- Website: https://songlongvn.com

### 2. Phần mềm tham khảo
**PROMICRA PRO-SCAN** - Manual Whole Slide Scanning
- Website: https://promicra.com/manual-slide-scanning/
- Tính năng: Real-time stitching, focus detection, grid guide
- Tương thích: PROMICAM cameras

**ToupTek Photonics** - Scientific Cameras
- Website: https://www.touptekphotonics.com
- Sản phẩm: Microscopy cameras, HDMI cameras, USB3 cameras
- SDK: Hỗ trợ Python, C++, .NET

---

## 🔌 Tích hợp Camera vào Dự án

### Bước 1: Cài đặt Driver Camera

#### Cho Euromex DC.5000F:
1. Download driver từ nhà sản xuất
2. Cài đặt theo hướng dẫn
3. Kiểm tra camera xuất hiện trong Device Manager

#### Kiểm tra camera:
```python
import cv2

# List all available cameras
for i in range(10):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera {i}: Available")
        ret, frame = cap.read()
        if ret:
            print(f"  Resolution: {frame.shape[1]}x{frame.shape[0]}")
        cap.release()
    else:
        break
```

### Bước 2: Cấu hình Camera trong Code

Cập nhật `camera_capture.py`:

```python
class Camera:
    def __init__(self, source=0, resolution=(1920, 1080)):
        """
        Initialize camera
        
        Args:
            source: Camera index (0, 1, 2...) or folder path
            resolution: Desired resolution (width, height)
        """
        self.source = source
        self.resolution = resolution
        
        # Camera settings for Euromex DC.5000F
        self.camera_settings = {
            'brightness': 128,      # 0-255
            'contrast': 128,        # 0-255
            'saturation': 128,      # 0-255
            'exposure': -6,         # Auto exposure
            'gain': 0,              # Auto gain
            'white_balance': 4000,  # Kelvin
        }
```

### Bước 3: Tối ưu cho Real-time Scanning

Tạo file `realtime_camera.py`:

```python
import cv2
import numpy as np
import time

class RealtimeMicroscopeCamera:
    """
    Real-time camera handler for microscope scanning
    Optimized for Euromex DC.5000F and similar USB cameras
    """
    
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self.is_running = False
        
        # Performance settings
        self.target_fps = 30
        self.buffer_size = 1  # Minimize latency
        
    def start(self):
        """Initialize and start camera"""
        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)  # DirectShow for Windows
        
        if not self.cap.isOpened():
            raise Exception(f"Cannot open camera {self.camera_index}")
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, self.buffer_size)
        
        # Auto settings
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # Disable autofocus for microscope
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Manual exposure
        
        self.is_running = True
        print(f"[Camera] Started: {self.get_resolution()}")
        
    def get_frame(self):
        """Capture a single frame"""
        if not self.is_running:
            return None
            
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None
    
    def get_resolution(self):
        """Get current camera resolution"""
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (width, height)
    
    def set_exposure(self, value):
        """Set exposure (-13 to -1, or 0 for auto)"""
        self.cap.set(cv2.CAP_PROP_EXPOSURE, value)
    
    def set_brightness(self, value):
        """Set brightness (0-255)"""
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, value)
    
    def set_contrast(self, value):
        """Set contrast (0-255)"""
        self.cap.set(cv2.CAP_PROP_CONTRAST, value)
    
    def release(self):
        """Release camera resources"""
        if self.cap:
            self.cap.release()
        self.is_running = False
        print("[Camera] Released")


# Test camera
if __name__ == "__main__":
    camera = RealtimeMicroscopeCamera(0)
    camera.start()
    
    print("Press 'q' to quit, 's' to save frame")
    
    while True:
        frame = camera.get_frame()
        if frame is not None:
            cv2.imshow("Microscope Camera", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            cv2.imwrite(f"capture_{int(time.time())}.jpg", frame)
            print("Frame saved!")
    
    camera.release()
    cv2.destroyAllWindows()
```

---

## 🎯 Workflow với Hardware Thật

### 1. Setup Microscope
```
1. Đặt slide lên bàn kính hiển vi
2. Điều chỉnh focus cho rõ nét
3. Cài đặt độ phóng đại phù hợp
4. Đảm bảo ánh sáng đều
```

### 2. Chạy Real-time Scanner
```bash
# Test camera trước
py realtime_camera.py

# Chạy scanner
py main_headless.py
```

### 3. Manual Scanning Process
```
1. Bắt đầu từ góc trên-trái của slide
2. Di chuyển bàn kính từ trái sang phải
3. Khi hết hàng, xuống dưới và quay lại trái
4. Lặp lại cho đến khi quét hết vùng cần thiết
5. Đảm bảo overlap 30-50% giữa các frame
```

---

## ⚙️ Cấu hình Tối ưu

### Camera Settings
```python
# Trong main_headless.py
CAMERA_INDEX = 0  # Thường là 0, kiểm tra với realtime_camera.py
RESOLUTION = (1920, 1080)  # Full HD
EXPOSURE = -6  # Điều chỉnh theo điều kiện ánh sáng
BRIGHTNESS = 128
CONTRAST = 128
```

### Stitching Settings
```python
# Overlap giữa các ảnh
OVERLAP_PERCENTAGE = 40  # 30-50% recommended

# Số lượng features để detect
NUM_FEATURES = 5000

# Confidence threshold
CONFIDENCE_THRESHOLD = 0.5
```

---

## 🔧 Troubleshooting

### Camera không nhận diện
```bash
# Kiểm tra device
py -c "import cv2; print(cv2.getBuildInformation())"

# List cameras
py realtime_camera.py
```

### Ảnh bị mờ/tối
- Điều chỉnh exposure: `camera.set_exposure(-4)`
- Tăng brightness: `camera.set_brightness(150)`
- Kiểm tra ánh sáng kính hiển vi

### Stitching thất bại
- Tăng overlap lên 50%
- Giảm tốc độ di chuyển slide
- Đảm bảo focus ổn định
- Kiểm tra ánh sáng đều

---

## 📊 Performance Expectations

### Với Euromex DC.5000F (1920x1080)
- **Capture FPS**: 30 fps
- **Stitching time**: ~5-10s per frame pair
- **Total scan time**: 5-15 phút (tùy kích thước slide)
- **Output resolution**: 5000-15000 pixels (tùy số lượng tiles)

### Recommended Workflow
1. **Quick scan** (10x magnification): Toàn bộ slide, low resolution
2. **Detailed scan** (40x magnification): Vùng quan tâm, high resolution
3. **Comparison**: So sánh với reference image

---

## 🎓 Best Practices

### 1. Chuẩn bị Slide
- Làm sạch slide trước khi quét
- Đảm bảo coverslip không bị bong bóng khí
- Kiểm tra mẫu không bị dịch chuyển

### 2. Thiết lập Microscope
- Sử dụng Köhler illumination
- Điều chỉnh diaphragm cho ánh sáng đều
- Lock focus nếu có thể

### 3. Scanning Technique
- Di chuyển chậm và đều
- Giữ tốc độ ổn định
- Theo pattern có hệ thống (snake pattern)
- Pause nếu cần điều chỉnh focus

### 4. Quality Control
- Kiểm tra preview sau mỗi hàng
- Quét lại vùng có vấn đề
- Lưu checkpoint thường xuyên

---

## 📞 Support & Resources

### Nhà cung cấp Camera
**Song Long Equipment Co., Ltd**
- Hotline: 0908.285.230 / 0902.802.330
- Email: sales@songlongvn.com
- Website: https://songlongvn.com

### Technical Documentation
- Euromex DC.5000F Catalog: [Download](https://drive.google.com/file/d/11lS41emkJYX_ENU9WDa-lLiIWSqFz5Qz/view)
- PROMICRA Manual: https://promicra.com/manual-slide-scanning/
- ToupTek SDK: https://www.touptekphotonics.com

### Software Support
- OpenCV Documentation: https://docs.opencv.org
- Python Camera Guide: https://pyimagesearch.com

---

**Version**: 1.0  
**Last Updated**: 2025-11-25  
**Status**: Ready for Hardware Integration ✅
