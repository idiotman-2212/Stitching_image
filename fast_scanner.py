# -*- coding: utf-8 -*-
"""
FAST CONTINUOUS SCANNER - Chup LIEN TUC khi di chuyen
======================================================
- Chup LIEN TUC (khong doi dung)
- Scan map TO va RO
- Luu anh NGAY vao scan_output
- Nhanh nhu video Microvisioneer
"""
import cv2
import numpy as np
import os
import json
import sys
import time

print("="*70, flush=True)
print("FAST CONTINUOUS SCANNER", flush=True)
print("="*70, flush=True)

# Config
camera_id = 1
tile_size = 512
step_size = 100  # Chup moi 300px = NHANH HON!
output_dir = "scan_output"

if len(sys.argv) > 1:
    camera_id = int(sys.argv[1])
if len(sys.argv) > 2:
    tile_size = int(sys.argv[2])
if len(sys.argv) > 3:
    step_size = int(sys.argv[3])

print(f"Camera: {camera_id}", flush=True)
print(f"Tile: {tile_size}x{tile_size}", flush=True)
print(f"Step: {step_size}px (chup moi {step_size}px di chuyen)", flush=True)

# Create dirs
os.makedirs(output_dir, exist_ok=True)
os.makedirs(os.path.join(output_dir, 'Blocks', 'L00'), exist_ok=True)
os.makedirs(os.path.join(output_dir, 'Data'), exist_ok=True)

# Open camera
print(f"\nOpening camera {camera_id}...", flush=True)
cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("[ERROR] Cannot open camera!", flush=True)
    sys.exit(1)

# Camera settings - FAST exposure for less blur
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 30)

camera_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
camera_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"[OK] Camera: {camera_w}x{camera_h}", flush=True)

# State
current_x = 0.0
current_y = 0.0
tile_count = 0
tiles = []

scan_map = {}
min_row, max_row = 0, 0
min_col, max_col = 0, 0

# Motion tracking - SIMPLE and FAST
detector = cv2.ORB_create(nfeatures=300)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
prev_kp = None
prev_desc = None

accumulated_dist = 0.0

def capture_tile(frame):
    """Capture and save tile IMMEDIATELY"""
    global tile_count, min_row, max_row, min_col, max_col
    
    h, w = frame.shape[:2]
    cx, cy = w // 2, h // 2
    half = tile_size // 2
    
    x1 = max(0, cx - half)
    y1 = max(0, cy - half)
    x2 = min(w, cx + half)
    y2 = min(h, cy + half)
    
    tile = frame[y1:y2, x1:x2].copy()
    
    if tile.shape[0] != tile_size or tile.shape[1] != tile_size:
        tile = cv2.resize(tile, (tile_size, tile_size))
    
    # SAVE IMMEDIATELY!
    filename = f"B0{tile_count:06X}C.jpg"
    filepath = os.path.join(output_dir, 'Blocks', 'L00', filename)
    cv2.imwrite(filepath, tile, [cv2.IMWRITE_JPEG_QUALITY, 90])
    
    row = int(current_y / step_size)
    col = int(current_x / step_size)
    
    tiles.append({
        "Index": tile_count,
        "Level": 0,
        "Row": row,
        "Coloumn": col,
        "CoreX": int(current_x),
        "CoreY": int(current_y),
        "ImageName": filename
    })
    
    scan_map[(row, col)] = True
    
    if len(scan_map) == 1:
        min_row = max_row = row
        min_col = max_col = col
    else:
        min_row = min(min_row, row)
        max_row = max(max_row, row)
        min_col = min(min_col, col)
        max_col = max(max_col, col)
    
    tile_count += 1
    print(f"[CAPTURE] Tile #{tile_count} saved to {filename}", flush=True)
    
    return row, col

