# HƯỚNG DẪN SỬ DỤNG HỆ THỐNG QUÉT TIÊU BẢN TỰ ĐỘNG LIÊN TỤC

## 🎯 TỔNG QUAN

Hệ thống này cho phép bạn **CHỤP ẢNH TIÊU BẢN LIÊN TỤC** một cách tự động khi di chuyển bàn mẫu, **KHÔNG CẦN** phải nhấn nút chụp mỗi lần!

### Tính năng chính:

✅ **Motion Detection** - Tự động phát hiện khi bàn mẫu di chuyển  
✅ **Auto Capture** - Tự động chụp ảnh khi di chuyển đủ xa  
✅ **Position Tracking** - Tính toán tọa độ chính xác bằng feature matching  
✅ **Multi-Level Generation** - Tự động tạo các level L00-L07 như LandingMed  
✅ **Real-time Preview** - Hiển thị trạng thái quét trực tiếp  

---

## 🚀 CÁCH SỬ DỤNG

### Bước 1: Chạy chương trình

```bash
py auto_scan_continuous.py
```

Hoặc với tham số tùy chỉnh:

```bash
# camera_id tile_size overlap output_dir
py auto_scan_continuous.py 0 1024 0.1 scan_output
```

### Bước 2: Chuẩn bị

1. **Đặt tiêu bản** lên bàn kính
2. **Điều chỉnh focus** để ảnh rõ nét
3. **Di chuyển về góc** của vùng cần quét

### Bước 3: Bắt đầu quét

1. Nhấn phím **S** (Start) để bắt đầu quét
2. **Di chuyển bàn mẫu từ từ và đều đặn**:
   - Bắt đầu từ góc trên-trái
   - Di chuyển sang phải (theo hàng ngang)
   - Khi hết hàng, xuống hàng dưới
   - Tiếp tục cho đến khi quét hết vùng

### Bước 4: Hệ thống tự động

Khi bạn di chuyển bàn mẫu:

🔄 **Hệ thống tự động**:
- Phát hiện chuyển động qua feature matching
- Tính toán tọa độ chính xác
- **Tự động chụp ảnh** khi di chuyển đủ xa (theo overlap đã cài đặt)
- Hiển thị thông tin real-time trên màn hình

❌ **BẠN KHÔNG CẦN**:
- Nhấn nút chụp mỗi lần
- Tính toán tọa độ thủ công
- Lo lắng về overlap
- Đếm số tiles đã chụp

### Bước 5: Tạm dừng/Tiếp tục

- Nhấn **P** (Pause) để tạm dừng
- Nhấn **S** (Start) để tiếp tục

### Bước 6: Tạo Multi-Levels

Sau khi quét xong:

1. Nhấn **P** để tạm dừng
2. Nhấn **G** (Generate) để tạo các levels L01-L07
3. Đợi hệ thống xử lý (1-5 phút tùy số lượng tiles)

### Bước 7: Kết thúc

- Nhấn **Q** (Quit) để kết thúc
- Hệ thống tự động lưu `BlocksJson.json`

---

## 📊 CÁC PHÍM ĐIỀU KHIỂN

| Phím | Chức năng | Mô tả |
|------|-----------|-------|
| **S** | Start | Bắt đầu quét tự động |
| **P** | Pause | Tạm dừng quét |
| **R** | Reset | Bắt đầu lại từ đầu |
| **G** | Generate Levels | Tạo các levels L01-L07 từ L00 |
| **Q** | Quit | Kết thúc và lưu metadata |

---

## 💡 NGUYÊN LÝ HOẠT ĐỘNG

### 1. Motion Detection (Phát hiện chuyển động)

```
Frame hiện tại ──┐
                 ├──> Feature Matching ──> Tính dx, dy
Frame trước    ──┘
```

Hệ thống sử dụng **ORB (Oriented FAST and Rotated BRIEF)** để:
- Phát hiện keypoints trên 2 frames liên tiếp
- Tính toán vector di chuyển
- Loại bỏ outliers bằng median

### 2. Auto Capture (Tự động chụp)

```
Nếu sqrt(dx² + dy²) >= step_size:
    ├─> Chụp tile
    ├─> Lưu ảnh
    ├─> Cập nhật tọa độ
    └─> Reset accumulator
```

