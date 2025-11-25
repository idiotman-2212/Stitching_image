"""
Real-time Microscope Camera Handler
Optimized for Euromex DC.5000F and similar USB microscope cameras
"""

import cv2
import numpy as np
import time

class RealtimeMicroscopeCamera:
    """
    Real-time camera handler for microscope scanning
    Supports live preview, auto-capture, and manual capture
    """
    
    def __init__(self, camera_index=0, resolution=(1920, 1080)):
        """
        Initialize camera
        
        Args:
            camera_index: Camera device index (0, 1, 2...)
            resolution: Desired resolution (width, height)
        """
        self.camera_index = camera_index
        self.target_width, self.target_height = resolution
        self.cap = None
        self.is_running = False
        
        # Performance settings
        self.target_fps = 30
        self.buffer_size = 1  # Minimize latency for real-time
        
        # Camera properties
        self.current_exposure = -6
        self.current_brightness = 128
        self.current_contrast = 128
        
    def list_available_cameras(self):
        """List all available cameras"""
        print("Scanning for cameras...")
        available = []
        
        for i in range(10):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    h, w = frame.shape[:2]
                    available.append({
                        'index': i,
                        'resolution': f"{w}x{h}",
                        'backend': 'DirectShow'
                    })
                    print(f"  Camera {i}: {w}x{h}")
                cap.release()
        
        return available
    
    def start(self):
        """Initialize and start camera"""
        print(f"[Camera] Initializing camera {self.camera_index}...")
        
        # Use DirectShow backend for Windows (better performance)
        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        
        if not self.cap.isOpened():
            raise Exception(f"Cannot open camera {self.camera_index}")
        
        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_height)
        
        # Set FPS
        self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
        
        # Minimize buffer for real-time
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, self.buffer_size)
        
        # Disable autofocus (microscope has manual focus)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        
        # Set manual exposure
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # 0.25 = manual mode
        self.cap.set(cv2.CAP_PROP_EXPOSURE, self.current_exposure)
        
        # Set brightness and contrast
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, self.current_brightness)
        self.cap.set(cv2.CAP_PROP_CONTRAST, self.current_contrast)
        
        self.is_running = True
        
        # Get actual resolution
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        
        print(f"[Camera] Started successfully")
        print(f"  Resolution: {actual_width}x{actual_height}")
        print(f"  FPS: {actual_fps}")
        print(f"  Exposure: {self.current_exposure}")
        
        return True
    
    def get_frame(self):
        """
        Capture a single frame
        
        Returns:
            numpy.ndarray: Frame image or None if failed
        """
        if not self.is_running or self.cap is None:
            return None
        
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None
    
    def get_resolution(self):
        """Get current camera resolution"""
        if self.cap is None:
            return (0, 0)
        
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (width, height)
    
    def set_exposure(self, value):
        """
        Set exposure value
        
        Args:
            value: Exposure value (-13 to -1 for manual, 0 for auto)
        """
        if self.cap:
            self.cap.set(cv2.CAP_PROP_EXPOSURE, value)
            self.current_exposure = value
            print(f"[Camera] Exposure set to {value}")
    
    def set_brightness(self, value):
        """
        Set brightness
        
        Args:
            value: Brightness value (0-255)
        """
        if self.cap:
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, value)
            self.current_brightness = value
            print(f"[Camera] Brightness set to {value}")
    
    def set_contrast(self, value):
        """
        Set contrast
        
        Args:
            value: Contrast value (0-255)
        """
        if self.cap:
            self.cap.set(cv2.CAP_PROP_CONTRAST, value)
            self.current_contrast = value
            print(f"[Camera] Contrast set to {value}")
    
    def get_camera_info(self):
        """Get detailed camera information"""
        if not self.cap:
            return {}
        
        info = {
            'resolution': self.get_resolution(),
            'fps': int(self.cap.get(cv2.CAP_PROP_FPS)),
            'exposure': int(self.cap.get(cv2.CAP_PROP_EXPOSURE)),
            'brightness': int(self.cap.get(cv2.CAP_PROP_BRIGHTNESS)),
            'contrast': int(self.cap.get(cv2.CAP_PROP_CONTRAST)),
            'saturation': int(self.cap.get(cv2.CAP_PROP_SATURATION)),
            'gain': int(self.cap.get(cv2.CAP_PROP_GAIN)),
        }
        return info
    
    def release(self):
        """Release camera resources"""
        if self.cap:
            self.cap.release()
            self.cap = None
        self.is_running = False
        print("[Camera] Released")


