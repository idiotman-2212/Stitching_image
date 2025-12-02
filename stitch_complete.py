# -*- coding: utf-8 -*-
"""
CHUONG TRINH GHEP ANH TU TILES - PHIEN BAN HOAN CHINH (V3)
==========================================================

Tinh nang moi:
1. Ho tro Overlap (chong lap) giua cac tiles de sua loi lech anh
2. Tu dong chia nho anh neu kich thuoc qua lon (vuot qua gioi han JPEG)
3. Ho tro chon overlap thu cong hoac tu dong

Su dung:
    python stitch_complete.py [layer] [overlap]
    
Vi du:
    python stitch_complete.py 1 512    # Ghep L01 voi overlap 512px
    python stitch_complete.py 1 0      # Ghep L01 khong overlap (mac dinh)
"""

import cv2
import os
import sys
import numpy as np
import glob
import math

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Gioi han kich thuoc JPEG (an toan)
MAX_JPEG_DIM = 60000

def parse_filename(filename):
    basename = os.path.basename(filename).upper()
    if not basename.startswith('B') or not basename.endswith('.JPG'):
        return None, None, None
    name = basename[1:-5]
    if len(name) != 7:
        return None, None, None
    try:
        layer = int(name[0], 16)
        row = int(name[1:4], 16)
        col = int(name[4:7], 16)
        return layer, row, col
    except ValueError:
        return None, None, None

def save_large_image(image, output_path):
    """Luu anh lon bang cach chia nho neu can"""
    h, w = image.shape[:2]
    
    if h <= MAX_JPEG_DIM and w <= MAX_JPEG_DIM:
        # Luu binh thuong
        print(f"Dang luu file: {output_path}")
        return cv2.imwrite(output_path, image, [cv2.IMWRITE_JPEG_QUALITY, 95])
    
    print(f"\n[WARNING] Anh qua lon ({w}x{h}) de luu thanh 1 file JPEG!")
    print(f"Dang chia nho thanh cac phan (tiles lon)...")
    
    base, ext = os.path.splitext(output_path)
    
    # Chia thanh cac khoi < MAX_JPEG_DIM
    rows = math.ceil(h / MAX_JPEG_DIM)
    cols = math.ceil(w / MAX_JPEG_DIM)
    
    success = True
    for r in range(rows):
        for c in range(cols):
            y_start = r * MAX_JPEG_DIM
            y_end = min((r + 1) * MAX_JPEG_DIM, h)
            x_start = c * MAX_JPEG_DIM
            x_end = min((c + 1) * MAX_JPEG_DIM, w)
            
            part_path = f"{base}_part_{r}_{c}{ext}"
            print(f"  Luu phan {r},{c}: {part_path} ({x_end-x_start}x{y_end-y_start})")
            
            part_img = image[y_start:y_end, x_start:x_end]
            if not cv2.imwrite(part_path, part_img, [cv2.IMWRITE_JPEG_QUALITY, 95]):
                print(f"  [ERROR] Khong the luu {part_path}")
                success = False
                
    return success