**step_size** = tile_size × (1 - overlap_percent)

Ví dụ: tile_size=1024, overlap=10% → step_size=922 pixels

### 3. Position Tracking (Theo dõi vị trí)

```
Tọa độ toàn cục:
- current_x += dx (mỗi frame)
- current_y += dy (mỗi frame)

Row = current_y / step_size
Col = current_x / step_size
```

### 4. Multi-Level Generation

```
Level 0 (L00): Full resolution (1024x1024 tiles)
     ↓ (resize 1/2)
Level 1 (L01): Downscale 2x
     ↓ (resize 1/2)
Level 2 (L02): Downscale 4x
     ↓ ...
Level 7 (L07): Downscale 128x (thumbnail)
```

---

## 📁 CẤU TRÚC DỮ LIỆU

Sau khi chạy xong, bạn sẽ có:

```
scan_output/
├── Blocks/
│   ├── L00/  (Full resolution)
│   │   ├── B0000000C.jpg
│   │   ├── B0000001C.jpg
│   │   └── ...
│   ├── L01/  (Downscale 2x)
│   │   ├── B1000000C.jpg
│   │   └── ...
│   ├── L02/  (Downscale 4x)
│   ├── L03/  (Downscale 8x)
│   ├── L04/  (Downscale 16x)
│   ├── L05/  (Downscale 32x)
│   ├── L06/  (Downscale 64x)
│   └── L07/  (Downscale 128x - thumbnail)
└── Data/
    └── BlocksJson.json  (Metadata)
```

**File `BlocksJson.json`** có cấu trúc **HOÀN TOÀN GIỐNG** LandingMed!

---

## ⚙️ TÙY CHỈNH THAM SỐ

### Thay đổi tile size:

```bash
# Tile 512x512 (nhỏ hơn, chi tiết hơn)
py auto_scan_continuous.py 0 512 0.1

# Tile 2048x2048 (lớn hơn, ít tiles hơn)
py auto_scan_continuous.py 0 2048 0.1
```

### Thay đổi overlap:

```bash
# Overlap 20% (nhiều overlap hơn, an toàn hơn)
py auto_scan_continuous.py 0 1024 0.2

# Overlap 5% (ít overlap, nhanh hơn nhưng rủi ro cao)
py auto_scan_continuous.py 0 1024 0.05
```

**Khuyến nghị**: Overlap 10-15% là tối ưu

### Thay đổi output directory:

```bash
py auto_scan_continuous.py 0 1024 0.1 my_scan_folder
```

---

## 🔧 SAU KHI QUÉT XONG

### Ghép ảnh:

Sử dụng code ghép ảnh cũ của bạn!

```bash
# Chỉnh sửa đường dẫn trong stitch_landingmed_final.py
# base_path = "scan_output"

py stitch_landingmed_final.py 1
```

Hoặc tạo script ghép nhanh:

```python
import os
os.system('py stitch_landingmed_final.py 1')
```

---

## 💪 TỐI ƯU HIỆU SUẤT

### 1. Tốc độ di chuyển

**Quá nhanh** → Hệ thống không kịp phát hiện  
**Quá chậm** → Tốn thời gian

**Tốc độ lý tưởng**: Di chuyển đều đặn, ~2-3 giây/tile

### 2. Độ sáng và focus

- ✅ Ánh sáng đủ, đồng đều
- ✅ Focus rõ nét
- ❌ Tránh quá tối hoặc quá sáng
- ❌ Tránh blur

Nếu ảnh không rõ → Feature matching thất bại → Không tự động chụp được!

### 3. Pattern di chuyển

**Tốt nhất**: Zigzag pattern (giống rắn)

```
Row 0: →→→→→→  (Trái sang phải)
          ↓
Row 1: ←←←←←←  (Phải sang trái)
          ↓
Row 2: →→→→→→  (Trái sang phải)
```

**Tránh**: Di chuyển lung tung, nhảy cóc

### 4. Hiệu suất xử lý

Hệ thống sử dụng **ORB** (nhanh, real-time):
- ~30-60 FPS trên máy i5
- Tự động chụp không lag
- Multi-level generation: 1-5 phút cho 200-500 tiles

---

## ⚠️ XỬ LÝ LỖI

