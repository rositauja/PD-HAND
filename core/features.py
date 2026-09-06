#features.py
import cv2
import numpy as np

from skimage.feature import hog, local_binary_pattern

def extract_spiral_features(thresh_img):
    features = {}

    ink_pixels   = np.sum(thresh_img > 0)
    total_pixels = thresh_img.size
    ink_ratio    = ink_pixels / total_pixels

    features["ink_pixels"] = int(ink_pixels)
    features["ink_ratio"]  = float(ink_ratio)

    contours, _ = cv2.findContours(
        thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    features["num_contours"] = len(contours)

    if contours:
        largest_contour   = max(contours, key=cv2.contourArea)
        contour_area      = cv2.contourArea(largest_contour)
        contour_perimeter = cv2.arcLength(largest_contour, True)
        x, y, w, h        = cv2.boundingRect(largest_contour)
        aspect_ratio      = w / h if h != 0 else 0

        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            centroid_x = M["m10"] / M["m00"]
            centroid_y = M["m01"] / M["m00"]
        else:
            centroid_x, centroid_y = 0, 0

        rect_area = w * h
        extent    = contour_area / rect_area if rect_area != 0 else 0

        hull      = cv2.convexHull(largest_contour)
        hull_area = cv2.contourArea(hull)
        solidity  = contour_area / hull_area if hull_area != 0 else 0
    else:
        contour_area = contour_perimeter = 0
        w = h = 0
        aspect_ratio = centroid_x = centroid_y = extent = solidity = 0

    features["contour_area"]        = float(contour_area)
    features["contour_perimeter"]   = float(contour_perimeter)
    features["bounding_box_width"]  = int(w)
    features["bounding_box_height"] = int(h)
    features["aspect_ratio"]        = float(aspect_ratio)
    features["centroid_x"]          = float(centroid_x)
    features["centroid_y"]          = float(centroid_y)
    features["extent"] = float(extent)
    features["solidity"] = float(solidity)

    # HOG features
    hog_features = hog(
        thresh_img,
        orientations=8,
        pixels_per_cell=(16, 16),
        cells_per_block=(1, 1),
        visualize=False
    )

    for i, val in enumerate(hog_features):
        features[f"hog_{i}"] = float(val)

    # LBP features
    lbp = local_binary_pattern(
        thresh_img,
        P=8,
        R=1,
        method='uniform'
    )

    lbp_hist, _ = np.histogram(
        lbp.ravel(),
        bins=10,
        range=(0, 10),
        density=True
    )

    for i, val in enumerate(lbp_hist):
        features[f"lbp_{i}"] = float(val)

    # Hu Moments
    moments = cv2.moments(thresh_img)

    hu_moments = cv2.HuMoments(
        moments
    ).flatten()

    for i, val in enumerate(hu_moments):
        features[f"hu_{i}"] = float(
            np.sign(val) * np.log1p(abs(val))
        )

    return features

def extract_meander_features(thresh_img):
    """
    Meander uses the same 12 features as spiral.
    Both are drawing-based tasks with identical feature pipelines.
    """
    return extract_spiral_features(thresh_img)