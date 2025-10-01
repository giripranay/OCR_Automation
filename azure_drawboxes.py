import os
import json
import cv2

# Set your folder path here
folder_path = "H:\\OCR_Automation\\infrrd_ocr_data"
image_folder = "H:\\OCR_Automation\\infrrd_input_samples"
output_folder = os.path.join(image_folder, "azure_boxes")
os.makedirs(output_folder, exist_ok=True)

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
        with open(json_path, "r") as f:
            data = json.load(f)

        # Draw boxes
        for token in data:
            x1, y1 = token["startX"], token["startY"]
            x2, y2 = token["endX"], token["endY"]
            text = token.get("text", "")
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # Save output image
        output_path = os.path.join(output_folder, image_name)
        cv2.imwrite(output_path, image)
        print(f"Saved annotated image to {output_path}")