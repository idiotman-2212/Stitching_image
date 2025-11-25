# 🎯 Quick Reference - Hardware Integration

## Khi nhận được Camera Euromex DC.5000F

### Bước 1: Cài đặt Driver
1. Kết nối camera vào cổng USB 3.0
2. Windows sẽ tự động cài driver (hoặc download từ CD đi kèm)
3. Kiểm tra trong Device Manager → Imaging Devices

### Bước 2: Test Camera
```bash
py realtime_camera.py
```

**Kết quả mong đợi:**
```
Scanning for cameras...
  Camera 0: 1920x1080
[Camera] Started successfully
  Resolution: 1920x1080
  FPS: 30
  Exposure: -6
```

### Bước 3: Điều chỉnh Settings
Trong cửa sổ preview, dùng phím:
- `+/-` : Điều chỉnh exposure (ánh sáng)
- `W/S` : Điều chỉnh brightness
- `A/D` : Điều chỉnh contrast
- `S`   : Save ảnh test
- `Q`   : Thoát

### Bước 4: Chạy Scanner
Sửa file `main_headless.py`:
```python
# Dòng 13: Đổi từ True sang False
USE_SIMULATION = False

# Dòng 28: Đổi source từ IMAGE_FOLDER sang 0
cam = Camera(source=0)  # 0 = camera index
```

Chạy:
```bash
py main_headless.py
```

---

## Workflow Thực Tế

### 1. Chuẩn bị
- [ ] Đặt slide lên kính hiển vi
- [ ] Điều chỉnh focus rõ nét
- [ ] Kiểm tra ánh sáng đều
- [ ] Test camera với `realtime_camera.py`

### 2. Scanning
- [ ] Bắt đầu từ góc trên-trái
- [ ] Di chuyển từ trái → phải (overlap 40%)
- [ ] Khi hết hàng, xuống dưới và quay lại trái
- [ ] Lặp lại cho đến hết vùng cần quét

### 3. Kiểm tra kết quả
- [ ] Xem `stitched_output.jpg`
- [ ] Kiểm tra SSIM score
- [ ] Nếu không tốt, quét lại với overlap lớn hơn

---

## Troubleshooting Nhanh

### Camera không nhận
```bash
# Kiểm tra camera có sẵn không
py -c "import cv2; print([i for i in range(10) if cv2.VideoCapture(i).isOpened()])"
```

### Ảnh quá tối
```python
# Trong realtime_camera.py, tăng exposure
camera.set_exposure(-4)  # Càng gần 0 càng sáng
camera.set_brightness(150)
```

### Ảnh quá sáng
```python
camera.set_exposure(-8)  # Càng âm càng tối
camera.set_brightness(100)
```

### Stitching thất bại
- Tăng overlap lên 50%
- Di chuyển chậm hơn
- Đảm bảo focus không đổi
- Kiểm tra ánh sáng ổn định

