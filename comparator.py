import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

class ImageComparator:
    def __init__(self):
        pass

    def compare(self, imageA, imageB):
        """
        Compares two images and returns a similarity score (SSIM) and a difference image.
        Images are resized to match the smaller one's dimensions for comparison.
        """
        if imageA is None or imageB is None:
            return 0.0, None

        # Convert to grayscale
        grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

        # Resize to match dimensions
        hA, wA = grayA.shape
        hB, wB = grayB.shape
        
        # Simple approach: resize the larger one to the smaller one
        # In a real medical app, you'd want registration/alignment first.
        target_h = min(hA, hB)
        target_w = min(wA, wB)

        grayA = cv2.resize(grayA, (target_w, target_h))
        grayB = cv2.resize(grayB, (target_w, target_h))

        # Compute SSIM
        (score, diff) = ssim(grayA, grayB, full=True)
        diff = (diff * 255).astype("uint8")

        return score, diff