def test_camera():
    """Test camera with live preview and controls"""
    print("=" * 60)
    print("MICROSCOPE CAMERA TEST")
    print("=" * 60)
    
    # List available cameras
    camera = RealtimeMicroscopeCamera()
    available = camera.list_available_cameras()
    
    if not available:
        print("\n[ERROR] No cameras found!")
        print("Please check:")
        print("  1. Camera is connected via USB")
        print("  2. Camera drivers are installed")
        print("  3. Camera is not being used by another application")
        return
    
    # Select camera
    if len(available) > 1:
        print(f"\nFound {len(available)} cameras. Using camera 0.")
        print("To use a different camera, modify camera_index in the code.")
    
    # Start camera
    try:
        camera.start()
    except Exception as e:
        print(f"\n[ERROR] Failed to start camera: {e}")
        return
    
    # Display info
    info = camera.get_camera_info()
    print("\nCamera Information:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("CONTROLS:")
    print("=" * 60)
    print("  [Q]     - Quit")
    print("  [S]     - Save current frame")
    print("  [I]     - Show camera info")
    print("  [+/-]   - Adjust exposure")
    print("  [W/S]   - Adjust brightness")
    print("  [A/D]   - Adjust contrast")
    print("=" * 60)
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            frame = camera.get_frame()
            
            if frame is None:
                print("[WARNING] Failed to get frame")
                time.sleep(0.1)
                continue
            
            # Calculate FPS
            frame_count += 1
            elapsed = time.time() - start_time
            if elapsed > 0:
                fps = frame_count / elapsed
            else:
                fps = 0
            
            # Add overlay
            display = frame.copy()
            h, w = display.shape[:2]
            
            # Semi-transparent background for text
            overlay = display.copy()
            cv2.rectangle(overlay, (0, 0), (300, 120), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, display, 0.4, 0, display)
            
            # Display info
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(display, f"FPS: {fps:.1f}", (10, 30), font, 0.7, (0, 255, 0), 2)
            cv2.putText(display, f"Resolution: {w}x{h}", (10, 60), font, 0.6, (255, 255, 255), 2)
            cv2.putText(display, f"Exposure: {camera.current_exposure}", (10, 90), font, 0.6, (255, 255, 255), 2)
            
            cv2.imshow("Microscope Camera - Live Preview", display)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\n[+] Quit requested")
                break
            
            elif key == ord('s'):
                filename = f"microscope_capture_{int(time.time())}.jpg"
                cv2.imwrite(filename, frame)
                print(f"[+] Frame saved: {filename}")
            
            elif key == ord('i'):
                info = camera.get_camera_info()
                print("\nCamera Information:")
                for key, value in info.items():
                    print(f"  {key}: {value}")
            
            elif key == ord('+') or key == ord('='):
                camera.set_exposure(min(camera.current_exposure + 1, -1))
            
            elif key == ord('-') or key == ord('_'):
                camera.set_exposure(max(camera.current_exposure - 1, -13))
            
            elif key == ord('w'):
                camera.set_brightness(min(camera.current_brightness + 10, 255))
            
            elif key == ord('s'):
                camera.set_brightness(max(camera.current_brightness - 10, 0))
            
            elif key == ord('d'):
                camera.set_contrast(min(camera.current_contrast + 10, 255))
            
            elif key == ord('a'):
                camera.set_contrast(max(camera.current_contrast - 10, 0))
    
    except KeyboardInterrupt:
        print("\n[+] Interrupted by user")
    
    finally:
        camera.release()
        cv2.destroyAllWindows()
        print("\n[+] Camera test completed")


if __name__ == "__main__":
    test_camera()
