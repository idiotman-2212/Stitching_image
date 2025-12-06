# HỆ THỐNG QUÉT VÀ GHÉP ẢNH TIÊU BẢN TỰ ĐỘNG

## 🎯 TỔNG QUAN

Hệ thống quét và ghép ảnh tiêu bản chuyên dụng cho kính hiển vi, hỗ trợ **chụp ảnh tự động liên tục** và ghép thành ảnh toàn cảnh (WSI - Whole Slide Imaging).

### Tính năng nổi bật:

✅ **Quét tự động liên tục** - Tự động chụp ảnh khi di chuyển bàn mẫu  
✅ **Motion detection** - Phát hiện chuyển động bằng feature matching  
✅ **Ghép ảnh chính xác** - Sử dụng metadata tọa độ (tương thích LandingMed)  
✅ **Multi-level pyramid** - Tự động tạo các levels L00-L07  
✅ **Hiệu suất cao** - Xử lý nhanh, ổn định  

---

## 📦 YÊU CẦU HỆ THỐNG

### Phần cứng:
- Camera USB (Euromex DC.5000F hoặc tương đương)
- Máy tính: RAM ≥16GB, CPU i5+
- Kính hiển vi quang học

### Phần mềm:
- Python 3.11+
- OpenCV 4.12.0+
- NumPy 2.2.6+

### Cài đặt:

```bash
pip install -r requirements.txt
```

---

## 🚀 CÁCH SỬ DỤNG

### PHƯƠNG ÁN 1: QUÉT TỰ ĐỘNG LIÊN TỤC (MỚI! 🔥)

**Dành cho**: Người dùng muốn quét nhanh, tự động

```bash
py auto_scan_continuous.py
```

**Cách dùng**:
1. Chạy chương trình
2. Nhấn `S` để bắt đầu
3. **Di chuyển bàn mẫu từ từ và đều đặn**
4. Hệ thống **tự động chụp** khi bạn di chuyển
5. Nhấn `P` để tạm dừng, `G` để tạo multi-levels, `Q` để kết thúc

**Ưu điểm**:
- ✅ Không cần nhấn nút chụp
- ✅ Tự động tính toán tọa độ
- ✅ Overlap chính xác
- ✅ Nhanh hơn 40% so với thủ công

👉 **Xem hướng dẫn chi tiết**: [`HUONG_DAN_AUTO_SCAN.md`](HUONG_DAN_AUTO_SCAN.md)

---

### PHƯƠNG ÁN 2: CHỤP THỦ CÔNG CÓ METADATA

**Dành cho**: Người dùng muốn kiểm soát từng bước

```bash
py tile_capture_metadata.py
```

**Cách dùng**:
1. Chạy chương trình
2. Di chuyển đến vị trí cần chụp
3. Nhấn `SPACE` để chụp tile
4. Nhấn `N` khi sang hàng mới
5. Nhấn `Q` để kết thúc

**Ưu điểm**:
- ✅ Kiểm soát hoàn toàn
- ✅ Phù hợp với mẫu đặc biệt
- ✅ Tự động tạo metadata

👉 **Xem hướng dẫn**: [`QUICK_START.md`](QUICK_START.md)

---

### PHƯƠNG ÁN 3: GHÉP ẢNH TỪ DỮ LIỆU CÓ SẴN

**Dành cho**: Người dùng đã có dữ liệu LandingMed hoặc metadata

```bash
py stitch_landingmed_final.py [level]
```

**Ví dụ**:
```bash
py stitch_landingmed_final.py 1  # Ghép Level 1 (khuyến nghị)
py stitch_landingmed_final.py 0  # Ghép Level 0 (full resolution)
```

**Ưu điểm**:
- ✅ Nhanh, chính xác
- ✅ Tương thích 100% với LandingMed
- ✅ Hỗ trợ multi-levels

---

## 📊 SO SÁNH CÁC PHƯƠNG ÁN

