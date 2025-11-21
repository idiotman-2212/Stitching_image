import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import time

class FastStitcher:
    """
    Fast image stitcher using ORB features and incremental stitching.
    Much faster than OpenCV's Stitcher for sequential microscope images.
    """
    def __init__(self, use_gpu=False):
        self.images = []
        self.use_gpu = use_gpu
        
        # Use ORB (faster than SIFT/SURF, patent-free)
        self.detector = cv2.ORB_create(nfeatures=2000)
        
        # FLANN matcher for fast matching
        FLANN_INDEX_LSH = 6
        index_params = dict(algorithm=FLANN_INDEX_LSH,
                           table_number=6,
                           key_size=12,
                           multi_probe_level=1)
        search_params = dict(checks=50)
        self.matcher = cv2.FlannBasedMatcher(index_params, search_params)
        
        print(f"FastStitcher initialized (GPU: {use_gpu})")

    def add_image(self, image):
        """Add image to the stitching queue"""
        self.images.append(image)

    def _detect_features(self, img):
        """Detect keypoints and descriptors"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        kp, des = self.detector.detectAndCompute(gray, None)
        return kp, des

    def _match_images(self, des1, des2):
        """Match descriptors between two images"""
        if des1 is None or des2 is None or len(des1) < 2 or len(des2) < 2:
            return []
        
        try:
            matches = self.matcher.knnMatch(des1, des2, k=2)
            
            # Lowe's ratio test
            good_matches = []
            for match_pair in matches:
                if len(match_pair) == 2:
                    m, n = match_pair
                    if m.distance < 0.7 * n.distance:
                        good_matches.append(m)
            
            return good_matches
        except:
            return []

    def _stitch_pair(self, img1, img2, kp1, kp2, matches):
        """Stitch two images together"""
        if len(matches) < 4:
            print("Not enough matches found")
            return None
        
        # Extract matched keypoints
        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
        
        # Find homography
        H, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
        
        if H is None:
            print("Homography estimation failed")
            return None
        
        # Warp img2 to img1's coordinate system
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]
        
        # Calculate output size
        corners = np.float32([[0, 0], [0, h2], [w2, h2], [w2, 0]]).reshape(-1, 1, 2)
        warped_corners = cv2.perspectiveTransform(corners, H)
        
        all_corners = np.concatenate((
            np.float32([[0, 0], [0, h1], [w1, h1], [w1, 0]]).reshape(-1, 1, 2),
            warped_corners
        ), axis=0)
        
        [x_min, y_min] = np.int32(all_corners.min(axis=0).ravel() - 0.5)
        [x_max, y_max] = np.int32(all_corners.max(axis=0).ravel() + 0.5)
        
        # Translation matrix
        translation = np.array([[1, 0, -x_min],
                               [0, 1, -y_min],
                               [0, 0, 1]])
        
        # Warp images
        output_size = (x_max - x_min, y_max - y_min)
        result = cv2.warpPerspective(img2, translation.dot(H), output_size)
        result[-y_min:-y_min + h1, -x_min:-x_min + w1] = img1
        
        return result

    def stitch_incremental(self):
        """
        Incremental stitching: stitch images sequentially.
        Much faster than stitching all at once.
        """
        if len(self.images) < 2:
            print("Not enough images to stitch")
            return None, "Not enough images"
        
        print(f"Fast stitching {len(self.images)} images incrementally...")
        start_time = time.time()
        
        # Detect features for all images in parallel
        print("Detecting features...")
        with ThreadPoolExecutor(max_workers=4) as executor:
            features = list(executor.map(self._detect_features, self.images))
        
        # Start with first image
        result = self.images[0].copy()
        result_kp, result_des = features[0]
        
        # Incrementally stitch each image
        for i in range(1, len(self.images)):
            print(f"Stitching image {i+1}/{len(self.images)}...")
            
            kp2, des2 = features[i]
            
            # Match features
            matches = self._match_images(result_des, des2)
            print(f"  Found {len(matches)} matches")
            
            if len(matches) < 4:
                print(f"  Skipping image {i+1} (not enough matches)")
                continue
            
            # Stitch
            stitched = self._stitch_pair(result, self.images[i], result_kp, kp2, matches)
            
            if stitched is not None:
                result = stitched
                # Re-detect features on the result for next iteration
                result_kp, result_des = self._detect_features(result)
            else:
                print(f"  Failed to stitch image {i+1}")
        
        elapsed = time.time() - start_time
        print(f"Stitching completed in {elapsed:.2f} seconds")
        
        return result, None

    def stitch(self):
        """Main stitch method (uses incremental approach)"""
        return self.stitch_incremental()

    def clear(self):
        """Clear image buffer"""
        self.images = []
