import os
import json
import cv2

# Set your folder paths
folder_path = "H:\\OCR_Automation\\infrrd_ocr_data"
image_folder = "H:\\OCR_Automation\\infrrd_input_samples"
text_folder = "H:\\OCR_Automation\\TEXT_OCR"
output_folder = os.path.join(image_folder, "azure_boxes")
text_output_folder = os.path.join(text_folder, "azure_text")

# Create output folders if they don't exist
os.makedirs(output_folder, exist_ok=True)
os.makedirs(text_output_folder, exist_ok=True)

# Loop through all JSON files in the folder
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

        sorted_tokens = []

        # Draw boxes and collect tokens for sorting
        for token in data:
            x1, y1 = token["startX"], token["startY"]
            x2, y2 = token["endX"], token["endY"]
            text = token.get("text", "")
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

            # Calculate center point for sorting
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            sorted_tokens.append((center_y, center_x, text))

        # Sort tokens top-to-bottom, then left-to-right
        sorted_tokens.sort()
        ordered_text = " ".join(token[2] for token in sorted_tokens)

        # Save annotated image
        output_path = os.path.join(output_folder, image_name)
        cv2.imwrite(output_path, image)
        print(f"Saved annotated image to {output_path}")

        # Save sorted text
        text_output_path = os.path.join(text_output_folder, filename.replace(".json", ".txt"))
        with open(text_output_path, "w", encoding="utf-8") as text_file:
            text_file.write(ordered_text)
        print(f"Saved sorted text to {text_output_path}")