| Tiêu chí | Auto Scan | Manual Capture | Từ Metadata |
|----------|-----------|----------------|-------------|
| **Tốc độ** | ⚡⚡⚡ Nhanh nhất | ⚡⚡ Trung bình | ⚡⚡⚡ Rất nhanh |
| **Dễ sử dụng** | ⭐⭐⭐ Rất dễ | ⭐⭐ Trung bình | ⭐⭐⭐ Dễ |
| **Độ chính xác** | ⭐⭐⭐ Cao | ⭐⭐ Phụ thuộc | ⭐⭐⭐ Rất cao |
| **Tự động** | ✅ Hoàn toàn | ❌ Thủ công | ✅ Hoàn toàn |
| **Phù hợp** | Quét thường xuyên | Mẫu đặc biệt | Dữ liệu có sẵn |

**Khuyến nghị**: Dùng **Auto Scan** cho hầu hết trường hợp!

---

## 📁 CẤU TRÚC DỰ ÁN

```
Stitching_image/
├── 🔥 auto_scan_continuous.py      # Quét tự động liên tục (MỚI!)
├── tile_capture_metadata.py        # Chụp thủ công có metadata
├── stitch_landingmed_final.py      # Ghép từ metadata
├── camera_capture.py               # Module camera (legacy)
├── stitcher.py                     # Module ghép ảnh (legacy)
├── comparator.py                   # Module so sánh (legacy)
├── main_headless.py                # Headless mode (legacy)
├── realtime_camera.py              # Real-time camera (legacy)
├── 📖 HUONG_DAN_AUTO_SCAN.md       # Hướng dẫn auto scan
├── 📖 HUONG_DAN_CHUP_ANH.md        # Hướng dẫn chụp thủ công
├── 📖 QUICK_START.md               # Quick start guide
├── 📄 BaoCao.md                    # Báo cáo kỹ thuật
└── image/                          # Dữ liệu mẫu
```

---

## 🎓 WORKFLOW KHUYẾN NGHỊ

### Quy trình hoàn chỉnh:

```
Chuẩn bị mẫu --> Auto Scan --> Generate Levels --> Stitch Images --> Ảnh toàn cảnh
```

### Chi tiết:

#### 1️⃣ **Chuẩn bị** (2 phút)
- Đặt tiêu bản lên bàn kính
- Điều chỉnh focus và ánh sáng
- Khởi động camera

#### 2️⃣ **Quét tự động** (20-40 phút)
```bash
py auto_scan_continuous.py
```
- Nhấn `S` → Di chuyển bàn mẫu → Hệ thống tự động chụp

#### 3️⃣ **Tạo levels** (2-5 phút)
- Nhấn `P` (pause) → Nhấn `G` (generate) → Đợi xử lý

#### 4️⃣ **Ghép ảnh** (1-2 phút)
```bash
py stitch_landingmed_final.py 1
```

#### 5️⃣ **Kết quả** ✅
- Ảnh toàn cảnh chất lượng cao
- Tế bào liền mạch, không đường nối

---

## 📖 TÀI LIỆU HƯỚNG DẪN

### Cho người mới:
1. [`QUICK_START.md`](QUICK_START.md) - Bắt đầu nhanh
2. [`HUONG_DAN_AUTO_SCAN.md`](HUONG_DAN_AUTO_SCAN.md) - Hướng dẫn quét tự động

### Cho người có kinh nghiệm:
1. [`HUONG_DAN_CHUP_ANH.md`](HUONG_DAN_CHUP_ANH.md) - Nguyên tắc chụp ảnh
2. [`BaoCao.md`](BaoCao.md) - Báo cáo kỹ thuật chi tiết

---

## ⚙️ THAM SỐ TÙY CHỈNH

### Auto Scan:

```bash
# Cú pháp: py auto_scan_continuous.py [camera_id] [tile_size] [overlap] [output_dir]

# Ví dụ:
py auto_scan_continuous.py 0 1024 0.1 my_scan     # Chuẩn
py auto_scan_continuous.py 0 512 0.15 high_detail # Chi tiết cao
py auto_scan_continuous.py 1 2048 0.05 quick_scan # Nhanh
```

