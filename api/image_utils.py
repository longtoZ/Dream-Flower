# image_utils.py
import io
import cv2
import numpy as np

def separate_staff_zones(images_io: io.BytesIO) -> list:
    original_image = cv2.imdecode(np.frombuffer(images_io.getvalue(), np.uint8), cv2.IMREAD_COLOR)
    modified_image = original_image.copy()
    height, width, channels = modified_image.shape

    # Apply grayscale, Gaussian blur, thresholding and morphological operations to group staff zones
    gray = cv2.cvtColor(modified_image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 10))
    dilate = cv2.dilate(thresh, kernel, iterations=1)

    # Find contours and filter for staff zones
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cnts = sorted(cnts, key=lambda x : cv2.boundingRect(x)[1]) # Sort based on vertical order

    # Extract staff zones by filtering contours whose width is greater than 80% of the image width
    staff_zones = []

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        
        if w > width*0.8:
            roi = original_image[y:y+h, x:x+w]
            staff_zones.append(roi)
        
    return staff_zones

def remove_staff_lines(zone: np.ndarray) -> np.ndarray:
    # Convert image to grayscale and apply thresholding
    gray = cv2.cvtColor(zone, cv2.COLOR_BGR2GRAY)
    vertical = cv2.threshold(gray, 210, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Create structure element for extracting vertical lines through morphology operations
    verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 4))
    
    # Apply morphology operations
    vertical = cv2.erode(vertical, verticalStructure)
    vertical = cv2.dilate(vertical, verticalStructure)

    # Reconstruct noteheads and beams
    notehead_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    reconstructed = cv2.dilate(vertical, notehead_kernel, iterations=1)

    # Invert the image to origin
    inverted = cv2.bitwise_not(reconstructed)

    return inverted

def extract_staff_lines(zone: np.ndarray) -> list:
    # Convert image to grayscale and apply thresholding
    gray = cv2.cvtColor(zone, cv2.COLOR_BGR2GRAY)
    horizontal = cv2.threshold(gray, 210, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    height, width, = horizontal.shape

    # Create structure element for extracting horizontal lines through morphology operations
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (round(width*0.8), 1))

    # Apply morphology operations
    horizontal = cv2.erode(horizontal, horizontalStructure)
    horizontal = cv2.dilate(horizontal, horizontalStructure)

    # Filter based on thickness
    contours, _ = cv2.findContours(horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=lambda x : cv2.boundingRect(x)[1])

    # List to hold staff lines
    staff_lines = []

    for contour in contours:
        # Get bounding box of each contour
        x, y, w, h = cv2.boundingRect(contour)
        
        # Filter based on height (thickness)
        if w < width*0.8 and h > 4:  # Adjust this value to filter out thicker beams
            cv2.drawContours(horizontal, [contour], -1, 0, -1)
        else:
            staff_lines.append((x, y, w, h))

    # Optional: Preserve edges
    # horizontal = cv2.dilate(horizontal, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)), iterations=1)

    return staff_lines