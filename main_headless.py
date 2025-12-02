# -*- coding: utf-8 -*-
"""
MICROSCOPE SLIDE SCANNER - MAIN PROGRAM
=======================================

Chuong trinh chinh de ghep anh tu tiles va so sanh voi anh goc.
Su dung thuat toan ghep grid voi overlap tu dong/thu cong.
"""

import cv2
import os
import sys
import numpy as np
import glob
import math
import time

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Cau hinh mac dinh
DEFAULT_LAYER = 1
DEFAULT_OVERLAP = 512
MAX_JPEG_DIM = 60000

def parse_filename(filename):
    """Parse filename de lay toa do grid (B[L][RRR][CCC]C.jpg)"""
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
        print(f"Dang luu file: {output_path}")
        return cv2.imwrite(output_path, image, [cv2.IMWRITE_JPEG_QUALITY, 95])
    
    print(f"\n[WARNING] Anh qua lon ({w}x{h}) de luu thanh 1 file JPEG!")
    print(f"Dang chia nho thanh cac phan (tiles lon)...")
    
    base, ext = os.path.splitext(output_path)
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

def stitch_layer(layer_num, base_path, overlap=0):
    """Ghep tat ca cac tiles cua mot layer"""
    layer_name = f'L0{layer_num}'
    layer_path = os.path.join(base_path, layer_name)
    
    if not os.path.exists(layer_path):
        print(f"[ERROR] Khong tim thay thu muc: {layer_path}")
        return None
    
    # Tim files
    image_files = glob.glob(os.path.join(layer_path, '*.jpg'))
    image_files.extend(glob.glob(os.path.join(layer_path, '*.JPG')))
    
    if not image_files:
        print(f"[ERROR] Khong co file anh trong {layer_path}")
        return None
    
    print(f"Tim thay {len(image_files)} tiles trong {layer_name}")
    
    # Parse files
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
    
    # Thong tin grid
    grid_height = max_row - min_row + 1
    grid_width = max_col - min_col + 1
    total_tiles = len(tiles)
    
    # Doc tile mau
    sample_img = cv2.imread(list(tiles.values())[0])
    tile_h, tile_w = sample_img.shape[:2]
    
    # Tinh kich thuoc output
    eff_w = tile_w - overlap
    eff_h = tile_h - overlap
    output_w = (grid_width - 1) * eff_w + tile_w
    output_h = (grid_height - 1) * eff_h + tile_h
    output_size_mb = (output_w * output_h * 3) / (1024 * 1024)
    
    print(f"\nThong tin grid:")
    print(f"  Grid: {grid_height}x{grid_width}")
    print(f"  Tile size: {tile_w}x{tile_h}")
    print(f"  Overlap: {overlap} pixels")
    print(f"  Output Resolution: {output_w} x {output_h} pixels")
    print(f"  RAM can thiet: {output_size_mb:.1f} MB")
    
    if output_size_mb > 10000:
        print(f"\n[WARNING] Anh qua lon (>10GB)! Co the gay loi bo nho.")
    
    # Tao canvas
    try:
        print(f"\nDang tao canvas...")
        canvas = np.zeros((output_h, output_w, 3), dtype=np.uint8)
    except MemoryError:
        print(f"[ERROR] Khong du bo nho RAM!")
        return None
    
    # Ghep tiles
    print(f"Dang ghep {total_tiles} tiles...")
    tiles_processed = 0
    progress_interval = max(1, total_tiles // 20)
    
    for (row, col), img_path in sorted(tiles.items()):
        img = cv2.imread(img_path)
        if img is not None:
            y = (row - min_row) * eff_h
            x = (col - min_col) * eff_w
            
            # Resize neu can
            if img.shape[0] != tile_h or img.shape[1] != tile_w:
                img = cv2.resize(img, (tile_w, tile_h))
            
            # Paste
            if y + tile_h <= output_h and x + tile_w <= output_w:
                canvas[y:y+tile_h, x:x+tile_w] = img
                tiles_processed += 1
            
            if tiles_processed % progress_interval == 0:
                print(f"  Tien trinh: {tiles_processed}/{total_tiles} ({(tiles_processed/total_tiles)*100:.1f}%)")
                
    print(f"Da ghep: {tiles_processed} tiles")
    return canvas

def compare_with_original(stitched_img, original_path):
    """So sanh anh ghep voi anh goc L07"""
    if not os.path.exists(original_path):
        print(f"[WARNING] Khong tim thay anh goc: {original_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"SO SANH VOI ANH GOC (L07)")
    print(f"{'='*60}")
    
    original = cv2.imread(original_path)
    if original is None:
        print("[ERROR] Khong the doc anh goc")
        return
        
    print(f"Anh ghep: {stitched_img.shape[1]}x{stitched_img.shape[0]}")
    print(f"Anh goc: {original.shape[1]}x{original.shape[0]}")
    
    # Resize anh ghep xuong kich thuoc anh goc de so sanh
    print("Dang resize anh ghep de so sanh...")
    stitched_resized = cv2.resize(stitched_img, (original.shape[1], original.shape[0]))
    
    # Tinh do tuong dong
    print("Dang tinh do tuong dong...")
    diff = cv2.absdiff(stitched_resized, original)
    mean_diff = np.mean(diff)
    similarity = 100 * (1 - mean_diff / 255)
    
    print(f"\nKET QUA SO SANH:")
    print(f"  Do sai lech trung binh (Mean Diff): {mean_diff:.2f}")
    print(f"  Do tuong dong (Similarity): {similarity:.2f}%")
    
    if similarity > 95:
        print("  => RẤT TỐT (Excellent match)")
    elif similarity > 85:
        print("  => KHÁ TỐT (Good match)")
    elif similarity > 70:
        print("  => TRUNG BÌNH (Moderate match)")
    else:
        print("  => KÉM (Poor match)")
        
    # Luu anh so sanh
    cv2.imwrite("comparison_diff.jpg", diff)
    print("Da luu anh so sanh: comparison_diff.jpg")

def main():
    print("=" * 60)
    print("HE THONG GHEP ANH MICROSCOPE (GRID STITCHING)")
    print("=" * 60)
    
    # Cau hinh duong dan
    base_path = r'f:\Backup\DELL\ABT\Stitching_image\image\YFB-T001\YFB-T001\Blocks'
    output_dir = r'f:\Backup\DELL\ABT\Stitching_image'
    original_path = os.path.join(base_path, 'L07', 'B7000000C.jpg')
    
    # Xu ly tham so dong lenh
    layer = DEFAULT_LAYER
    overlap = DEFAULT_OVERLAP
    
    if len(sys.argv) > 1:
        try:
            layer = int(sys.argv[1])
        except: pass
        
    if len(sys.argv) > 2:
        try:
            overlap = int(sys.argv[2])
        except: pass
        
    output_path = os.path.join(output_dir, f'stitched_result_L0{layer}.jpg')
    
    print(f"Cau hinh:")
    print(f"  Layer: L0{layer}")
    print(f"  Overlap: {overlap} pixels")
    print(f"  Input: {base_path}")
    print(f"  Output: {output_path}")
    
    # Thuc hien ghep anh
    start_time = time.time()
    result = stitch_layer(layer, base_path, overlap)
    
    if result is not None:
        # Luu ket qua
        save_large_image(result, output_path)
        
        elapsed = time.time() - start_time
        print(f"\nThoi gian xu ly: {elapsed:.1f} giay")
        
        # So sanh voi anh goc
        compare_with_original(result, original_path)
        
        print(f"\n[SUCCESS] Hoan thanh! File da luu tai:\n{output_path}")
    else:
        print(f"\n[FAILED] Ghep anh that bai!")

if __name__ == "__main__":
    main()
