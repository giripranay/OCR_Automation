import os
import json
import cv2
import numpy as np

# Set your folder path
folder_path = "H:\\OCR_Automation\\GOOGLE_VISION_OCR"
image_folder = "H:\\OCR_Automation\\infrrd_input_samples"
output_folder = os.path.join(image_folder, "google")
os.makedirs(output_folder, exist_ok=True)

# Loop through all JSON files
for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        json_path = os.path.join(folder_path, filename)
        image_name = filename.replace(".json", ".jpg")
        image_path = os.path.join(image_folder, image_name)

        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Image not found for {filename}")
            continue

        # Load JSON data
        with open(json_path, "r") as f:
            data = json.load(f)

        # Process OCR data
        pages = data.get("pages", [])
        if not pages or not isinstance(pages[0], list):
            print(f"No valid page data in {filename}")
            continue

        for word_info in pages[0]:
            word = word_info.get("word", "")
            box = word_info.get("bounding_box", [])
            if len(box) == 4:
                pts = np.array([[pt["x"], pt["y"]] for pt in box], np.int32).reshape((-1, 1, 2))
                cv2.polylines(image, [pts], isClosed=True, color=(0, 0, 255), thickness=2)
                cv2.putText(image, word, (box[0]["x"], box[0]["y"] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # Save annotated image
        output_path = os.path.join(output_folder, image_name)
        cv2.imwrite(output_path, image)
        print(f"Saved annotated image to {output_path}")