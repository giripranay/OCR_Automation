import os
import json

def normalize_text(text):
    return text.strip().upper()

def extract_google_tokens(data):
    return [
        {
            "text": normalize_text(token["word"]),
            "bounding_box": token["bounding_box"]
        }
        for token in data['pages'][0]
    ]

def extract_azure_tokens(data):
    return {normalize_text(token["text"]) for token in data if token["type"] == "token"}

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

def process_files(azure_folder, google_folder):
    results = []

    for filename in os.listdir(google_folder):
        google_path = os.path.join(google_folder, filename)
        azure_path = os.path.join(azure_folder, filename)

        if not os.path.exists(azure_path):
            continue

        with open(google_path, 'r') as f:
            google_data = json.load(f)

        with open(azure_path, 'r') as f:
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

    return results

# Example usage:
azure_folder = r"H:\OCR_Automation\infrrd_ocr_data"
google_folder = r"H:\OCR_Automation\GOOGLE_VISION_OCR"
report = process_files(azure_folder, google_folder)
for result in report:   
    print(result['matched_tokens'], result['unmatched_tokens'], result['match_percentage'], result['unmatch_percentage'])