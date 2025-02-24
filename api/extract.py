from ultralytics import YOLO
import cv2
import torch

NUMBER_OF_CLASSES = 20
CLASS_NAMES = ['barline', 'bass_clef', 'decrescendo', 'dotted_note', 'eight_beam', 'eight_flag', 'eight_rest', 'flat', 'half_note', 'natural', 'quarter_note', 'quarter_rest', 'sharp', 'sixteenth_beam', 'sixteenth_flag', 'sixteenth_rest', 'thirty_second_beam', 'treble_clef', 'whole_half_rest', 'whole_note']

# Load a pretrained model
model = YOLO(r"C:\Users\VICTUS\Documents\OMR project\model_training\runs\detect\train4\weights\best.pt")

# Check if CUDA (GPU) is available
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

def extract_boxes(image_path: str) -> list:
    """
    Extracts bounding boxes from an image using a pretrained YOLO model.
    :param image_path: path to the image
    :return: list of bounding boxes for each class
    """

    # Load the image
    image = cv2.imread(image_path)

    # Validate the model
    results = model(image)

    # Save boxes' coordinates to a list
    box_coordinates = [[] for _ in range(NUMBER_OF_CLASSES)]

    # Store the bounding boxes of each class
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0].item())
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            box_coordinates[class_id].append((x1, y1, x2, y2))

    return box_coordinates

def drawBoundingBoxes(image_path: str, boxes: list, output_path: str) -> None:
    """
    Draws bounding boxes on an image.
    :param image_path: path to the image
    :param boxes: list of bounding boxes
    :param output_path: path to the output image
    """

    # Load the image
    image = cv2.imread(image_path)

    # Draw bounding boxes
    for class_id, box_list in enumerate(boxes):
        for box in box_list:
            x1, y1, x2, y2 = box
            cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

            # Add class name
            cv2.putText(image, CLASS_NAMES[class_id], (int(x1), int(y1)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Save the image
    cv2.imwrite(output_path, image)

image_path = r"C:\Users\VICTUS\Documents\OMR project\model_training\res\dream_flower\roi_2_reconstructed.jpg"
boxes = extract_boxes(image_path)
print(boxes)


