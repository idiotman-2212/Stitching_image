import cv2
import numpy as np

class ImageStitcher:
    """
    Standard OpenCV-based image stitcher.
    Uses OpenCV's Stitcher class for panorama creation.
    """
    def __init__(self):
        self.images = []
        # Create stitcher instance (OpenCV 4.x)
        try:
            self.stitcher = cv2.Stitcher_create(cv2.Stitcher_PANORAMA)
        except AttributeError:
            # Fallback for older OpenCV versions
            self.stitcher = cv2.createStitcher()
    
    def add_image(self, image):
        """Add an image to the list of images to be stitched."""
        if image is not None:
            self.images.append(image.copy())
    
    def stitch(self):
        """
        Stitch all added images into a panorama.
        
        Returns:
            tuple: (stitched_image, error_message)
                   stitched_image is None if stitching failed
        """
        if len(self.images) < 2:
            return None, "Need at least 2 images to stitch"
        
        print(f"Stitching {len(self.images)} images using OpenCV Stitcher...")
        
        try:
            status, stitched = self.stitcher.stitch(self.images)
            
            if status == cv2.Stitcher_OK:
                print("Stitching successful!")
                return stitched, None
            else:
                error_messages = {
                    cv2.Stitcher_ERR_NEED_MORE_IMGS: "Need more images",
                    cv2.Stitcher_ERR_HOMOGRAPHY_EST_FAIL: "Homography estimation failed",
                    cv2.Stitcher_ERR_CAMERA_PARAMS_ADJUST_FAIL: "Camera parameters adjustment failed"
                }
                error_msg = error_messages.get(status, f"Unknown error (code: {status})")
                print(f"Stitching failed: {error_msg}")
                return None, error_msg
                
        except Exception as e:
            error_msg = f"Exception during stitching: {str(e)}"
            print(error_msg)
            return None, error_msg
    
    def reset(self):
        """Clear all stored images."""
        self.images = []