### Lỗi: "Không phát hiện chuyển động"

**Nguyên nhân**: Ảnh quá đơn điệu (không có texture)  
**Giải pháp**: 
- Tăng độ phóng đại để thấy chi tiết
- Điều chỉnh focus

### Lỗi: "Chụp quá nhiều tiles ở cùng vị trí"

**Nguyên nhân**: Overlap quá lớn hoặc di chuyển quá chậm  
**Giải pháp**: 
- Giảm overlap xuống 0.05-0.1
- Di chuyển nhanh hơn một chút

### Lỗi: "Có khoảng trống giữa các tiles"

**Nguyên nhân**: Overlap quá nhỏ hoặc di chuyển quá nhanh  
**Giải pháp**: 
- Tăng overlap lên 0.15-0.2
- Di chuyển chậm và đều đặn hơn

### Lỗi: "Memory Error khi generate levels"

**Nguyên nhân**: Quá nhiều tiles, RAM không đủ  
**Giải pháp**: 
- Đóng các ứng dụng khác
- Nếu vẫn lỗi, comment dòng tạo canvas trong `generate_lower_levels()`
- Generate từng level một

---

## 📈 ƯỚC TÍNH THỜI GIAN

Ví dụ: Quét vùng 20mm × 30mm

| Thông số | Giá trị |
|----------|---------|
| Tile size | 1024×1024 |
| Overlap | 10% |
| Step size | ~920 pixels |
| Số tiles dọc | ~22 |
| Số tiles ngang | ~33 |
| **Tổng tiles** | **~726 tiles** |
| Tốc độ | ~3s/tile |
| **Thời gian quét** | **~35 phút** |
| Generate levels | ~3 phút |
| **Tổng thời gian** | **~38 phút** |

---

## 🎓 SO SÁNH VỚI PHƯƠNG PHÁP CŨ

| Tiêu chí | Phương pháp cũ (Manual) | Phương pháp mới (Auto) |
|----------|-------------------------|------------------------|
| **Chụp ảnh** | Nhấn SPACE mỗi lần| ✅ Tự động |
| **Tính tọa độ** | Tự đếm Row/Col | ✅ Tự động |
| **Overlap** | Phụ thuộc con người | ✅ Chính xác 10% |
| **Tốc độ** | Chậm (~5s/tile) | ✅ Nhanh (~3s/tile) |
| **Độ chính xác** | Phụ thuộc kỹ năng | ✅ Cao (feature matching) |
| **Dễ sử dụng** | Khó, cần tập trung | ✅ Dễ, chỉ di chuyển |
| **Multi-level** | Phải tạo thủ công | ✅ Tự động |
| **Tương thích** | Custom format | ✅ Giống LandingMed 100% |

---

## 🔗 TÀI LIỆU THAM KHẢO

- `auto_scan_continuous.py` - Source code hệ thống
- `stitch_landingmed_final.py` - Ghép ảnh từ metadata
- `BaoCao.md` - Báo cáo kỹ thuật chi tiết

---

## ❓ FAQ

**Q: Tôi có thể dùng với bất kỳ camera nào không?**  
A: Có! Miễn là camera hỗ trợ DirectShow (hầu hết camera USB).

**Q: Nếu tôi di chuyển bàn mẫu quá nhanh thì sao?**  
A: Hệ thống sẽ không kịp phát hiện motion. Hãy di chuyển chậm và đều đặn.

**Q: Tôi có thể tạm dừng giữa chừng không?**  
A: Có! Nhấn P để pause, sau đó nhấn S để tiếp tục.

**Q: File BlocksJson.json có giống LandingMed không?**  
A: Hoàn toàn giống! Bạn dùng code ghép ảnh cũ 100%.

**Q: Tôi có thể xem ảnh đã quét chưa?**  
A: Có! Kiểm tra trong thư mục `scan_output/Blocks/L00/` hoặc dùng code ghép ảnh.

**Q: Hệ thống có hoạt động với mẫu không có texture không?**  
A: Khó. Cần có đủ chi tiết để feature matching hoạt động. Nếu mẫu quá đơn điệu, hãy zoom vào để thấy texture.

---

**Ngày tạo**: 04/12/2025  
**Người viết**: Châu Huy Diễn  
**Phiên bản**: 1.0
