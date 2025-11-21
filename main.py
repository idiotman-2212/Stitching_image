import cv2
import os
import time
from camera_capture import Camera
from stitcher import ImageStitcher
from fast_stitcher import FastStitcher
from comparator import ImageComparator

def main():
    # Configuration
    IMAGE_FOLDER = "image" # Folder containing images for simulation
    ORIGINAL_IMAGE_PATH = "original.jpg" # Path to the ground truth image
    USE_SIMULATION = True # Set to False to use real webcam (index 0)
    USE_FAST_STITCHER = True # Set to True for faster stitching (recommended)

    # Initialize components
    if USE_SIMULATION and os.path.exists(IMAGE_FOLDER):
        print(f"Initializing Camera in Simulation Mode using folder: {IMAGE_FOLDER}")
        cam = Camera(source=IMAGE_FOLDER)
    else:
        print("Initializing Camera (Webcam)")
        cam = Camera(source=0)

    if USE_FAST_STITCHER:
        print("Using FastStitcher (optimized for speed)")
        stitcher = FastStitcher()
    else:
        print("Using standard OpenCV Stitcher")
        stitcher = ImageStitcher()
    
    comparator = ImageComparator()

    # Load Original Image for comparison
    original_img = None
    if os.path.exists(ORIGINAL_IMAGE_PATH):
        original_img = cv2.imread(ORIGINAL_IMAGE_PATH)
        print(f"Loaded original image from {ORIGINAL_IMAGE_PATH}")
    else:
        print(f"Warning: Original image not found at {ORIGINAL_IMAGE_PATH}. Comparison will be skipped.")

    cam.start()
    
    print("Controls:")
    print("  Press 'c' to capture a frame (or it will auto-capture in simulation)")
    print("  Press 's' to stitch captured images")
    print("  Press 'q' to quit")

    captured_frames = []

    while True:
        # In simulation mode, we might want to control the speed or trigger manually
        # For this demo, let's show the stream and capture on 'c' or auto-capture if it's a video stream
        
        frame = cam.get_frame()
        
        if frame is None:
            if cam.is_simulation:
                print("End of simulation stream.")
                break
            else:
                print("Failed to grab frame")
                break

        # Show the live feed
        cv2.imshow("Camera Feed", frame)
        
        key = cv2.waitKey(100) & 0xFF # Wait 100ms

        # Auto-capture in simulation for demo purposes (or manual 'c')
        # Let's make it manual 'c' for better control, or auto if user wants.
        # The user said "chụp liên tục" (continuous). 
        # Let's capture every frame in simulation mode automatically to show the flow.
        if cam.is_simulation:
            print("Auto-capturing frame...")
            captured_frames.append(frame)
            stitcher.add_image(frame)
            cv2.imshow("Last Captured", frame)
            time.sleep(0.05) # Slow down a bit
        elif key == ord('c'):
            print("Capturing frame...")
            captured_frames.append(frame)
            stitcher.add_image(frame)
            cv2.imshow("Last Captured", frame)

        if key == ord('s') or (cam.is_simulation and len(captured_frames) >= len(cam.image_files) and len(captured_frames) > 0):
            # Perform stitching
            print("Stitching images...")
            result, error = stitcher.stitch()
            
            if result is not None:
                cv2.imshow("Stitched Result", result)
                cv2.imwrite("stitched_output.jpg", result)
                print("Stitched image saved to stitched_output.jpg")

                # Compare if original exists
                if original_img is not None:
                    score, diff = comparator.compare(original_img, result)
                    print(f"Similarity Score (SSIM): {score:.4f}")
                    cv2.imshow("Difference Map", diff)
                else:
                    print("Skipping comparison (no original image).")
                
                print("Press any key to continue (or wait 3s)...")
                cv2.waitKey(3000)
            else:
                print(f"Stitching failed: {error}")
            
            # If simulation, we might want to stop after stitching
            if cam.is_simulation:
                break

        if key == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
