# image_utils.py
import io
import cv2
import numpy as np

def separate_staff_zones(images_io: io.BytesIO) -> list:
    """Separates an image into distinct staff zones."""
    original_image = cv2.imdecode(np.frombuffer(images_io.getvalue(), np.uint8), cv2.IMREAD_COLOR)
    if original_image is None:
        print("Error: Could not decode image in separate_staff_zones")
        return []
        
    modified_image = original_image.copy()
    height, width, channels = modified_image.shape

    # Apply grayscale, Gaussian blur, thresholding and morphological operations
    gray = cv2.cvtColor(modified_image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    # Use a kernel biased towards horizontal connection to group staff lines
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (width // 10, 5)) # Adjusted kernel size
    dilate = cv2.dilate(thresh, kernel, iterations=3) # Increased iterations

    # Find contours and filter for staff zones
    cnts, _ = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # cnts = cnts[0] if len(cnts) == 2 else cnts[1] # Older OpenCV versions
    
    if not cnts:
        print("Warning: No contours found for staff separation.")
        # Fallback: return the whole image as one zone if no contours found
        return [original_image] 

    cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[1])  # Sort vertically

    staff_zones = []
    min_staff_width_ratio = 0.6 # Adjust if needed

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        
        # Filter based on width relative to image width and minimum height
        if w > width * min_staff_width_ratio and h > 10: # Added min height check
            # Add some padding around the detected zone if desired
            padding = 5 
            y_start = max(0, y - padding)
            y_end = min(height, y + h + padding)
            x_start = max(0, x - padding)
            x_end = min(width, x + w + padding)
            
            roi = original_image[y_start:y_end, x_start:x_end]
            staff_zones.append(roi)
            # Optional: Draw rectangle on original image for debugging
            # cv2.rectangle(modified_image, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)
            
    # cv2.imwrite("debug_staff_separation.png", modified_image) # For debugging

    if not staff_zones:
        print("Warning: No suitable staff zone contours found after filtering.")
        # Fallback: return the whole image if filtering removed all zones
        return [original_image]
        
    return staff_zones


def remove_staff_lines(zone: np.ndarray) -> np.ndarray:
    """Removes staff lines from a given staff zone image."""
    if zone is None or zone.size == 0:
        print("Error: Invalid input zone in remove_staff_lines")
        return np.array([]) # Return empty array or handle error as appropriate

    gray = cv2.cvtColor(zone, cv2.COLOR_BGR2GRAY)
    
    # Adaptive thresholding might be more robust than OTSU here
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                   cv2.THRESH_BINARY_INV, 15, 8)

    # --- Horizontal line removal ---
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1)) # Kernel to detect horizontal lines
    detected_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

    # Dilate lines slightly to ensure full removal, but not too much to affect symbols
    cnts = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(thresh, [c], -1, (0, 0, 0), 2) # Draw black over detected lines

    # --- Vertical line removal (optional, can sometimes remove note stems) ---
    # vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    # detected_vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    # cnts_v = cv2.findContours(detected_vertical_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # cnts_v = cnts_v[0] if len(cnts_v) == 2 else cnts_v[1]
    # for c in cnts_v:
    #     cv2.drawContours(thresh, [c], -1, (0,0,0), 2) 

    # Return the image with lines removed (still binary)
    # Convert back to BGR if needed by the model later
    # return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR) 
    return cv2.bitwise_not(thresh) # Invert back to black symbols on white bg

def extract_staff_lines(zone: np.ndarray) -> list:
    """Extracts the coordinates of the staff lines within a zone."""
    if zone is None or zone.size == 0:
        print("Error: Invalid input zone in extract_staff_lines")
        return []
        
    gray = cv2.cvtColor(zone, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    height, width = thresh.shape

    # Use morphology to isolate horizontal lines
    # Kernel width should be significant fraction of zone width
    horizontal_kernel_size = max(15, width // 4) 
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_kernel_size, 1))
    
    # Open operation (erode then dilate) helps remove noise and keeps lines
    horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)

    # Find contours of the lines
    contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # contours = contours[0] if len(contours) == 2 else contours[1] # Older OpenCV

    staff_lines = []
    min_line_width_ratio = 0.5 # Minimum width relative to zone width
    max_line_thickness = 5     # Maximum pixel thickness for a staff line

    contours = sorted(contours, key=lambda x: cv2.boundingRect(x)[1]) # Sort by y-coordinate

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        
        # Filter based on width and thickness (height of bounding box)
        if w > width * min_line_width_ratio and h <= max_line_thickness and h > 0:
             # Calculate the centerline y-coordinate
            center_y = y + h // 2
            # Store as (x_start, y_center, width, thickness) or just y_center
            staff_lines.append({'y': center_y, 'x': x, 'width': w, 'thickness': h}) 
            # Could also just store y: staff_lines.append(center_y)
            
    # Further refine: check if we have roughly 5 lines and if they are evenly spaced
    if len(staff_lines) > 7 or len(staff_lines) < 3: # Basic sanity check
        print(f"Warning: Unexpected number of staff lines found: {len(staff_lines)}")
        # Could add logic here to try and select the best 5 lines if needed
        
    # Return the y-coordinates (or more detailed dicts)
    return [line['y'] for line in staff_lines] # Example: return just y-coords