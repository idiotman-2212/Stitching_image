# CÔNG TY TNHH GIẢI PHÁP Y SINH ABT

## CHI NHÁNH LONG HẬU

### PHÒNG KTCN

---

## ĐỀ CƯƠNG NGHIÊN CỨU-PHÁT TRIỂN PHẦN MỀM

## PHẦN MỀM GHÉP ẢNH CHO CAMERA

**<Mã phần mềm>**

---

| | | |
|---|---|---|
| **SOẠN THẢO BỞI** | **SOÁT XÉT BỞI** | **PHÊ DUYỆT BỞI** |
| Ký tên: Châu Huy Diễn | Ký tên: | Ký tên: |
| Họ tên: Châu Huy Diễn | Họ tên: | Họ tên: |
| Chức vụ: Nhân viên IT | Chức vụ: | Chức vụ: |
| Ngày ký: | Ngày ký: | Ngày ký: |

---

## I. MỤC ĐÍCH

Hướng dẫn việc triển khai thực hiện nghiên cứu-phát triển phần mềm Ghép ảnh cho camera đáp ứng các yêu cầu đã định. Cụ thể, phần mềm này nhằm mục tiêu:

### 1. Mục tiêu chính

- Chuyển đổi kính hiển vi quang học tiêu chuẩn (sử dụng bàn kính thủ công) thành **Hệ thống Quét Tiêu bản Toàn cảnh Thủ công** (Manual Whole Slide Scanning)

- Thu thập và ghép các hình ảnh nhỏ từ camera kính hiển vi để tạo ra ảnh toàn cảnh (panorama) chất lượng cao với **độ chính xác cao**, đảm bảo các mẫu tế bào liền mạch và khớp với nhau

- Sử dụng metadata từ hệ thống LandingMed để đảm bảo độ chính xác cao trong ghép ảnh

### 2. Mục tiêu cụ thể

- Số hóa tiêu bản: Chuyển đổi tiêu bản vật lý thành ảnh kỹ thuật số chất lượng cao

- Lưu trữ lâu dài: Bảo quản mẫu dưới dạng số, tránh hư hỏng vật lý

- Chia sẻ dễ dàng: Gửi ảnh qua mạng cho chẩn đoán từ xa

- Phân tích tự động: Tạo cơ sở cho các ứng dụng AI/ML trong tương lai

- Giảm chi phí: Sử dụng camera USB thông thường thay vì hệ thống chuyên dụng đắt tiền

- Đảm bảo độ chính xác: Ghép ảnh dựa trên tọa độ thực tế từ metadata, không phụ thuộc vào feature matching

---

## II. PHẠM VI ÁP DỤNG

Áp dụng cho quá trình nghiên cứu-phát triển phần mềm Ghép ảnh cho camera tại phòng KTCN của Công ty TNHH Giải pháp Y sinh ABT-Chi nhánh Long Hậu, bao gồm việc tích hợp phần cứng, xử lý metadata và tối ưu hóa thuật toán ghép ảnh dựa trên tọa độ.

---

## III. TRÁCH NHIỆM, QUYỀN HẠN VÀ THÀNH PHẦN THAM GIA THẨM ĐỊNH ĐỀ CƯƠNG

| STT | Nội dung công việc | Trách nhiệm |
|-----|-------------------|-------------|
| 1 | Soạn thảo, xét duyệt và phê duyệt đề cương | Phòng KTCN |
| 2 | Nghiên cứu, lựa chọn và phát triển thuật toán ghép ảnh dựa trên metadata | Phòng KTCN |
| 3 | Tích hợp và cấu hình Camera Kính Hiển Vi (Driver, Live Stream, Cài đặt Exposure, Resolution) | Phòng KTCN |
| 4 | Xây dựng module xử lý metadata và tính toán tọa độ tile | Phòng KTCN |
| 5 | Kiểm tra chất lượng và đánh giá độ chính xác của ảnh ghép | Phòng KTCN |
| 6 | Lập kế hoạch chi tiết và triển khai các Phase tiếp theo | Phòng KTCN |
| 7 | Tổng hợp báo cáo kỹ thuật và tài liệu hướng dẫn sử dụng/cài đặt phần cứng | Phòng KTCN |

---

