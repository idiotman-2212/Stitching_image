# Hướng Dẫn Ghép Ảnh Từ Tiles

## Tổng Quan

Dự án này chứa các công cụ để ghép các ảnh tiles thành một ảnh hoàn chỉnh. Các ảnh được tổ chức theo cấu trúc pyramid với nhiều mức độ phân giải khác nhau (L00-L07).

## Cấu Trúc Layers

Các layer được sắp xếp theo độ phân giải từ thấp đến cao:

| Layer | Số Tiles | Grid Size | Độ Phân Giải | Mô Tả |
|-------|----------|-----------|--------------|-------|
| L07   | 1        | 1x1       | Thấp nhất    | Ảnh gốc |
| L06   | 4        | 2x2       | 2x          | |
| L05   | 9        | 3x3       | 4x          | |
| L04   | 25       | 5x5       | 8x          | |
| L03   | 81       | 9x9       | 16x         | |
| L02   | 306      | 18x17     | 32x         | |
| L01   | 1,224    | 36x34     | 64x         | Khuyến nghị |
| L00   | 4,828    | ~70x69    | 128x        | Cao nhất (rất lớn) |

## Format Tên File

Các tile có format: `B[L][RRR][CCC]C.jpg`

Trong đó:
- `B`: Prefix
- `[L]`: Layer number (0-7) - 1 ký tự hex
- `[RRR]`: Row index - 3 ký tự hex (000-FFF)
- `[CCC]`: Column index - 3 ký tự hex (000-FFF)
- `C`: Suffix
- `.jpg`: Extension

**Ví dụ:**
- `B1000000C.jpg` → Layer 1, Row 0, Col 0
- `B100000BC.jpg` → Layer 1, Row 0, Col 11 (B = 11 trong hex)
- `B1023A0FC.jpg` → Layer 1, Row 35 (0x023), Col 2575 (0xA0F)

## Cách Sử Dụng

### 1. Script Chính (Khuyến Nghị)

```bash
# Ghép layer L01 (khuyến nghị - độ phân giải cao, kích thước hợp lý)
python stitch_complete.py 1

# Ghép layer L00 (độ phân giải cao nhất - file rất lớn!)
python stitch_complete.py 0

# Ghép layer L02 (độ phân giải trung bình)
python stitch_complete.py 2
```

### 2. Kết Quả

Script sẽ tạo file output với tên: `L0[X]_stitched_complete.jpg`

**Ví dụ với L01:**
- **Input**: 1,224 tiles (mỗi tile 1024x1024)
- **Output**: 1 ảnh (34,816 x 36,864 pixels)
- **Kích thước file**: ~130 MB
- **Độ chính xác**: ~87% so với ảnh gốc L07

## Khuyến Nghị

### Layer Nên Sử Dụng

- **L01**: Tốt nhất cho hầu hết mục đích - độ phân giải cao, kích thước file hợp lý (~130 MB)
- **L02**: Nếu cần file nhỏ hơn (~30 MB) với độ phân giải trung bình
- **L00**: Chỉ khi cần độ phân giải tối đa (cảnh báo: file rất lớn >500 MB)

### Lưu Ý Kỹ Thuật

1. **Bộ nhớ**: Ghép L00 cần ~4-5 GB RAM
2. **Thời gian**: 
   - L01: ~1-2 phút
   - L00: ~5-10 phút
3. **Dung lượng đĩa**: Đảm bảo có đủ không gian trống

## Kết Quả Đã Kiểm Tra

### L01 (Đã Kiểm Tra)
- ✅ Ghép thành công 1,224/1,224 tiles (100%)
- ✅ Kích thước: 34,816 x 36,864 pixels
- ✅ Dung lượng: 132.6 MB
- ✅ Độ tương đồng với L07: 86.88%

### L06 (Đã Kiểm Tra)
- ✅ Ghép thành công 4/4 tiles (100%)
- ✅ Kích thước: 2,048 x 2,048 pixels
- ✅ Độ tương đồng với L07: 97.22%

## Cấu Trúc Thư Mục

```
Stitching_image/
├── image/
│   └── YFB-T001/
│       └── YFB-T001/
│           └── Blocks/
│               ├── L00/  (4,828 tiles)
│               ├── L01/  (1,224 tiles)
│               ├── L02/  (306 tiles)
│               ├── L03/  (81 tiles)
│               ├── L04/  (25 tiles)
│               ├── L05/  (9 tiles)
│               ├── L06/  (4 tiles)
│               └── L07/  (1 tile - ảnh gốc)
├── stitch_complete.py     # Script chính
├── stitch_final.py        # Script chi tiết hơn
└── [Output files]         # Các file ảnh đã ghép
```

## Xử Lý Lỗi

### Lỗi Thường Gặp

1. **"Khong tim thay thu muc"**
   - Kiểm tra đường dẫn trong script
   - Đảm bảo thư mục Blocks tồn tại

2. **"Khong co tile hop le"**
   - Kiểm tra format tên file
   - Đảm bảo layer number đúng

3. **Out of Memory**
   - Thử layer thấp hơn (L02 thay vì L01)
   - Đóng các ứng dụng khác

## Thuật Toán

Script sử dụng phương pháp ghép ảnh theo grid:

1. **Parse tên file** để xác định vị trí (row, col) của mỗi tile
2. **Tạo canvas** với kích thước = grid_size × tile_size
3. **Paste từng tile** vào đúng vị trí trên canvas
4. **Lưu kết quả** dưới dạng JPEG (quality=95)

## So Sánh Với Ảnh Gốc

Script tự động so sánh ảnh ghép với ảnh gốc (L07) bằng cách:
1. Resize ảnh ghép xuống kích thước L07 (1024x1024)
2. Tính độ chênh lệch pixel trung bình
3. Hiển thị % độ tương đồng

**Độ tương đồng:**
- \>95%: Rất chính xác
- 85-95%: Khá chính xác
- <85%: Có thể có sai lệch

## Tác Giả

Script được phát triển để ghép ảnh microscope từ các tiles theo cấu trúc pyramid.

## Phiên Bản

- v1.0: Phiên bản đầu tiên (có lỗi parse filename)
- v2.0: Sửa lỗi parse filename với hex numbers (A, B, C, D, E, F)
- v2.1: Thêm so sánh với ảnh gốc và tối ưu hiệu suất
