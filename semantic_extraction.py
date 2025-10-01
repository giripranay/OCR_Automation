# mypy: disable-error-code="1"
import os
import json
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key="xxxx")  # Replace with your key

# Input and output paths
INPUT_FOLDER = "RAW_OCR"
OUTPUT_FOLDER = "EXTRACTED_OCR_DATA"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Fields to extract
FIELDS = ["Policy Number", "Collateral ID (VIN)", "Loan Number", "Policy Holder Name", "Policy Holder Address"]

def extract_fields_from_text(text: str) -> dict:
    """
    Pass the text to LLM and extract the required fields.
    Returns a dictionary with null for missing fields.
    """
    prompt = f"""
You are an assistant that extracts key information from insurance documents.
Extract the following fields from the text below. If a field is missing, return null.
Fields: {', '.join(FIELDS)}
Text:
\"\"\"
{text}
\"\"\"

Return only a JSON object with field names as keys.
"""
    response = client.chat.completions.create(
        model="gpt-5-mini",  # Or another model you have access to
        messages=[{"role": "user", "content": prompt}],
        # temperature=0
    )
    # Parse JSON returned by LLM
    try:
        content = response.choices[0].message.content.strip()
        data = json.loads(content)
    except Exception as e:
        print("Error parsing LLM output, returning nulls:", e)
        data = {field: None for field in FIELDS}
    return data

# Process each .txt file in RAW_OCR folder
for filename in os.listdir(INPUT_FOLDER):
    if not filename.lower().endswith(".txt"):
        continue
    input_path = os.path.join(INPUT_FOLDER, filename)
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    extracted_data = extract_fields_from_text(text)
    
    # Write JSON to output folder
    output_filename = os.path.splitext(filename)[0] + ".json"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, indent=4)
    
    print(f"Extracted data saved to: {output_path}")
