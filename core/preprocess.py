# core/preprocess.py 
import cv2
import numpy as np

def preprocess_spiral(image):
    """
    Preprocessing for spiral model.
    Matches the exact training pipeline.
    
    Steps:
    1. Resize to 128x128
    2. Convert BGR to Grayscale
    3. Apply GaussianBlur(5, 5)
    4. Otsu binary threshold (inverted)
    
    Args:
        image: BGR image from cv2.imread() or upload
        
    Returns:
        tuple: (gray, thresh)
            gray - grayscale image
            thresh - binary threshold image
    """
    resized = cv2.resize(image, (128, 128))
    gray    = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(
        blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )
    return gray, thresh

def preprocess_meander(image):
    """
    Preprocessing for meander model.
    
    Steps:
    1. Resize to 128x128
    2. Convert BGR to Grayscale
    3. Apply GaussianBlur(5, 5)
    4. Otsu binary threshold (inverted)
    
    Args:
        image: BGR image from cv2.imread() or upload
        
    Returns:
        tuple: (gray, thresh)
            gray - grayscale image
            thresh - binary threshold image
    """
    resized = cv2.resize(image, (128, 128))
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    # CLAHE enhancement
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8,8)
    )
    gray = clahe.apply(gray)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(
        blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )
    return gray, thresh

def preprocess_draw(image):
    resized = cv2.resize(image, (128, 128))
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(
        gray, 180, 255, cv2.THRESH_BINARY_INV
    )

    return gray, thresh