from ultralytics import YOLO
import torch
import os
import shutil

# Load the pretrained YOLO model
MODEL_PATH = r"C:\Users\VICTUS\Documents\OMR project\model_training\runs\detect\train5\weights\best.pt"
model = YOLO(MODEL_PATH)

# Set device (GPU if available, otherwise CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

CLASS_NAMES = ['barline', 'bass_clef', 'decrescendo', 'dotted_half_note', 'dotted_quarter_note', 
               'eight_beam', 'eight_flag', 'eight_rest', 'flat', 'half_note', 'natural', 'quarter_note', 
               'quarter_rest', 'sharp', 'sixteenth_beam', 'sixteenth_flag', 'sixteenth_rest', 'thirty_second_beam', 
               'treble_clef', 'whole_half_rest', 'whole_note']

unlabeled_images_path = r"C:\Users\VICTUS\Documents\OMR project\model_training\label_images"
unlabeled_images = ['110221_88.jpg', '110221_13.jpg', '110221_16.jpg', '110221_52.jpg', '110221_11.jpg', '110221_17.jpg', '110221_89.jpg', '110221_20.jpg', '110221_41.jpg', '110221_43.jpg', '110221_1.jpg', '110221_104.jpg', '110221_5.jpg', '110221_80.jpg', '110221_29.jpg', '110221_90.jpg', '110221_38.jpg', '110221_23.jpg', '110221_26.jpg', '110221_22.jpg', '110221_108.jpg', '110221_10.jpg', '110221_45.jpg', '110221_20.jpg', '110221_23.jpg', '110221_78.jpg', '110221_6.jpg', '110221_24.jpg', '110221_2.jpg', '110221_106.jpg', '110221_21.jpg', '110221_61.jpg', '110221_74.jpg', '110221_22.jpg', '110221_24.jpg', '110221_51.jpg', '110221_14.jpg', '110221_8.jpg', '110221_48.jpg', '110221_98.jpg', '110221_7.jpg', '110221_15.jpg']

images_output_path = r"C:\Users\VICTUS\Documents\OMR project\model_training\unlabeled_images\train\images"
label_output_path = r"C:\Users\VICTUS\Documents\OMR project\model_training\unlabeled_images\train\labels"

# Label all images and save their labels as YOLO format
for image_name in unlabeled_images:
    image_path = os.path.join(unlabeled_images_path, image_name)
    
    # Only save txt files containing labels
    results = model.predict(image_path, project=label_output_path, name=image_name.split('.')[0])

    # Save a copy of the image 
    shutil.copy(image_path, os.path.join(images_output_path, image_name))
    
    # Save the labels in YOLO format
    for result in results:
        boxes = result.boxes.xyxy.cpu().numpy()
        confidences = result.boxes.conf.cpu().numpy()
        class_ids = result.boxes.cls.cpu().numpy()
        image_width = result.orig_shape[1]
        image_height = result.orig_shape[0]
        
        with open(os.path.join(label_output_path, f"{image_name.split('.')[0]}.txt"), "w") as f:
            for box, confidence, class_id in zip(boxes, confidences, class_ids):
                x1, y1, x2, y2 = box

                # The YOLO format requires normalized coordinates
                center_x = (x1 + x2) / 2 / image_width
                center_y = (y1 + y2) / 2 / image_height
                width = (x2 - x1) / image_width
                height = (y2 - y1) / image_height
                
                f.write(f"{int(class_id)} {center_x} {center_y} {width} {height}\n")
        print(f"Labels saved for {image_name} in YOLO format.")