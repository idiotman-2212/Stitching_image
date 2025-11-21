import cv2
import os
import time
from camera_capture import Camera
from stitcher import ImageStitcher
from comparator import ImageComparator

def main():
    # Configuration
    IMAGE_FOLDER = "image"  # Folder containing images for simulation
    ORIGINAL_IMAGE_PATH = "original.jpg"  # Path to the ground truth image
    OUTPUT_PATH = "stitched_output.jpg"
    USE_SIMULATION = True  # Set to False to use real webcam (index 0)

    print("=" * 60)
    print("MICROSCOPE SLIDE SCANNER - HEADLESS MODE")
    print("=" * 60)
    
    # Initialize components
    if USE_SIMULATION and os.path.exists(IMAGE_FOLDER):
        print(f"[+] Initializing Camera in Simulation Mode")
        print(f"    Folder: {IMAGE_FOLDER}")
        cam = Camera(source=IMAGE_FOLDER)
    else:
        print("[+] Initializing Camera (Webcam)")
        cam = Camera(source=0)

    print("[+] Using OpenCV Stitcher")
    stitcher = ImageStitcher()
    
    comparator = ImageComparator()

    # Load Original Image for comparison
    original_img = None
    if os.path.exists(ORIGINAL_IMAGE_PATH):
        original_img = cv2.imread(ORIGINAL_IMAGE_PATH)
        print(f"[+] Loaded original image: {ORIGINAL_IMAGE_PATH}")
        print(f"    Size: {original_img.shape[1]}x{original_img.shape[0]}")
    else:
        print(f"[!] Original image not found: {ORIGINAL_IMAGE_PATH}")
        print("    Comparison will be skipped.")

    print("\n" + "=" * 60)
    print("STARTING CAPTURE & STITCHING PROCESS")
    print("=" * 60)
    
    cam.start()
    captured_frames = []
    frame_count = 0

    while True:
        frame = cam.get_frame()
        
        if frame is None:
            if cam.is_simulation:
                print("\n[+] End of simulation stream")
                break
            else:
                print("\n[-] Failed to grab frame")
                break

        # Auto-capture in simulation mode
        if cam.is_simulation:
            frame_count += 1
            print(f"    [{frame_count:2d}] Capturing frame {frame_count}... ", end="")
            captured_frames.append(frame)
            stitcher.add_image(frame)
            print("OK")
            
            time.sleep(0.1)  # Small delay for readability
            
            # Check if we've captured all images
            if len(captured_frames) >= len(cam.image_files):
                break

    print("\n" + "=" * 60)
    print("STITCHING PROCESS")
    print("=" * 60)
    print(f"Total frames captured: {len(captured_frames)}")
    
    if len(captured_frames) < 2:
        print("[-] Need at least 2 images to stitch!")
        cam.release()
        return
    
    print("Processing... This may take a moment...")
    start_time = time.time()
    
    result, error = stitcher.stitch()
    
    elapsed_time = time.time() - start_time
    
    if result is not None:
        print(f"[+] Stitching successful! (Time: {elapsed_time:.2f}s)")
        
        # Save stitched result
        cv2.imwrite(OUTPUT_PATH, result)
        print(f"[+] Stitched image saved: {OUTPUT_PATH}")
        print(f"    Size: {result.shape[1]}x{result.shape[0]}")
        
        print("\n" + "=" * 60)
        print("COMPARISON WITH ORIGINAL")
        print("=" * 60)
        
        # Compare if original exists
        if original_img is not None:
            score, diff = comparator.compare(original_img, result)
            print(f"[+] Similarity Score (SSIM): {score:.4f} ({score*100:.2f}%)")
            
            # Save difference map
            diff_path = "difference_map.jpg"
            cv2.imwrite(diff_path, diff)
            print(f"[+] Difference map saved: {diff_path}")
            
            # Interpretation
            if score > 0.95:
                print("    > Excellent match! Nearly identical.")
            elif score > 0.85:
                print("    > Good match with minor differences.")
            elif score > 0.70:
                print("    > Moderate match with noticeable differences.")
            else:
                print("    > Poor match. Significant differences detected.")
        else:
            print("[!] Skipping comparison (no original image)")
        
        print("\n" + "=" * 60)
        print("PROCESS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"Output files:")
        print(f"    * {OUTPUT_PATH}")
        if original_img is not None:
            print(f"    * difference_map.jpg")
        
    else:
        print(f"[-] Stitching failed: {error}")
        print("\nTroubleshooting tips:")
        print("    * Ensure images have sufficient overlap")
        print("    * Check that images are from the same scene")
        print("    * Try using more images or adjusting camera position")

    cam.release()
    print("\n[+] Camera released. Program finished.")

if __name__ == "__main__":
    main()
