import os
import json
import cv2

def normalize_text(text):
    return text.strip().upper()

def extract_google_tokens(data):
    """Extract tokens from Google Vision OCR JSON"""
    tokens = []
    for page in data.get("pages", []):
        for token in page:  # Adjust if your structure is different
            tokens.append({
                "text": normalize_text(token.get("word", "")),
                "bounding_box": token.get("bounding_box", {})
            })
    return tokens

def extract_azure_tokens(data):
    """Extract tokens from Azure OCR JSON"""
    return {normalize_text(token["text"]) for token in data if token.get("type") == "token"}

def compare_tokens(google_tokens, azure_token_set):
    unmatched = []
    matched_count = 0
    for token in google_tokens:
        if token["text"] in azure_token_set:
            matched_count += 1
        else:
            unmatched.append(token)

    total = len(google_tokens)
    match_percentage = (matched_count / total) * 100 if total > 0 else 0
    unmatch_percentage = 100 - match_percentage

    return unmatched, match_percentage, unmatch_percentage

def draw_unmatched_boxes(image_path, unmatched_tokens, output_path):
    """Draw bounding boxes for unmatched tokens"""
    img = cv2.imread(image_path)
    if img is None:
        print(f"⚠️ Could not read image {image_path}")
        return

    for token in unmatched_tokens:
        bbox = token["bounding_box"]
        if not bbox:
            continue

        # Assuming bbox = {"vertices": [{"x": , "y": }, ...]}
        points = [(v.get("x", 0), v.get("y", 0)) for v in bbox]

        if len(points) == 4:
            x1, y1 = points[0]
            x3, y3 = points[2]
            cv2.rectangle(img, (x1, y1), (x3, y3), (0, 0, 255), 2)  # Red box

            # Put text near the box
            cv2.putText(img, token["text"], (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, img)

def process_files(azure_folder, google_folder, image_folder, unmatched_output_folder):
    results = []
    os.makedirs(unmatched_output_folder, exist_ok=True)

    for filename in os.listdir(google_folder):
        google_path = os.path.join(google_folder, filename)
        azure_path = os.path.join(azure_folder, filename)
        image_path = os.path.join(image_folder, os.path.splitext(filename)[0] + ".jpg")  # assuming images are .jpg
        output_path = os.path.join(unmatched_output_folder, os.path.splitext(filename)[0] + "_unmatched.jpg")

        if not os.path.exists(azure_path):
            continue

        with open(google_path, "r") as f:
            google_data = json.load(f)
        with open(azure_path, "r") as f:
            azure_data = json.load(f)

        google_tokens = extract_google_tokens(google_data)
        azure_token_set = extract_azure_tokens(azure_data)

        unmatched, match_pct, unmatch_pct = compare_tokens(google_tokens, azure_token_set)

        results.append({
            "file": filename,
            "total_google_tokens": len(google_tokens),
            "matched_tokens": len(google_tokens) - len(unmatched),
            "unmatched_tokens": len(unmatched),
            "match_percentage": match_pct,
            "unmatch_percentage": unmatch_pct,
            "unmatched_details": unmatched
        })

        # Draw boxes for unmatched tokens
        if os.path.exists(image_path):
            draw_unmatched_boxes(image_path, unmatched, output_path)

    return results


# Example usage
azurefolder = r"H:\\OCR_Automation\\infrrd_ocr_data"
googlefolder = r"H:\\OCR_Automation\\GOOGLE_VISION_OCR"
imagefolder = r"H:\\OCR_Automation\\infrrd_input_samples"
unmatched_output_folder = r"H:\\OCR_Automation\\unmatched"

report = process_files(azurefolder, googlefolder, imagefolder, unmatched_output_folder)

for result in report:
    print(result["file"], result["matched_tokens"], result["unmatched_tokens"],
          f"{result['match_percentage']:.2f}%")
 