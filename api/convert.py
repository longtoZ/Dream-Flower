import os
import uuid
from pdf2image import convert_from_path

def convert_to_images(pdf_path: str) -> list:
    path = os.path.split(pdf_path)[1]

    output_folder = f"{str(uuid.uuid4())}_{path[:path.rindex('.pdf')]}_images"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Convert PDF to images
    images = convert_from_path(pdf_path, dpi=300, poppler_path="./poppler-24.08.0/Library/bin")

    # Save each page as an image
    for i, img in enumerate(images):
        img_path = f"{output_folder}/page_{i}.png"
        img.save(img_path, "PNG")
        print(f"Saved {img_path}")

convert_to_images(r"C:\Users\VICTUS\Downloads\Viva_la_vida_Coldplay_piano.pdf")