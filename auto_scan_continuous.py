# -*- coding: utf-8 -*-
"""
HE THONG QUET TIEU BAN TU DONG LIEN TUC
========================================
Chuong trinh tu dong chup anh lien tuc khi di chuyen ban mau,
tu dong tinh toan toa do va tao metadata giong LandingMed.

Tinh nang:
- Motion Detection: Phat hien khi ban mau di chuyen
- Auto Capture: Tu dong chup khi di chuyen du xa
- Position Tracking: Tinh toan toa do chinh xac bang feature matching
- Multi-level: Tao cac level L00-L07 tu dong
- Real-time Preview: Hien thi vung da quet
"""
import cv2
import numpy as np
import os
import json
import sys
import time
from datetime import datetime
from collections import deque

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class ContinuousScanner:
    """
    He thong quet tieu ban lien tuc
    """
    def __init__(self, output_dir="scan_output", tile_size=1024, overlap_percent=0.1):
        """
        Khoi tao scanner
        
        Args:
            output_dir: Thu muc luu du lieu
            tile_size: Kich thuoc tile (pixel) - mac dinh 1024x1024 nhu LandingMed
            overlap_percent: Ti le overlap (0.1 = 10%)
        """
        self.output_dir = output_dir
        self.tile_size = tile_size
        self.overlap_percent = overlap_percent
        
        # Tinh buoc di chuyen
        self.step_size = int(tile_size * (1 - overlap_percent))
        
        # Luu tru tiles
        self.tiles = []  # Danh sach tat ca tiles
        self.tile_counter = 0
        
        # Tracking position
        self.current_x = 0  # Toa do toan cuc hien tai
        self.current_y = 0
        self.prev_frame = None  # Frame truoc do
        self.prev_keypoints = None
        self.prev_descriptors = None
        
        # Feature detector (su dung ORB vi nhanh)
        self.detector = cv2.ORB_create(nfeatures=1000)
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        
        # Camera resolution
        self.camera_w = 0
        self.camera_h = 0
        
        # Trang thai
        self.is_scanning = False
        self.total_tiles_captured = 0
        
        # Buffer de luu cac frame gan day (de xuat levels sau)
        self.frame_buffer = deque(maxlen=100)
        
        # Scan Map Visualization - Luu cac o da quet
        self.scan_map = {}  # Key: (row, col), Value: True
        self.min_row, self.max_row = 0, 0
        self.min_col, self.max_col = 0, 0
        
        # Setup directories
        self.setup_directories()
        
    def setup_directories(self):
        """Tao cau truc thu muc giong LandingMed"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, 'Blocks'), exist_ok=True)
        
        # Tao cac level L00-L07
        for level in range(8):
            level_dir = os.path.join(self.output_dir, 'Blocks', f'L0{level}')
            os.makedirs(level_dir, exist_ok=True)
            
        os.makedirs(os.path.join(self.output_dir, 'Data'), exist_ok=True)
        
    def detect_movement(self, current_frame):
        """
        Phat hien va tinh toan su di chuyen cua ban mau
        
        Args:
            current_frame: Frame hien tai
            
        Returns:
            (dx, dy): Do di chuyen theo pixel, hoac None neu khong phat hien duoc
        """
        if self.prev_frame is None:
            # Frame dau tien, luu lai
            gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
            self.prev_keypoints, self.prev_descriptors = self.detector.detectAndCompute(gray, None)
            self.prev_frame = current_frame.copy()
            return (0, 0)
        
        # Tim keypoints tren frame hien tai
        gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        curr_keypoints, curr_descriptors = self.detector.detectAndCompute(gray, None)
        
        if curr_descriptors is None or self.prev_descriptors is None:
            return None
        
        if len(curr_descriptors) < 10 or len(self.prev_descriptors) < 10:
            return None
        
        # Tim matches
        try:
            matches = self.matcher.match(self.prev_descriptors, curr_descriptors)
            
            if len(matches) < 10:
                return None
            
            # Sap xep matches theo distance
            matches = sorted(matches, key=lambda x: x.distance)
            good_matches = matches[:min(50, len(matches))]
            
            # Tinh vector di chuyen trung binh
            dx_list = []
            dy_list = []
            
            for match in good_matches:
                prev_pt = self.prev_keypoints[match.queryIdx].pt
                curr_pt = curr_keypoints[match.trainIdx].pt
                
                dx = curr_pt[0] - prev_pt[0]
                dy = curr_pt[1] - prev_pt[1]
                
                dx_list.append(dx)
                dy_list.append(dy)
            
            # Lay median de giam thieu outliers
            dx_median = np.median(dx_list)
            dy_median = np.median(dy_list)
            
            # Luu frame hien tai cho lan tinh tiep theo
            self.prev_frame = current_frame.copy()
            self.prev_keypoints = curr_keypoints
            self.prev_descriptors = curr_descriptors
            
            return (-dx_median, -dy_median)  # Dao dau vi camera di nguoc lai ban mau
            
        except Exception as e:
            print(f"[WARNING] Loi khi tinh movement: {e}")
            return None
    
    def should_capture(self, dx, dy):
        """
        Kiem tra xem co nen chup anh khong
        
        Args:
            dx, dy: Do di chuyen tich luy
            
        Returns:
            True neu nen chup
        """
        # Chup khi di chuyen vuot qua step_size theo bat ky huong nao
        distance = np.sqrt(dx**2 + dy**2)
        return distance >= self.step_size
    
    def capture_tile(self, frame, accumulated_dx, accumulated_dy):
        """
        Chup tile va luu metadata
        
        Args:
            frame: Frame can luu
            accumulated_dx, dy: Tong do di chuyen tich luy
        """
        # Cap nhat vi tri toan cuc
        self.current_x += int(accumulated_dx)
        self.current_y += int(accumulated_dy)
        
        # Crop tile tu center cua frame
        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        half_tile = self.tile_size // 2
        
        # Tinh vi tri crop
        x1 = max(0, center_x - half_tile)
        y1 = max(0, center_y - half_tile)
        x2 = min(w, center_x + half_tile)
        y2 = min(h, center_y + half_tile)
        
        # Crop tile
        tile = frame[y1:y2, x1:x2].copy()
        
        # Resize neu can de dam bao kich thuoc chuan
        if tile.shape[:2] != (self.tile_size, self.tile_size):
            tile = cv2.resize(tile, (self.tile_size, self.tile_size))
        
        # Tinh Row va Column tu toa do
        row = self.current_y // self.step_size
        col = self.current_x // self.step_size
        
        # Ten file theo format LandingMed: B{Level}{Index:06X}C.jpg
        # Chi luu Level 0 truoc, cac level khac se tao sau
        index = self.tile_counter
        image_name = f"B0{index:06X}C.jpg"
        image_path = os.path.join(self.output_dir, 'Blocks', 'L00', image_name)
        
        # Luu tile
        cv2.imwrite(image_path, tile, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        # Tao metadata block
        block = {
            "Index": index,
            "Level": 0,
            "Coloumn": col,
            "Row": row,
            "CoreX": self.current_x,
            "CoreY": self.current_y,
            "CoreWidth": self.tile_size,
            "CoreHeight": self.tile_size,
            "ImageX": self.current_x,
            "ImageY": self.current_y,
            "ImageWidth": self.tile_size,
            "ImageHeight": self.tile_size,
            "BlueBackGround": 240.0,
            "GreedBackGround": 240.0,  # Giu nguyen loi chinh ta nhu LandingMed
            "RedBackGround": 240.0,
            "ImageName": image_name
        }
        
        self.tiles.append(block)
        self.tile_counter += 1
        self.total_tiles_captured += 1
        
        # Luu frame vao buffer (de xu ly levels sau)
        self.frame_buffer.append({
            'frame': tile,
            'block': block
        })
        
        # Cap nhat Scan Map
        grid_key = (row, col)
        self.scan_map[grid_key] = True
        
        # Cap nhat bounds cho minimap
        if len(self.scan_map) == 1:
            self.min_row = self.max_row = row
            self.min_col = self.max_col = col
        else:
            self.min_row = min(self.min_row, row)
            self.max_row = max(self.max_row, row)
            self.min_col = min(self.min_col, col)
            self.max_col = max(self.max_col, col)
        
        print(f"[✓] Tile #{self.total_tiles_captured}: "
              f"Row={row}, Col={col}, X={self.current_x}, Y={self.current_y}")
        
        return True
    
    def generate_lower_levels(self):
        """
        Tao cac levels tu L01 den L07 tu Level 0 (downsampling)
        """
        print(f"\n{'='*70}")
        print("TAO CAC LEVELS TU L01 DEN L07...")
        print(f"{'='*70}")
        
        if len(self.tiles) == 0:
            print("[WARNING] Khong co tiles L00 de tao levels!")
            return
        
        # Tim kich thuoc toan canh
        max_x = max(t['ImageX'] + t['ImageWidth'] for t in self.tiles)
        max_y = max(t['ImageY'] + t['ImageHeight'] for t in self.tiles)
        
        print(f"Kich thuoc toan canh L00: {max_x} x {max_y}")
        
        # Tao canvas L00 (full resolution)
        print(f"\nTao canvas L00...")
        canvas_l00 = np.zeros((max_y, max_x, 3), dtype=np.uint8)
        canvas_l00[:,:] = [240, 240, 240]
        
        # Ghep tat ca tiles vao canvas
        for tile_info in self.tiles:
            img_path = os.path.join(self.output_dir, 'Blocks', 'L00', tile_info['ImageName'])
            img = cv2.imread(img_path)
            if img is not None:
                x, y = tile_info['ImageX'], tile_info['ImageY']
                h, w = img.shape[:2]
                if y + h <= max_y and x + w <= max_x:
                    canvas_l00[y:y+h, x:x+w] = img
        
        # Tao cac levels bang cach downscale
        all_levels_blocks = list(self.tiles)  # Copy tiles L00
        
        for level in range(1, 8):
            print(f"\nTao Level {level}...")
            
            # Downscale canvas theo ty le 2^level
            scale = 2 ** level
            new_w = max_x // scale
            new_h = max_y // scale
            
            canvas_scaled = cv2.resize(canvas_l00, (new_w, new_h), interpolation=cv2.INTER_AREA)
            
            # Chia thanh cac tiles
            tile_size_scaled = self.tile_size  # Giu nguyen kich thuoc tile
            step_size_scaled = int(tile_size_scaled * (1 - self.overlap_percent))
            
            level_tiles = []
            tile_index = 0
            
            for row_idx, y in enumerate(range(0, new_h, step_size_scaled)):
                for col_idx, x in enumerate(range(0, new_w, step_size_scaled)):
                    # Crop tile
                    y2 = min(y + tile_size_scaled, new_h)
                    x2 = min(x + tile_size_scaled, new_w)
                    
                    tile = canvas_scaled[y:y2, x:x2].copy()
                    
                    # Resize neu can
                    if tile.shape[:2] != (tile_size_scaled, tile_size_scaled):
                        if tile.shape[0] < tile_size_scaled//2 or tile.shape[1] < tile_size_scaled//2:
                            continue  # Bo qua tiles qua nho
                        tile = cv2.resize(tile, (tile_size_scaled, tile_size_scaled))
                    
                    # Tao ten file
                    image_name = f"B{level}{tile_index:06X}C.jpg"
                    image_path = os.path.join(self.output_dir, 'Blocks', f'L0{level}', image_name)
                    
                    # Luu tile
                    cv2.imwrite(image_path, tile, [cv2.IMWRITE_JPEG_QUALITY, 90])
                    
                    # Tao metadata (toa do trong he toa do cua level hien tai)
                    block = {
                        "Index": tile_index + (level << 24),  # Shift level vao index
                        "Level": level,
                        "Coloumn": col_idx,
                        "Row": row_idx,
                        "CoreX": x,
                        "CoreY": y,
                        "CoreWidth": tile_size_scaled,
                        "CoreHeight": tile_size_scaled,
                        "ImageX": x,
                        "ImageY": y,
                        "ImageWidth": tile_size_scaled,
                        "ImageHeight": tile_size_scaled,
                        "BlueBackGround": 240.0,
                        "GreedBackGround": 240.0,
                        "RedBackGround": 240.0,
                        "ImageName": image_name
                    }
                    
                    level_tiles.append(block)
                    all_levels_blocks.append(block)
                    tile_index += 1
            
            print(f"  Level {level}: Tao {len(level_tiles)} tiles")
        
        # Luu tat ca blocks vao BlocksJson.json
        print(f"\nLuu BlocksJson.json...")
        json_path = os.path.join(self.output_dir, 'Data', 'BlocksJson.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(all_levels_blocks, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Da luu {len(all_levels_blocks)} blocks vao {json_path}")
    
    def save_metadata(self):
        """Luu metadata BlocksJson.json"""
        json_path = os.path.join(self.output_dir, 'Data', 'BlocksJson.json')
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.tiles, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Da luu metadata: {json_path}")
        print(f"  Tong so tiles Level 0: {len(self.tiles)}")
    
    def run(self, camera_id=0):
        """Chay chuong trinh chinh"""
        print("="*70)
        print("HE THONG QUET TIEU BAN TU DONG LIEN TUC")
        print("="*70)
        print()
        print("HUONG DAN:")
        print("  [S]      - Bat dau quet (Start)")
        print("  [P]      - Tam dung (Pause)")
        print("  [R]      - Reset (Bat dau lai)")
        print("  [G]      - Tao cac levels L01-L07 (Generate levels)")
        print("  [Q]      - Ket thuc (Quit)")
        print()
        print("CHE DO TU DONG:")
        print("  - He thong tu dong phat hien khi ban mau di chuyen")
        print("  - Tu dong chup anh khi di chuyen du xa")
        print(f"  - Overlap: {self.overlap_percent*100:.0f}%")
        print(f"  - Buoc di chuyen: {self.step_size} pixels")
        print("="*70)
        print()
        
        # Khoi tao camera
        print(f"Dang mo camera {camera_id}...")
        cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        
        if not cap.isOpened():
            print(f"[ERROR] Khong the mo camera {camera_id}!")
            return
        
        # Set resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
        # Lay resolution thuc te
        self.camera_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.camera_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"[OK] Camera da san sang!")
        print(f"  Resolution: {self.camera_w} x {self.camera_h}")
        print(f"\nNhan [S] de bat dau quet...")
        
        # Tich luy movement
        accumulated_dx = 0
        accumulated_dy = 0
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    print("[WARNING] Khong doc duoc frame!")
                    time.sleep(0.1)
                    continue
                
                # Hien thi frame
                display = frame.copy()
                
                # Ve thong tin
                status = "SCANNING" if self.is_scanning else "PAUSED"
                color = (0, 255, 0) if self.is_scanning else (0, 0, 255)
                
                info_text = [
                    f"Status: {status} | Tiles: {self.total_tiles_captured}",
                    f"Position: X={self.current_x}, Y={self.current_y}",
                    f"Movement: dX={accumulated_dx:.0f}, dY={accumulated_dy:.0f}",
                    f"[S]=Start [P]=Pause [R]=Reset [G]=Generate [Q]=Quit"
                ]
                
                y_pos = 30
                for text in info_text:
                    cv2.putText(display, text, (10, y_pos),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    y_pos += 30
                
                # Ve vung tile se chup (center)
                h, w = display.shape[:2]
                center_x, center_y = w // 2, h // 2
                half_tile = min(self.tile_size, min(w, h)) // 2
                
                cv2.rectangle(display, 
                             (center_x - half_tile, center_y - half_tile),
                             (center_x + half_tile, center_y + half_tile),
                             (0, 255, 255), 2)
                
                # === TAO MINIMAP HIEN THI VUNG DA QUET ===
                minimap_size = 350
                minimap_margin = 15
                
                # Tao nen minimap
                minimap = np.zeros((minimap_size, minimap_size, 3), dtype=np.uint8)
                minimap[:,:] = [40, 40, 40]  # Nen xam dam
                
                # Ve border
                cv2.rectangle(minimap, (0, 0), (minimap_size-1, minimap_size-1), (100, 100, 100), 2)
                
                # Hien thi minimap neu co du lieu
                if len(self.scan_map) > 0:
                    # Tinh kich thuoc luoi
                    map_h = self.max_row - self.min_row + 1
                    map_w = self.max_col - self.min_col + 1
                    
                    # Them margin cho luoi (cho phep mo rong)
                    margin_cells = 5
                    map_h_padded = map_h + margin_cells * 2
                    map_w_padded = map_w + margin_cells * 2
                    
                    if map_h_padded > 0 and map_w_padded > 0:
                        # Tinh ty le scale
                        usable_size = minimap_size - 40  # Tru di padding
                        scale = min(usable_size / map_w_padded, usable_size / map_h_padded)
                        
                        # Tinh offset de can giua
                        grid_w = int(map_w_padded * scale)
                        grid_h = int(map_h_padded * scale)
                        offset_x = (minimap_size - grid_w) // 2
                        offset_y = (minimap_size - grid_h) // 2
                        
                        # Ve luoi nen (grid lines)
                        for i in range(map_h_padded + 1):
                            y = offset_y + int(i * scale)
                            cv2.line(minimap, (offset_x, y), (offset_x + grid_w, y), (60, 60, 60), 1)
                        for i in range(map_w_padded + 1):
                            x = offset_x + int(i * scale)
                            cv2.line(minimap, (x, offset_y), (x, offset_y + grid_h), (60, 60, 60), 1)
                        
                        # Ve cac o da quet (mau xanh la)
                        for (row, col) in self.scan_map.keys():
                            grid_row = row - self.min_row + margin_cells
                            grid_col = col - self.min_col + margin_cells
                            
                            x = offset_x + int(grid_col * scale)
                            y = offset_y + int(grid_row * scale)
                            x2 = offset_x + int((grid_col + 1) * scale)
                            y2 = offset_y + int((grid_row + 1) * scale)
                            
                            # To mau o da quet
                            cv2.rectangle(minimap, (x+1, y+1), (x2-1, y2-1), (0, 200, 0), -1)
                            # Vien nhe
                            cv2.rectangle(minimap, (x, y), (x2, y2), (0, 255, 0), 1)
                        
                        # Ve vi tri hien tai (cham do)
                        curr_row = self.current_y // self.step_size
                        curr_col = self.current_x // self.step_size
                        grid_row = curr_row - self.min_row + margin_cells
                        grid_col = curr_col - self.min_col + margin_cells
                        
                        center_x_map = offset_x + int((grid_col + 0.5) * scale)
                        center_y_map = offset_y + int((grid_row + 0.5) * scale)
                        
                        # Vong tron ngoai (trang)
                        cv2.circle(minimap, (center_x_map, center_y_map), 8, (255, 255, 255), 2)
                        # Vong tron trong (do)
                        cv2.circle(minimap, (center_x_map, center_y_map), 5, (0, 0, 255), -1)
                        
                        # Hien thi thong tin scan coverage
                        coverage_text = f"Coverage: {len(self.scan_map)} tiles"
                        cv2.putText(minimap, coverage_text, (10, minimap_size - 10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
                else:
                    # Chua co du lieu
                    text = "No scan data"
                    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
                    text_x = (minimap_size - text_size[0]) // 2
                    text_y = (minimap_size + text_size[1]) // 2
                    cv2.putText(minimap, text, (text_x, text_y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)
                
                # Tieu de minimap
                cv2.putText(minimap, "SCAN MAP", (10, 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Chu thich mau
                legend_y = 50
                cv2.rectangle(minimap, (10, legend_y), (25, legend_y+10), (0, 200, 0), -1)
                cv2.putText(minimap, "Scanned", (30, legend_y+10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
                
                cv2.circle(minimap, (17, legend_y+25), 5, (0, 0, 255), -1)
                cv2.putText(minimap, "Current", (30, legend_y+30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
                
                # Chen minimap vao goc phai duoi cua display
                if h > minimap_size + minimap_margin and w > minimap_size + minimap_margin:
                    # Tao vung trong suot (blending)
                    alpha = 0.95
                    y1 = h - minimap_size - minimap_margin
                    y2 = h - minimap_margin
                    x1 = w - minimap_size - minimap_margin
                    x2 = w - minimap_margin
                    
                    # Blend minimap voi display
                    display[y1:y2, x1:x2] = cv2.addWeighted(
                        display[y1:y2, x1:x2], 1-alpha,
                        minimap, alpha, 0
                    )
                
                cv2.imshow('Auto Scan - Continuous', display)
                
                # Xu ly phim
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('s') or key == ord('S'):
                    self.is_scanning = True
                    print("[START] Bat dau quet...")
                    
                elif key == ord('p') or key == ord('P'):
                    self.is_scanning = False
                    print("[PAUSE] Tam dung...")
                    
                elif key == ord('r') or key == ord('R'):
                    print("[RESET] Bat dau lai tu dau...")
                    self.current_x = 0
                    self.current_y = 0
                    self.tiles = []
                    self.tile_counter = 0
                    self.total_tiles_captured = 0
                    self.prev_frame = None
                    accumulated_dx = 0
                    accumulated_dy = 0
                    # Reset scan map
                    self.scan_map = {}
                    self.min_row, self.max_row = 0, 0
                    self.min_col, self.max_col = 0, 0
                    
                elif key == ord('g') or key == ord('G'):
                    if not self.is_scanning:
                        print("\n[GENERATE] Tao cac levels...")
                        self.generate_lower_levels()
                    else:
                        print("[WARNING] Hay tam dung quet truoc khi generate!")
                    
                elif key == ord('q') or key == ord('Q'):
                    print("\n[QUIT] Ket thuc...")
                    break
                
                # Xu ly auto scan
                if self.is_scanning:
                    # Phat hien movement
                    movement = self.detect_movement(frame)
                    
                    if movement is not None:
                        dx, dy = movement
                        accumulated_dx += dx
                        accumulated_dy += dy
                        
                        # Kiem tra xem co nen chup khong
                        if self.should_capture(accumulated_dx, accumulated_dy):
                            self.capture_tile(frame, accumulated_dx, accumulated_dy)
                            # Reset accumulator
                            accumulated_dx = 0
                            accumulated_dy = 0
                            
        except KeyboardInterrupt:
            print("\n[!] Ngat boi nguoi dung!")
            
        finally:
            cap.release()
            cv2.destroyAllWindows()
            
            # Luu metadata
            if len(self.tiles) > 0:
                self.save_metadata()
                
                print("\n" + "="*70)
                print("HOAN THANH!")
                print("="*70)
                print(f"\nThong ke:")
                print(f"  Tong tiles Level 0: {len(self.tiles)}")
                print(f"  Thu muc: {self.output_dir}")
                print(f"\nBuoc tiep theo:")
                print(f"  1. Tao cac levels (neu chua tao): Nhan G truoc khi thoat")
                print(f"  2. Ghep anh:")
                print(f"     py stitch_landingmed_final.py")
                print()
            else:
                print("\n[WARNING] Khong co du lieu de luu!")


def main():
    # Tham so
    output_dir = "scan_output"
    camera_id = 0
    tile_size = 1024  # Kich thuoc tile nhu LandingMed Level 0
    overlap_percent = 0.1  # 10% overlap
    
    # Kiem tra tham so dong lenh
    if len(sys.argv) > 1:
        try:
            camera_id = int(sys.argv[1])
        except:
            pass
    
    if len(sys.argv) > 2:
        try:
            tile_size = int(sys.argv[2])
        except:
            pass
    
    if len(sys.argv) > 3:
        try:
            overlap_percent = float(sys.argv[3])
        except:
            pass
    
    if len(sys.argv) > 4:
        output_dir = sys.argv[4]
    
    # Chay chuong trinh
    scanner = ContinuousScanner(
        output_dir=output_dir,
        tile_size=tile_size,
        overlap_percent=overlap_percent
    )
    scanner.run(camera_id=camera_id)


if __name__ == "__main__":
    main()