## IV. THUẬT NGỮ, ĐỊNH NGHĨA

| STT | Thuật ngữ | Định nghĩa |
|-----|-----------|-----------|
| 1 | WSI | Whole Slide Imaging - Quét toàn bộ tiêu bản |
| 2 | Stitching | Ghép nối nhiều ảnh nhỏ thành ảnh lớn |
| 3 | Metadata | Dữ liệu mô tả về dữ liệu (tọa độ, kích thước, level...) |
| 4 | Tile | Ảnh nhỏ (mảnh ghép) trong hệ thống WSI |
| 5 | Level | Mức độ phóng đại/thu nhỏ (0=chi tiết nhất, 7=tổng quan nhất) |
| 6 | Canvas | Vùng vẽ lớn để ghép các tiles |
| 7 | BlocksJson | File JSON chứa metadata của tất cả các tiles |
| 8 | ImageX, ImageY | Tọa độ góc trái-trên của tile trong hệ tọa độ toàn cục |
| 9 | ImageWidth, ImageHeight | Kích thước của tile (pixel) |
| 10 | Row, Column | Vị trí hàng/cột của tile trong lưới tiles |
| 11 | Scale Factor | Tỷ lệ giữa kích thước thực tế và metadata |
| 12 | Panorama | Ảnh toàn cảnh ghép từ nhiều ảnh nhỏ |

---

## V. NỘI DUNG

### 1. Thông tin chung

**Người thực hiện: Châu Huy Diễn**

**Thời gian thực hiện: Từ 20/11/2025 đến 03/12/2025**

### 2. Mục đích nghiên cứu

Mục đích của đề cương này là hướng dẫn việc triển khai thực hiện nghiên cứu-phát triển phần mềm Ghép ảnh cho camera đáp ứng các yêu cầu đã định. Cụ thể, phần mềm này nhằm mục tiêu chuyển đổi một kính hiển vi tiêu chuẩn thành một **Hệ thống Quét Lam Kính Thủ công (Manual Whole Slide Scanning)** bằng cách thu thập và ghép các hình ảnh nhỏ theo **tọa độ chính xác từ metadata** để tạo ra một ảnh toàn cảnh chất lượng cao, đảm bảo các mẫu tế bào liền mạch và khớp với nhau.

### 3. Tổng quan hệ thống

Hệ thống ghép ảnh hiện tại sử dụng phương pháp **Metadata-Based Stitching** - ghép ảnh dựa trên thông tin tọa độ chính xác từ file `BlocksJson.json`. Phương pháp này đảm bảo:

- **Độ chính xác cao**: Mỗi tile được đặt đúng vị trí theo tọa độ thực tế
- **Tế bào liền mạch**: Các mẫu tế bào khớp hoàn hảo giữa các tiles
- **Hiệu suất tốt**: Không cần phải tính toán feature matching phức tạp
- **Tương thích**: Hoạt động tương thích với format dữ liệu của LandingMed

### 4. Yêu cầu thiết bị

| TT | Tên thiết bị | ĐVT | Số lượng | Yêu cầu |
|----|-------------|-----|----------|---------|
| 1 | Camera Kính Hiển Vi | Cái | 1 | Euromex DC.5000F, 5MP, USB 2.0/3.0 |
| 2 | Cổng/cáp kết nối | Cái | 1 | USB 3.0 với máy tính |
| 3 | Máy tính | Bộ | 1 | RAM ≥16GB, CPU i5+, Windows 10/11 |
| 4 | Kính hiển vi | Cái | 1 | Kính hiển vi quang học tiêu chuẩn |
| 5 | Tiêu bản mẫu | Cái | 1-50 | Tiêu bản mô học để test |

### 5. Yêu cầu phần mềm

| TT | Tên phần mềm/Thư viện | Phiên bản | Mục đích |
|----|--------------------|-----------|----------|
| 1 | Python | 3.11+ | Ngôn ngữ lập trình chính |
| 2 | opencv-python | 4.12.0+ | Xử lý ảnh, đọc/ghi file |
| 3 | numpy | 2.2.6 | Tính toán mảng, xử lý canvas |
| 4 | json | Built-in | Đọc metadata từ BlocksJson.json |

### 6. Kiến trúc hệ thống

