# -*- coding: utf-8 -*-
"""
MAIN PROGRAM - SU DUNG METADATA LANDING-MED
============================================
Ghep anh chinh xac theo BlocksJson.json va so sanh voi anh goc
"""
import cv2
import os
import json
import numpy as np
import sys
import time

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def load_metadata(json_path):
    """Doc metadata tu BlocksJson.json"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def stitch_from_metadata(level, blocks_all, blocks_folder):
    """
    Ghep anh tu metadata
    
    Returns:
        canvas (numpy array) hoac None neu that bai
    """
    # Loc blocks theo level
    level_blocks = [b for b in blocks_all if b.get('Level') == level]
    
    if not level_blocks:
        print(f"[ERROR] Khong tim thay blocks cho Level {level}")
        return None
    
    print(f"  So luong tiles: {len(level_blocks)}")
    
    # Lay thong tin tu sample
    sample_block = level_blocks[0]
    sample_path = os.path.join(blocks_folder, f'L0{level}', sample_block['ImageName'])
    
    if not os.path.exists(sample_path):
        print(f"[ERROR] Khong tim thay file: {sample_path}")
        return None
    
    sample_img = cv2.imread(sample_path)
    
    if sample_img is None:
        print(f"[ERROR] Khong the doc file: {sample_path}")
        return None
    
    actual_h, actual_w = sample_img.shape[:2]
    metadata_w = sample_block['ImageWidth']
    
    # Tinh scale
    scale = actual_w / metadata_w
    print(f"  Scale factor: {scale:.4f}")
    
    # Tinh canvas size
    min_x = min(b['ImageX'] for b in level_blocks)
    min_y = min(b['ImageY'] for b in level_blocks)
    max_x = max(b['ImageX'] + b['ImageWidth'] for b in level_blocks)
    max_y = max(b['ImageY'] + b['ImageHeight'] for b in level_blocks)
    
    canvas_w = int((max_x - min_x) * scale)
    canvas_h = int((max_y - min_y) * scale)
    canvas_size_mb = (canvas_w * canvas_h * 3) / (1024**2)
    
    print(f"  Canvas: {canvas_w} x {canvas_h} pixels")
    print(f"  RAM can thiet: {canvas_size_mb:.1f} MB")
    
    # Canh bao neu qua lon
    if canvas_size_mb > 15000:  # >15GB
        print(f"\n[ERROR] Canvas qua lon ({canvas_size_mb/1024:.1f} GB)!")
        print("L00 can rat nhieu RAM. Hay dung L01 hoac L02 thay the.")
        return None
    elif canvas_size_mb > 8000:  # >8GB
        print(f"\n[WARNING] Canvas rat lon ({canvas_size_mb/1024:.1f} GB)")
        print("Dam bao may co du RAM!")
    
    # Tao canvas
    print(f"\n  Dang tao canvas...")
    try:
        canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
        canvas[:, :] = [240, 240, 240]
    except MemoryError:
        print("[ERROR] Khong du RAM de tao canvas!")
        print(f"Can thiet: {canvas_size_mb/1024:.1f} GB RAM")
        print("Khuyen nghi: Dung level cao hon (L01, L02 hoac L03)")
        return None
    
    # Ghep tiles
    print(f"  Dang ghep {len(level_blocks)} tiles...")
    processed = 0
    interval = max(1, len(level_blocks) // 10)
    
    for i, block in enumerate(level_blocks):
        img_path = os.path.join(blocks_folder, f'L0{level}', block['ImageName'])
        img = cv2.imread(img_path)
        
        if img is not None:
            x = int((block['ImageX'] - min_x) * scale)
            y = int((block['ImageY'] - min_y) * scale)
            h, w = img.shape[:2]
            
            if y + h <= canvas_h and x + w <= canvas_w:
                canvas[y:y+h, x:x+w] = img
                processed += 1
        
        if (i + 1) % interval == 0:
            print(f"    {i+1}/{len(level_blocks)} ({100*(i+1)/len(level_blocks):.0f}%)")
    
    print(f"  Da ghep: {processed}/{len(level_blocks)} tiles")
    
    if processed < len(level_blocks) * 0.9:  # <90% thanh cong
        print(f"[WARNING] Chi ghep duoc {100*processed/len(level_blocks):.0f}% tiles")
    
    return canvas

def compare_with_original(stitched, original_path):
    """So sanh voi anh goc"""
    if not os.path.exists(original_path):
        return 0
    
    original = cv2.imread(original_path)
    if original is None:
        return 0
    
    # Resize
    stitched_resized = cv2.resize(stitched, (original.shape[1], original.shape[0]))
    
    # Tinh do tuong dong
    diff = cv2.absdiff(stitched_resized, original)
    similarity = 100 * (1 - np.mean(diff) / 255)
    
    return similarity

def main():
    print("="*70)
    print("HE THONG GHEP ANH MICROSCOPE - LANDING MED COMPATIBLE")
    print("="*70)
    
    # Cau hinh
    base_path = r'f:\Backup\DELL\ABT\Stitching_image\image\YFB-T001\YFB-T001'
    blocks_json = os.path.join(base_path, 'Data', 'BlocksJson.json')
    blocks_folder = os.path.join(base_path, 'Blocks')
    output_dir = r'f:\Backup\DELL\ABT\Stitching_image'
    original_path = os.path.join(blocks_folder, 'L07', 'B7000000C.jpg')
    
    # Tham so
    level = 1  # Mac dinh L01
    if len(sys.argv) > 1:
        try:
            level = int(sys.argv[1])
            if level < 0 or level > 7:
                print("[ERROR] Level phai tu 0 den 7!")
                return
        except:
            print("[ERROR] Tham so khong hop le!")
            return
    
    output_path = os.path.join(output_dir, f'stitched_result_L0{level}.jpg')
    
    print(f"\nCau hinh:")
    print(f"  Level: L0{level}")
    print(f"  Output: {output_path}")
    
    # Kiem tra file
    if not os.path.exists(blocks_json):
        print(f"\n[ERROR] Khong tim thay metadata: {blocks_json}")
        return
    
    # Doc metadata
    print(f"\nDoc metadata...")
    try:
        blocks_all = load_metadata(blocks_json)
        print(f"  Tim thay {len(blocks_all)} blocks")
    except Exception as e:
        print(f"[ERROR] Khong the doc metadata: {e}")
        return
    
    # Ghep anh
    print(f"\nGhep anh Level {level}...")
    start = time.time()
    
    result = stitch_from_metadata(level, blocks_all, blocks_folder)
    
    if result is not None:
        # Luu file
        print(f"\nDang luu file...")
        try:
            success = cv2.imwrite(output_path, result, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            if not success:
                print(f"[ERROR] Khong the luu file: {output_path}")
                return
            
            elapsed = time.time() - start
            file_size = os.path.getsize(output_path) / (1024**2)
            
            print(f"\n{'='*70}")
            print(f"[SUCCESS] HOAN THANH!")
            print(f"{'='*70}")
            print(f"  Thoi gian: {elapsed:.1f} giay")
            print(f"  File: {output_path}")
            print(f"  Kich thuoc: {file_size:.1f} MB")
            
            # So sanh
            if level != 7:
                print(f"\nSo sanh voi anh goc L07...")
                similarity = compare_with_original(result, original_path)
                print(f"  Do tuong dong: {similarity:.2f}%")
                
                if similarity > 95:
                    print("  => EXCELLENT (Rat tot)")
                elif similarity > 85:
                    print("  => GOOD (Tot)")
                elif similarity > 70:
                    print("  => FAIR (Kha)")
                else:
                    print("  => POOR (Can kiem tra lai)")
            
            print(f"\n{'='*70}")
            
        except Exception as e:
            print(f"[ERROR] Loi khi luu file: {e}")
            return
        
    else:
        print(f"\n{'='*70}")
        print(f"[FAILED] GHEP ANH THAT BAI!")
        print(f"{'='*70}")
        
        if level == 0:
            print("\nL00 rat lon va can nhieu RAM (>15GB).")
            print("KHUYEN NGHI: Dung L01 thay the:")
            print("  python main_headless.py 1")
        else:
            print("\nVui long kiem tra:")
            print("  - Du lieu co day du khong?")
            print("  - Co du RAM khong?")

if __name__ == "__main__":
    main()