def stitch_layer(layer_num, base_path, output_path, overlap=0, progress_interval=100):
    layer_name = f'L0{layer_num}'
    layer_path = os.path.join(base_path, layer_name)
    
    if not os.path.exists(layer_path):
        print(f"[ERROR] Khong tim thay thu muc: {layer_path}")
        return None
    
    image_files = glob.glob(os.path.join(layer_path, '*.jpg'))
    image_files.extend(glob.glob(os.path.join(layer_path, '*.JPG')))
    
    if not image_files:
        print(f"[ERROR] Khong co file anh trong {layer_path}")
        return None
    
    print(f"\n{'='*70}")
    print(f"GHEP LAYER {layer_name} (Overlap: {overlap}px)")
    print(f"{'='*70}")
    
    tiles = {}
    min_row, max_row = float('inf'), -1
    min_col, max_col = float('inf'), -1
    
    for img_path in image_files:
        l, r, c = parse_filename(img_path)
        if l == layer_num and r is not None:
            tiles[(r, c)] = img_path
            min_row = min(min_row, r)
            max_row = max(max_row, r)
            min_col = min(min_col, c)
            max_col = max(max_col, c)
    
    if not tiles:
        print(f"[ERROR] Khong co tile hop le!")
        return None
    
    grid_height = max_row - min_row + 1
    grid_width = max_col - min_col + 1
    total_tiles = len(tiles)
    
    # Doc tile mau
    sample_img = cv2.imread(list(tiles.values())[0])
    tile_h, tile_w = sample_img.shape[:2]
    
    # Tinh kich thuoc output voi overlap
    # Cong thuc: (N-1)*(Tile - Overlap) + Tile
    # = N*Tile - (N-1)*Overlap
    
    eff_w = tile_w - overlap
    eff_h = tile_h - overlap
    
    output_w = (grid_width - 1) * eff_w + tile_w
    output_h = (grid_height - 1) * eff_h + tile_h
    
    output_size_mb = (output_w * output_h * 3) / (1024 * 1024)
    
    print(f"\nThong tin grid:")
    print(f"  Grid: {grid_height}x{grid_width}")
    print(f"  Tile size: {tile_w}x{tile_h}")
    print(f"  Overlap: {overlap} pixels")
    print(f"  Effective size: {eff_w}x{eff_h}")
    print(f"  Output Resolution: {output_w} x {output_h} pixels")
    print(f"  Dung luong RAM can thiet: {output_size_mb:.1f} MB")
    
    if output_size_mb > 10000: # Canh bao neu > 10GB
        print(f"\n[WARNING] Anh qua lon! Co the gay loi bo nho (Memory Error).")
        print(f"Khuyen nghi su dung layer thap hon hoac may co RAM > {output_size_mb/1024 + 4:.0f}GB")
    
    # Tao canvas
    try:
        print(f"\nDang tao canvas...")
        canvas = np.zeros((output_h, output_w, 3), dtype=np.uint8)
    except MemoryError:
        print(f"[ERROR] Khong du bo nho RAM de tao canvas!")
        return None
    
    # Ghep tiles
    print(f"\nDang ghep {total_tiles} tiles...")
    tiles_processed = 0
    
    for (row, col), img_path in sorted(tiles.items()):
        img = cv2.imread(img_path)
        
        if img is not None:
            # Tinh vi tri
            y = (row - min_row) * eff_h
            x = (col - min_col) * eff_w
            
            # Xu ly overlap: Chi paste phan khong overlap (tru hang cuoi/cot cuoi)
            # Hoac don gian la paste de len nhau (cai sau de len cai truoc)
            # De don gian va hieu qua, ta paste toan bo tile
            # Vi thu tu sorted la row tang dan, col tang dan -> paste tu trai sang phai, tren xuong duoi
            # Nen tile sau se de len tile truoc o vung overlap -> OK
            
            h_paste, w_paste = img.shape[:2]
            
            # Resize neu can (phong ngua loi)
            if h_paste != tile_h or w_paste != tile_w:
                img = cv2.resize(img, (tile_w, tile_h))
            
            # Kiem tra bien
            if y + tile_h > output_h or x + tile_w > output_w:
                continue
                
            canvas[y:y+tile_h, x:x+tile_w] = img
            tiles_processed += 1
            
            if tiles_processed % progress_interval == 0:
                print(f"  Tien trinh: {tiles_processed}/{total_tiles} ({(tiles_processed/total_tiles)*100:.1f}%)")
    
    print(f"\nDa ghep: {tiles_processed} tiles")
    
    # Luu ket qua
    save_large_image(canvas, output_path)
    return canvas

if __name__ == "__main__":
    base_path = r'f:\Backup\DELL\ABT\Stitching_image\image\YFB-T001\YFB-T001\Blocks'
    output_dir = r'f:\Backup\DELL\ABT\Stitching_image'
    
    layer = 1
    overlap = 0
    
    if len(sys.argv) > 1:
        try:
            layer = int(sys.argv[1])
        except: pass
        
    if len(sys.argv) > 2:
        try:
            overlap = int(sys.argv[2])
        except: pass
    
    output_path = os.path.join(output_dir, f'L0{layer}_stitched_complete.jpg')
    
    stitch_layer(layer, base_path, output_path, overlap, progress_interval=100)