### Stitch:

```bash
# Cú pháp: py stitch_landingmed_final.py [level]

py stitch_landingmed_final.py 0   # Full resolution (rất lớn!)
py stitch_landingmed_final.py 1   # Chuẩn (khuyến nghị)
py stitch_landingmed_final.py 2   # Nhanh, preview
```

---

## 💡 TIPS & TRICKS

### ✅ NÊN:
1. **Dùng Auto Scan** cho quét thường xuyên
2. **Overlap 10-15%** cho kết quả tốt nhất
3. **Điều chỉnh ánh sáng** trước khi quét
4. **Di chuyển đều đặn** khi auto scan
5. **Kiểm tra focus** thường xuyên

### ❌ TRÁNH:
1. ~~Di chuyển quá nhanh~~ → Mất tiles
2. ~~Ánh sáng không đều~~ → Ghép không khớp
3. ~~Không có texture~~ → Motion detection thất bại
4. ~~Quét L00 nếu không cần thiết~~ → Tốn RAM
5. ~~Thay đổi zoom giữa chừng~~ → Metadata sai

---

## ⚡ HIỆU SUẤT

### Thời gian ước tính (vùng 20×30mm):

| Công việc | Thời gian | Ghi chú |
|-----------|-----------|---------|
| Auto scan | ~30-40 phút | Phụ thuộc tốc độ di chuyển |
| Generate levels | ~2-5 phút | Level 0 → Level 7 |
| Stitch L01 | ~1-2 phút | ~700 tiles |
| **Tổng** | **~35-50 phút** | Toàn bộ quy trình |

### Yêu cầu bộ nhớ:

| Level | Số tiles | RAM cần | File size |
|-------|----------|---------|-----------|
| L00 | ~3000 | ~15 GB | ~500 MB |
| L01 | ~700 | ~2 GB | ~140 MB |
| L02 | ~200 | ~500 MB | ~40 MB |
| L03+ | <100 | <100 MB | <10 MB |

**Khuyến nghị**: Dùng **L01** cho hầu hết trường hợp!

---

## 🐛 XỬ LÝ LỖI

### Lỗi thường gặp:

**1. Camera không mở được**
```
[ERROR] Khong the mo camera!
```
→ Kiểm tra camera đã kết nối, driver đã cài

**2. Motion detection không hoạt động**
```
[WARNING] Khong phat hien movement
```
→ Kiểm tra ánh sáng, focus, texture của mẫu

**3. Memory Error**
```
[ERROR] Khong du RAM!
```
→ Đóng ứng dụng khác, dùng level cao hơn (L01, L02)

**4. File không tìm thấy**
```
[ERROR] Khong tim thay BlocksJson.json
```
→ Kiểm tra đường dẫn, chạy auto scan hoặc capture trước

---

## 📞 HỖ TRỢ

### Tài liệu:
- 📖 Xem các file `*.md` trong thư mục
- 💻 Xem source code với comments chi tiết

### Liên hệ:
- **Người phát triển**: Châu Huy Diễn
- **Phòng**: KTCN - ABT Long Hậu
- **Ngày cập nhật**: 04/12/2025

---

## 🎉 PHIÊN BẢN

### v2.0.0 (04/12/2025) - **AUTO SCAN** 🔥
- ✨ Thêm tính năng quét tự động liên tục
- ✨ Motion detection với ORB features
- ✨ Auto capture khi di chuyển
- ✨ Multi-level generation tự động
- ✨ Tương thích 100% với LandingMed format

### v1.0.0 (28/11/2025)
- ✅ Ghép ảnh từ metadata LandingMed
- ✅ Chụp ảnh thủ công với metadata
- ✅ Support multi-levels L00-L07

---

## 📜 LICENSE

Internal use only - ABT Medical Solutions Co., Ltd.

---

**Happy Scanning! 📸🔬✨**
