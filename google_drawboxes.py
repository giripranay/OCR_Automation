import os
import json
import cv2
import numpy as np

# Set your folder paths
folder_path = "H:\\OCR_Automation\\GOOGLE_VISION_OCR"
image_folder = "H:\\OCR_Automation\\infrrd_input_samples"
text_folder = "H:\\OCR_Automation\\TEXT_OCR"
output_folder = os.path.join(image_folder, "google")
text_output_folder = os.path.join(text_folder, "google_text")
# Create output folders if they don't exist
os.makedirs(output_folder, exist_ok=True)
os.makedirs(text_output_folder, exist_ok=True)

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
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Process OCR data
        pages = data.get("pages", [])
        if not pages or not isinstance(pages[0], list):
            print(f"No valid page data in {filename}")
            continue

        sorted_words = []

        for word_info in pages[0]:
            word = word_info.get("word", "")
            box = word_info.get("bounding_box", [])
            if len(box) == 4:
                # Draw bounding box and word on image
                pts = np.array([[pt["x"], pt["y"]] for pt in box], np.int32).reshape((-1, 1, 2))
                cv2.polylines(image, [pts], isClosed=True, color=(0, 0, 255), thickness=2)
                cv2.putText(image, word, (box[0]["x"], box[0]["y"] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

                # Calculate center point for sorting
                center_x = sum(pt["x"] for pt in box) / 4
                center_y = sum(pt["y"] for pt in box) / 4
                sorted_words.append((center_y, center_x, word))

        # Sort words top-to-bottom, then left-to-right
        sorted_words.sort()
        ordered_text = " ".join(word for _, _, word in sorted_words)

        # Save annotated image
        output_image_path = os.path.join(output_folder, image_name)
        cv2.imwrite(output_image_path, image)
        print(f"Saved annotated image to {output_image_path}")

        # Save sorted text
        text_output_path = os.path.join(text_output_folder, filename.replace(".json", ".txt"))
        with open(text_output_path, "w", encoding="utf-8") as text_file:
            text_file.write(ordered_text)
        print(f"Saved sorted text to {text_output_path}")