import os
from difflib import SequenceMatcher

# Define the paths to the two folders
azure_folder = "H:\\OCR_Automation\\TEXT_OCR\\azure_text"
google_folder = "H:\\OCR_Automation\\TEXT_OCR\\google"

# Check if both folders exist
if not os.path.exists(azure_folder):
    print(f"Azure folder not found: {azure_folder}")
elif not os.path.exists(google_folder):
    print(f"Google folder not found: {google_folder}")
else:
    # List all text files in the azure folder
    azure_files = [f for f in os.listdir(azure_folder) if f.endswith(".txt")]

    # Compare each file with the corresponding file in the google folder
    for filename in azure_files:
        azure_path = os.path.join(azure_folder, filename)
        google_path = os.path.join(google_folder, filename)

        if os.path.exists(google_path):
            # Read both files
            with open(azure_path, "r", encoding="utf-8") as f1, open(google_path, "r", encoding="utf-8") as f2:
                azure_text = f1.read()
                google_text = f2.read()

            # Compute similarity score
            similarity = SequenceMatcher(None, azure_text, google_text).ratio()
            print(f"{filename}: Similarity Score = {similarity:.2%}")
        else:
            print(f"Matching file not found in Google folder for: {filename}")