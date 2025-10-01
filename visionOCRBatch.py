import os
import io
import json
import argparse
from google.cloud import vision

def vision_ocr_image(image_path, output_folder="GOOGLE_VISION_OCR"):
    client = vision.ImageAnnotatorClient()

    with io.open(image_path, "rb") as f:
        content = f.read()
    image = vision.Image(content=content)

    response = client.document_text_detection(image=image)
    full_text = response.full_text_annotation.text if response.full_text_annotation else ""

    ocr_data = {
        "full_text": full_text,
        "pages": []
    }

    for page in response.full_text_annotation.pages:
        page_words = []
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    word_text = "".join([s.text for s in word.symbols])
                    page_words.append({
                        "word": word_text,
                        "bounding_box": [{"x": v.x, "y": v.y} for v in word.bounding_box.vertices]
                    })
        ocr_data["pages"].append(page_words)

    os.makedirs(output_folder, exist_ok=True)
    base_name = os.path.basename(image_path)
    file_name, _ = os.path.splitext(base_name)
    out_path = os.path.join(output_folder, f"{file_name}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(ocr_data, f, indent=2, ensure_ascii=False)

    print(f"OCR data saved to {out_path}")

def process_folder(folder_path):
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(".jpg"):
            image_path = os.path.join(folder_path, file_name)
            vision_ocr_image(image_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perform Google Vision OCR on JPG images in a folder.")
    parser.add_argument("folder", help="Path to the folder containing JPG images")
    args = parser.parse_args()

    process_folder(args.folder)

