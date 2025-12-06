# -*- coding: utf-8 -*-
"""
GHEP ANH THEO METADATA LANDING-MED - PHIEN BAN HOAN CHINH
==========================================================
Su dung BlocksJson.json de ghep anh chinh xac nhu phan mem goc
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
    print("Doc metadata tu BlocksJson.json...")
    sys.stdout.flush()
    
    with open(json_path, 'r', encoding='utf-8') as f:
        blocks = json.load(f)
    
    print(f"  Tim thay {len(blocks)} blocks trong metadata")
    sys.stdout.flush()
    return blocks

def stitch_level(level, blocks_all, blocks_folder, output_path):
    """
    Ghep tat ca tiles cua mot level
    
    Args:
        level: Level can ghep (0-7)
        blocks_all: Danh sach tat ca blocks tu metadata
        blocks_folder: Thu muc chua cac file anh
        output_path: Duong dan luu file
    """
    print(f"\n{'='*70}")
    print(f"GHEP LEVEL {level} (L0{level})")
    print(f"{'='*70}")
    sys.stdout.flush()
    
    # Loc blocks theo level
    level_blocks = [b for b in blocks_all if b.get('Level') == level]
    
    if not level_blocks:
        print(f"[ERROR] Khong tim thay blocks cho Level {level}")
        return None
    
    print(f"So luong blocks: {len(level_blocks)}")
    sys.stdout.flush()
    
    # Lay thong tin tu block dau tien
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
    metadata_h = sample_block['ImageHeight']
    
    # Tinh ty le scale
    scale_x = actual_w / metadata_w
    scale_y = actual_h / metadata_h
    
    print(f"\nThong tin tiles:")
    print(f"  Kich thuoc thuc te (file .jpg): {actual_w} x {actual_h}")
    print(f"  Kich thuoc metadata: {metadata_w} x {metadata_h}")
    print(f"  Scale factor: {scale_x:.6f}")
    sys.stdout.flush()
    
    # Tim min/max toa do tu metadata
    min_x = min(b['ImageX'] for b in level_blocks)
    min_y = min(b['ImageY'] for b in level_blocks)
    max_x = max(b['ImageX'] + b['ImageWidth'] for b in level_blocks)
    max_y = max(b['ImageY'] + b['ImageHeight'] for b in level_blocks)
    
    # Tinh kich thuoc canvas sau khi scale
    canvas_w = int((max_x - min_x) * scale_x)
    canvas_h = int((max_y - min_y) * scale_y)
    canvas_size_mb = (canvas_w * canvas_h * 3) / (1024**2)
    
    print(f"\nThong tin canvas:")
    print(f"  Toa do metadata: ({min_x}, {min_y}) -> ({max_x}, {max_y})")
    print(f"  Kich thuoc canvas: {canvas_w} x {canvas_h} pixels")
    print(f"  Dung luong RAM: {canvas_size_mb:.1f} MB")
    sys.stdout.flush()
    
    # Kiem tra RAM
    if canvas_size_mb > 10000:  # >10GB
        print(f"\n[WARNING] Canvas rat lon ({canvas_size_mb/1024:.1f} GB)!")
        print("Co the gay loi Memory. Khuyen nghi dung level cao hon (L02 hoac L03)")
        response = input("Ban co muon tiep tuc? (y/n): ")
        if response.lower() != 'y':
            return None
    
    # Tao canvas
    print(f"\nTao canvas {canvas_w}x{canvas_h}...")
    sys.stdout.flush()
    
    try:
        canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
        # Background trang nhu trong metadata
        canvas[:, :] = [240, 240, 240]
    except MemoryError:
        print("[ERROR] Khong du RAM de tao canvas!")
        print("Hay thu voi level cao hon (it tiles hon)")
        return None
    
    # Ghep cac tiles
    print(f"\nGhep {len(level_blocks)} tiles...")
    sys.stdout.flush()
    
    processed = 0
    failed = 0
    progress_interval = max(1, len(level_blocks) // 20)
    
    for i, block in enumerate(sorted(level_blocks, key=lambda b: (b['Row'], b['Coloumn']))):
        img_name = block['ImageName']
        img_path = os.path.join(blocks_folder, f'L0{level}', img_name)
        
        # Doc anh
        img = cv2.imread(img_path)
        if img is None:
            failed += 1
            continue
        
        # Tinh vi tri tren canvas (scale toa do metadata)
        x = int((block['ImageX'] - min_x) * scale_x)
        y = int((block['ImageY'] - min_y) * scale_y)
        
        h, w = img.shape[:2]
        
        # Paste vao canvas (khong resize tile)
        if y + h <= canvas_h and x + w <= canvas_w:
            canvas[y:y+h, x:x+w] = img
            processed += 1
        else:
            failed += 1
        
        # Hien thi tien trinh
        if (i + 1) % progress_interval == 0:
            percent = 100 * (i + 1) / len(level_blocks)
            print(f"  Tien trinh: {i+1}/{len(level_blocks)} ({percent:.1f}%)")
            sys.stdout.flush()
    
    print(f"\nKet qua:")
    print(f"  Thanh cong: {processed} tiles")
    print(f"  That bai: {failed} tiles")
    sys.stdout.flush()
    
    # Luu ket qua
    print(f"\nDang luu ket qua...")
    sys.stdout.flush()
    
    success = cv2.imwrite(output_path, canvas, [cv2.IMWRITE_JPEG_QUALITY, 95])
    
    if success:
        file_size = os.path.getsize(output_path) / (1024**2)
        print(f"[SUCCESS] Da luu thanh cong!")
        print(f"  File: {output_path}")
        print(f"  Kich thuoc: {file_size:.1f} MB")
        sys.stdout.flush()
        return canvas
    else:
        print(f"[ERROR] Khong the luu file!")
        return None

def compare_with_original(stitched, original_path):
    """So sanh voi anh goc L07"""
    if not os.path.exists(original_path):
        return
    
    print(f"\n{'='*70}")
    print("SO SANH VOI ANH GOC L07")
    print(f"{'='*70}")
    
    original = cv2.imread(original_path)
    if original is None:
        return
    
    # Resize xuong kich thuoc L07
    stitched_resized = cv2.resize(stitched, (original.shape[1], original.shape[0]))
    
    # Tinh do tuong dong
    diff = cv2.absdiff(stitched_resized, original)
    mean_diff = np.mean(diff)
    similarity = 100 * (1 - mean_diff / 255)
    
    print(f"Do tuong dong: {similarity:.2f}%")
    
    if similarity > 95:
        print("=> EXCELLENT (Rat giong)")
    elif similarity > 85:
        print("=> GOOD (Tot)")
    elif similarity > 70:
        print("=> FAIR (Kha)")
    else:
        print("=> POOR (Can kiem tra lai)")

def main():
    print("="*70)
    print("HE THONG GHEP ANH - LANDING MED COMPATIBLE")
    print("="*70)
    print("Ghep anh dung theo metadata BlocksJson.json")
    print("="*70)
    sys.stdout.flush()
    
    # Cau hinh duong dan
    base_path = r'f:\Backup\DELL\ABT\Stitching_image\image\YFB-T001\YFB-T001'
    blocks_json = os.path.join(base_path, 'Data', 'BlocksJson.json')
    blocks_folder = os.path.join(base_path, 'Blocks')
    output_dir = r'f:\Backup\DELL\ABT\Stitching_image'
    original_path = os.path.join(blocks_folder, 'L07', 'B7000000C.jpg')
    
    # Lay level tu tham so dong lenh
    level = 1  # Mac dinh L01
    if len(sys.argv) > 1:
        try:
            level = int(sys.argv[1])
            if level < 0 or level > 7:
                print(f"[ERROR] Level phai tu 0 den 7!")
                return
        except:
            print(f"[ERROR] Tham so khong hop le!")
            return
    
    output_path = os.path.join(output_dir, f'landingmed_L0{level}_final.jpg')
    
    print(f"\nCau hinh:")
    print(f"  Level: {level}")
    print(f"  Metadata: {blocks_json}")
    print(f"  Output: {output_path}")
    print()
    sys.stdout.flush()
    
    # Kiem tra file ton tai
    if not os.path.exists(blocks_json):
        print(f"[ERROR] Khong tim thay file metadata: {blocks_json}")
        return
    
    # Doc metadata
    blocks_all = load_metadata(blocks_json)
    
    # Ghep anh
    start_time = time.time()
    result = stitch_level(level, blocks_all, blocks_folder, output_path)
    elapsed = time.time() - start_time
    
    if result is not None:
        print(f"\nThoi gian xu ly: {elapsed:.1f} giay")
        
        # So sanh voi L07
        if level != 7:
            compare_with_original(result, original_path)
        
        print(f"\n{'='*70}")
        print("HOAN THANH!")
        print(f"{'='*70}")
        print(f"\nGhi chu:")
        print(f"  - Level 0 (L00): Chi tiet nhat, nhung file rat lon")
        print(f"  - Level 1 (L01): Tot nhat cho su dung chung")
        print(f"  - Level 2-3: Cho xem tong quan")
        print(f"  - Level 7 (L07): Anh goc overview")
    else:
        print(f"\n[FAILED] Ghep anh that bai!")

if __name__ == "__main__":
    main()
