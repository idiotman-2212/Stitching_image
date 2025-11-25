import cv2
import glob
import os
import time

class Camera:
    def __init__(self, source=0, width=1280, height=720, fps=60):
        self.source = source
        self.cap = None
        self.width = width
        self.height = height
        self.fps = fps
        self.is_simulation = False
        self.image_files = []
        self.current_image_index = 0

    def start(self):
        if isinstance(self.source, str) and os.path.isdir(self.source):
            # Simulation mode: read from directory
            self.is_simulation = True
            self.image_files = sorted(glob.glob(os.path.join(self.source, "*.jpg")))
            if not self.image_files:
                 self.image_files = sorted(glob.glob(os.path.join(self.source, "*.png")))
            print(f"Simulation mode: Found {len(self.image_files)} images in {self.source}")
        else:
            # Real camera mode
            self.cap = cv2.VideoCapture(self.source)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            if not self.cap.isOpened():
                print(f"Error: Could not open camera {self.source}")
                # Fallback to simulation if camera fails? Or just raise error.
                # For demo, let's just print error.

    def get_frame(self):
        if self.is_simulation:
            if self.current_image_index < len(self.image_files):
                frame = cv2.imread(self.image_files[self.current_image_index])
                self.current_image_index += 1
                time.sleep(0.05) # Simulate delay (faster)
                return frame
            else:
                return None # End of stream
        else:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    return frame
            return None

    def release(self):
        if self.cap:
            self.cap.release()