def draw_minimap(display):
    """Draw LARGE minimap on display"""
    h, w = display.shape[:2]
    
    # LARGE minimap
    map_size = min(350, h - 100)
    minimap = np.zeros((map_size, map_size, 3), dtype=np.uint8)
    minimap[:,:] = [20, 20, 20]
    
    # Border
    cv2.rectangle(minimap, (0, 0), (map_size-1, map_size-1), (100, 100, 100), 2)
    
    # Title
    cv2.putText(minimap, f"SCAN MAP ({tile_count} tiles)", (10, 25),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    if len(scan_map) > 0:
        # Calculate grid
        map_h = max_row - min_row + 1
        map_w = max_col - min_col + 1
        
        margin = 2
        total_h = map_h + margin * 2
        total_w = map_w + margin * 2
        
        # Cell size
        usable = map_size - 60
        cell_size = max(5, min(usable // max(total_w, 1), usable // max(total_h, 1)))
        
        grid_w = total_w * cell_size
        grid_h = total_h * cell_size
        offset_x = (map_size - grid_w) // 2
        offset_y = (map_size - grid_h) // 2 + 25
        
        # Draw grid background
        cv2.rectangle(minimap, (offset_x, offset_y), 
                     (offset_x + grid_w, offset_y + grid_h), (40, 40, 40), -1)
        
        # Draw scanned cells
        for (r, c) in scan_map.keys():
            gr = r - min_row + margin
            gc = c - min_col + margin
            
            x = offset_x + gc * cell_size
            y = offset_y + gr * cell_size
            
            # Filled green cell
            cv2.rectangle(minimap, (x+1, y+1), 
                         (x+cell_size-1, y+cell_size-1), (0, 200, 0), -1)
            cv2.rectangle(minimap, (x, y), 
                         (x+cell_size, y+cell_size), (0, 255, 0), 1)
        
        # Current position (red dot)
        curr_row = int(current_y / step_size)
        curr_col = int(current_x / step_size)
        cr = curr_row - min_row + margin
        cc = curr_col - min_col + margin
        
        cx = offset_x + cc * cell_size + cell_size // 2
        cy = offset_y + cr * cell_size + cell_size // 2
        
        cv2.circle(minimap, (cx, cy), max(3, cell_size//3), (0, 0, 255), -1)
        cv2.circle(minimap, (cx, cy), max(5, cell_size//2), (255, 255, 255), 2)
    
    # Progress bar
    progress = int(accumulated_dist / step_size * (map_size - 20))
    progress = min(progress, map_size - 20)
    cv2.rectangle(minimap, (10, map_size - 20), (10 + progress, map_size - 10), (0, 255, 255), -1)
    cv2.rectangle(minimap, (10, map_size - 20), (map_size - 10, map_size - 10), (100, 100, 100), 1)
    
    # Overlay on display
    y1 = h - map_size - 10
    x1 = w - map_size - 10
    if y1 > 0 and x1 > 0:
        display[y1:y1+map_size, x1:x1+map_size] = minimap
    
    return display

print("\n" + "="*70, flush=True)
print("HUONG DAN:", flush=True)
print("  - Di chuyen stage LIEN TUC", flush=True)
print("  - He thong TU DONG CHUP moi 300px", flush=True)
print("  - Xem SCAN MAP o goc phai duoi", flush=True)
print("  - Nhan [Q] de thoat", flush=True)
print("="*70, flush=True)
print("\nBat dau quet...", flush=True)

frame_count = 0
last_status = time.time()

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        
        frame_count += 1
        display = frame.copy()
        
        # Motion detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        kp, desc = detector.detectAndCompute(gray, None)
        
        dx, dy = 0, 0
        
        if prev_kp is not None and prev_desc is not None and desc is not None:
            if len(kp) >= 10 and len(prev_kp) >= 10:
                try:
                    matches = bf.match(prev_desc, desc)
                    if len(matches) >= 5:
                        matches = sorted(matches, key=lambda x: x.distance)[:30]
                        
                        dx_list = []
                        dy_list = []
                        for m in matches:
                            pt1 = prev_kp[m.queryIdx].pt
                            pt2 = kp[m.trainIdx].pt
                            dx_list.append(pt2[0] - pt1[0])
                            dy_list.append(pt2[1] - pt1[1])
                        
                        dx = -np.median(dx_list)
                        dy = -np.median(dy_list)
                except:
                    pass
        
        prev_kp = kp
        prev_desc = desc
        
        # Update position
        current_x += dx
        current_y += dy
        accumulated_dist += np.sqrt(dx**2 + dy**2)
        
        # AUTO CAPTURE when moved enough
        if accumulated_dist >= step_size:
            row, col = capture_tile(frame)
            accumulated_dist = 0
        
        # Draw UI
        h, w = display.shape[:2]
        
        # Status bar
        cv2.rectangle(display, (0, 0), (w, 60), (0, 0, 0), -1)
        cv2.putText(display, f"Tiles: {tile_count} | Pos: ({int(current_x)}, {int(current_y)})",
                   (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(display, f"Progress: {int(accumulated_dist)}/{step_size}px | [Q]=Quit",
                   (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Tile boundary
        cx, cy = w // 2, h // 2
        half = min(tile_size, min(w, h)) // 4
        cv2.rectangle(display, (cx-half, cy-half), (cx+half, cy+half), (0, 255, 0), 2)
        
        # Crosshair
        cv2.line(display, (cx-20, cy), (cx+20, cy), (0, 255, 255), 2)
        cv2.line(display, (cx, cy-20), (cx, cy+20), (0, 255, 255), 2)
        
        # Draw minimap
        display = draw_minimap(display)
        
        # Show
        cv2.imshow('Fast Continuous Scanner', display)
        
        # Status update
        if time.time() - last_status > 2:
            print(f"[STATUS] Tiles: {tile_count} | Pos: ({int(current_x)}, {int(current_y)})", flush=True)
            last_status = time.time()
        
        # Keys
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord(' '):
            capture_tile(frame)
            accumulated_dist = 0

except KeyboardInterrupt:
    print("\n[STOPPED]", flush=True)
except Exception as e:
    print(f"\n[ERROR] {e}", flush=True)
    import traceback
    traceback.print_exc()
finally:
    cap.release()
    cv2.destroyAllWindows()
    
    if tile_count > 0:
        # Save metadata
        json_path = os.path.join(output_dir, 'Data', 'BlocksJson.json')
        with open(json_path, 'w') as f:
            json.dump(tiles, f, indent=2)
        
        print(f"\n" + "="*70, flush=True)
        print(f"DONE! {tile_count} tiles saved", flush=True)
        print(f"Tiles: {output_dir}/Blocks/L00/", flush=True)
        print(f"Metadata: {output_dir}/Data/BlocksJson.json", flush=True)
        print("="*70, flush=True)
    else:
        print("\n[WARNING] No tiles captured!", flush=True)