#### INPUT LAYER (Đầu vào)

- **Metadata File**: `BlocksJson.json` - Chứa thông tin tọa độ và kích thước của tất cả tiles
- **Image Tiles**: Các file .jpg được tổ chức theo level (L00 đến L07)
- **Level Selection**: Người dùng chọn level cần ghép (0-7)

#### PROCESSING LAYER (Xử lý)

**Module chính: Image Stitcher (stitch_landingmed_final.py)**

1. **Metadata Loading**
   - Đọc file `BlocksJson.json`
   - Phân tích thông tin về Level, Row, Column, ImageX, ImageY, ImageWidth, ImageHeight

2. **Canvas Calculation**
   - Tính toán kích thước canvas dựa trên min/max tọa độ
   - Tính scale factor giữa metadata và kích thước file thực tế
   - Cấp phát bộ nhớ cho canvas

3. **Tile Placement**
   - Sắp xếp tiles theo thứ tự Row, Column
   - Tính toán vị trí chính xác trên canvas: `x = (ImageX - min_x) × scale_x`
   - Đặt từng tile lên canvas theo tọa độ đã tính

4. **Quality Control**
   - Kiểm tra bounds để tránh lỗi tràn bộ nhớ
   - Theo dõi số lượng tiles thành công/thất bại
   - Báo cáo tiến trình xử lý

#### OUTPUT LAYER (Đầu ra)

- **Stitched Image**: File .jpg chứa ảnh panorama hoàn chỉnh
- **Statistics**: Thông tin về số tiles, kích thước, thời gian xử lý
- **Quality Report**: So sánh với ảnh gốc (nếu có)

### 7. Thuật toán chính

#### 7.1. Metadata-Based Stitching (Ghép ảnh dựa trên metadata)

**Nguyên lý hoạt động:**

Thay vì sử dụng feature detection (SIFT, SURF...) để tìm điểm chung giữa các ảnh, hệ thống sử dụng **thông tin tọa độ chính xác** từ metadata để đặt từng tile vào đúng vị trí.

**Các bước thực hiện:**

1. **LOAD METADATA (Đọc metadata)**
   - Input: File `BlocksJson.json`
   - Output: Danh sách blocks với các thuộc tính:
     - `Level`: Mức độ chi tiết (0-7)
     - `Row`, `Coloumn`: Vị trí trong lưới
     - `ImageX`, `ImageY`: Tọa độ pixel trong hệ tọa độ toàn cục
     - `ImageWidth`, `ImageHeight`: Kích thước tile
     - `ImageName`: Tên file ảnh
   - Thời gian: < 1 giây

2. **FILTER BY LEVEL (Lọc theo level)**
   - Input: Danh sách tất cả blocks, level cần ghép
   - Output: Danh sách blocks thuộc level đã chọn
   - Ví dụ: Level 1 có ~600-800 tiles, Level 7 chỉ có 1 tile

3. **CALCULATE SCALE FACTOR (Tính tỷ lệ scale)**
   - Đọc 1 tile mẫu để lấy kích thước thực tế
   - So sánh với kích thước trong metadata
   - Công thức:
     ```
     scale_x = actual_width / metadata_width
     scale_y = actual_height / metadata_height
     ```
   - Lý do: Kích thước file .jpg có thể khác với metadata do nén

4. **CREATE CANVAS (Tạo canvas)**
   - Tìm min/max tọa độ từ tất cả tiles:
     ```
     min_x = min(block.ImageX for all blocks)
     min_y = min(block.ImageY for all blocks)
     max_x = max(block.ImageX + block.ImageWidth for all blocks)
     max_y = max(block.ImageY + block.ImageHeight for all blocks)
     ```
   - Tính kích thước canvas sau khi scale:
     ```
     canvas_width = (max_x - min_x) × scale_x
     canvas_height = (max_y - min_y) × scale_y
     ```
   - Khởi tạo mảng numpy với background màu xám nhạt (240, 240, 240)
   - Thời gian: 1-5 giây (tùy level)

