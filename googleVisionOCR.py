from pdf2image import convert_from_path
from PIL import Image
import os

def pdf_to_tiff(pdf_path, tiff_path):
    # Convert all pages into a list of PIL images
    images = convert_from_path(pdf_path)

    # Save as multi-page TIFF
    images[0].save(
        tiff_path,
        save_all=True,
        append_images=images[1:],
        compression="tiff_deflate"
    )
    print(f"Converted {pdf_path} → {tiff_path}")
    return tiff_path


from google.cloud import vision
import io
import json

def vision_ocr_tiff(tiff_path, output_folder="GOOGLE_VISION_OCR"):
    client = vision.ImageAnnotatorClient()

    with io.open(tiff_path, "rb") as f:
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

    # Save JSON
    os.makedirs(output_folder, exist_ok=True)
    base_name = os.path.basename(tiff_path)
    file_name, _ = os.path.splitext(base_name)
    out_path = os.path.join(output_folder, f"{file_name}_vision_ocr.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(ocr_data, f, indent=2, ensure_ascii=False)

    print(f"OCR data saved to {out_path}")
    return ocr_data


if __name__ == "__main__":
    pdf_file = "c:\\Users\\girip\\Downloads\\Infrrd.pdf"
    tiff_file = "Infrrd.tiff"

    # Convert PDF → TIFF
    pdf_to_tiff(pdf_file, tiff_file)

    # OCR with Vision API
    vision_ocr_tiff(tiff_file)
