import sys
import os

def adjust_label_file(file_path, target_classes, img_width=640, img_height=640, pixel_adjust=2):
    """
    Adjusts YOLO label bounding box sizes for specified classes.
    
    :param file_path: Path to the YOLO label file.
    :param target_classes: List of class indices to adjust.
    :param img_width: Image width in pixels.
    :param img_height: Image height in pixels.
    :param pixel_adjust: Pixels to add to width and height.
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    adjusted_lines = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) != 5:
            continue  # Skip invalid lines
        
        cls, x_center, y_center, width, height = map(float, parts)
        
        if int(cls) in target_classes:
            width += pixel_adjust / img_width
            height += pixel_adjust / img_height
            width = min(width, 1.0)  # Ensure it doesn't exceed the limit
            height = min(height, 1.0)
        
        adjusted_lines.append(f"{int(cls)} {x_center:.16f} {y_center:.16f} {width:.16f} {height:.16f}\n")
    
    with open(file_path, 'w') as f:
        f.writelines(adjusted_lines)

if __name__ == "__main__":    
    directory = r"C:\Users\VICTUS\Documents\OMR project\dataset\train\labels"
    target_classes = {4, 10, 13, 16}  # Classes to adjust
    
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)
            adjust_label_file(file_path, target_classes)
            print(f"Adjusted: {file_path}")