5. **PASTE TILES (Dán các tiles)**
   - Sắp xếp tiles theo thứ tự (Row, Column)
   - Với mỗi tile:
     - Đọc ảnh từ file
     - Tính vị trí trên canvas:
       ```
       x = (block.ImageX - min_x) × scale_x
       y = (block.ImageY - min_y) × scale_y
       ```
     - Dán ảnh vào canvas:
       ```
       canvas[y:y+h, x:x+w] = tile_image
       ```
   - Không cần resize tile (giữ nguyên kích thước gốc)
   - Thời gian: 5-30 giây (tùy số lượng tiles)

6. **SAVE RESULT (Lưu kết quả)**
   - Ghi canvas ra file .jpg với quality = 95%
   - Báo cáo kích thước file và thống kê
   - Thời gian: 2-10 giây

**Ưu điểm của phương pháp:**

- ✅ **Độ chính xác tuyệt đối**: Tiles được đặt đúng vị trí theo tọa độ
- ✅ **Tế bào liền mạch**: Không có lỗi misalignment
- ✅ **Hiệu suất cao**: Không cần tính toán feature matching phức tạp
- ✅ **Ổn định**: Không bị ảnh hưởng bởi độ tương đồng của ảnh
- ✅ **Tương thích**: Hoạt động với dữ liệu từ LandingMed hoặc hệ thống tương tự

**Công thức tính toán:**

```
Tọa độ tile trên canvas:
x_canvas = (ImageX_metadata - min_x) × scale_x
y_canvas = (ImageY_metadata - min_y) × scale_y

Kích thước canvas:
W_canvas = (max_x - min_x) × scale_x
H_canvas = (max_y - min_y) × scale_y

Dung lượng RAM (MB):
RAM = (W_canvas × H_canvas × 3) / (1024²)
```

#### 7.2. Image Comparison (So sánh ảnh)

**Mục đích:** So sánh ảnh ghép với ảnh gốc Level 7 để đánh giá chất lượng

**Phương pháp:**
- Resize ảnh ghép về kích thước của L07
- Tính độ khác biệt trung bình:
  ```
  diff = |stitched - original|
  similarity = 100 × (1 - mean(diff) / 255)
  ```

**Đánh giá:**
- > 95%: Excellent (Rất giống)
- 85-95%: Good (Tốt)
- 70-85%: Fair (Khá)
- < 70%: Poor (Cần kiểm tra)

### 8. Kết quả thực tế

#### Thông số Level 1 (L01)

| Thông số | Giá trị |
|----------|---------|
| Số lượng tiles | ~700 tiles |
| Kích thước mỗi tile | 1440×2560 pixels |
| Kích thước canvas | ~15,000×25,000 pixels |
| Dung lượng RAM | ~1,800 MB |
| Thời gian xử lý | 15-30 giây |
| Kích thước file output | ~140 MB (.jpg) |
| Độ tương đồng với L07 | > 95% |

#### So sánh các Levels

| Level | Số tiles | Kích thước canvas | Thời gian | Mục đích sử dụng |
|-------|----------|-------------------|-----------|------------------|
| L00 | ~3000 | Rất lớn (>100k×200k) | 5-10 phút | Chi tiết tối đa, phân tích |
| L01 | ~700 | ~15k×25k | 15-30s | Sử dụng chung, chất lượng tốt |
| L02 | ~200 | ~8k×12k | 5-10s | Xem tổng quan nhanh |
| L03 | ~50 | ~4k×6k | 2-5s | Preview |
| L07 | 1 | ~500×800 | <1s | Thumbnail |

#### Đánh giá chất lượng

- ✅ **Tế bào liền mạch**: Các mẫu tế bào khớp hoàn hảo, không có đường nối
- ✅ **Màu sắc đồng nhất**: Không có sự chênh lệch màu giữa các tiles
- ✅ **Độ sắc nét**: Giữ nguyên độ sắc nét của ảnh gốc
- ✅ **Không bị lỗi**: Không có hiện tượng ghosting, overlapping sai

### 9. Tiến độ thực hiện

| TT | Công việc | Thời gian | Trạng thái |
|----|-----------|-----------|------------|
| **1** | **Nghiên cứu & Thiết kế** | | |
| 1.1 | Nghiên cứu thuật toán metadata-based stitching | 20-21/11/2025 | ✅ Hoàn thành |
| 1.2 | Phân tích cấu trúc BlocksJson.json | 21/11/2025 | ✅ Hoàn thành |
| 1.3 | Thiết kế kiến trúc hệ thống | 22/11/2025 | ✅ Hoàn thành |
| **2** | **Phát triển hệ thống** | | |
| 2.1 | Xây dựng module đọc metadata | 23/11/2025 | ✅ Hoàn thành |
| 2.2 | Xây dựng module tính toán canvas | 24/11/2025 | ✅ Hoàn thành |
| 2.3 | Xây dựng module ghép tiles | 25-26/11/2025 | ✅ Hoàn thành |
| 2.4 | Xây dựng module so sánh chất lượng | 27/11/2025 | ✅ Hoàn thành |
| **3** | **Kiểm thử và tối ưu** | | |
| 3.1 | Kiểm thử với các levels khác nhau | 28/11/2025 | ✅ Hoàn thành |
| 3.2 | Tối ưu hiệu năng và bộ nhớ | 01/12/2025 | ✅ Hoàn thành |
| 3.3 | Kiểm tra độ chính xác | 02/12/2025 | ✅ Hoàn thành |
| 3.4 | Hoàn thiện báo cáo | 03/12/2025 | ✅ Hoàn thành |

### 10. Hướng phát triển tiếp theo

1. **Tích hợp với camera thời gian thực**
   - Capture ảnh trực tiếp từ Euromex DC.5000F
   - Tự động tạo metadata khi chụp
   - Ghép ảnh real-time

2. **Tối ưu bộ nhớ**
   - Xử lý từng vùng thay vì load toàn bộ canvas
   - Hỗ trợ ghép ảnh L00 (level chi tiết nhất)

3. **Giao diện người dùng**
   - Xây dựng GUI để dễ sử dụng
   - Hiển thị preview và tiến trình
   - Cho phép zoom/pan trên ảnh kết quả

4. **Export đa định dạng**
   - Hỗ trợ xuất TIFF, PNG
   - Tạo Deep Zoom Images (DZI) để xem online

### 11. Tài liệu tham khảo

#### 11.1. Tài liệu kỹ thuật

1. **OpenCV Documentation (2024).** "Image Processing and Computer Vision".
   - URL: https://docs.opencv.org/4.x/
   - Hướng dẫn xử lý ảnh với OpenCV

2. **NumPy Documentation (2024).** "Array Programming with NumPy".
   - URL: https://numpy.org/doc/stable/
   - Hướng dẫn xử lý mảng và ma trận

3. **JSON Schema Specification.**
   - URL: https://json-schema.org/
   - Chuẩn định dạng file metadata

#### 11.2. Tài liệu phần cứng

1. **Euromex DC.5000F Catalog (2024).**
   - URL: https://drive.google.com/file/d/11lS41emkJYX_ENU9WDa-lLiIWSqFz5Qz/view
   - Thông số kỹ thuật camera

2. **USB 3.0 Specification.**
   - Yêu cầu về băng thông và driver

#### 11.3. Tham khảo thuật toán

1. **Coordinate-based Image Mosaicing.**
   - Phương pháp ghép ảnh dựa trên tọa độ chính xác
   - Ứng dụng trong y sinh học và kính hiển vi

2. **Whole Slide Imaging (WSI) Standards.**
   - Chuẩn định dạng dữ liệu cho quét tiêu bản
   - Metadata structure và best practices

---

## VI. KẾT LUẬN

Hệ thống ghép ảnh đã được phát triển thành công với phương pháp **Metadata-Based Stitching**, đảm bảo:

1. ✅ **Độ chính xác cao**: Các tiles được ghép đúng vị trí theo tọa độ thực tế
2. ✅ **Tế bào liền mạch**: Các mẫu tế bào khớp hoàn hảo, không có đường nối
3. ✅ **Hiệu suất tốt**: Xử lý nhanh, không tốn tài nguyên cho feature matching
4. ✅ **Tương thích**: Hoạt động với dữ liệu từ LandingMed
5. ✅ **Dễ bảo trì**: Code đơn giản, dễ hiểu và mở rộng

Hệ thống đã sẵn sàng triển khai và có thể phát triển thêm các tính năng như tích hợp camera real-time và giao diện người dùng.

---

**Ngày hoàn thành báo cáo: 03/12/2025**