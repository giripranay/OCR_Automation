import os
import subprocess
import concurrent.futures
import glob
import json


# ✅ Replace with your actual Python path
python_exe = r"H:\OCR_Automation\ocr_env\Scripts\python.exe"

# Define paths to scripts
scripts_dir = r"H:\\OCR_Automation"  # Update this if needed
google_ocr_script = os.path.join(scripts_dir, "googleOCR.py")
azure_drawboxes_script = os.path.join(scripts_dir, "azure_drawboxes.py")
google_drawboxes_script = os.path.join(scripts_dir, "google_drawboxes.py")
normalized_match_script = os.path.join(scripts_dir, "normalized_token_match.py")

# Step 1: Run googleOCR.py
subprocess.run([python_exe, google_ocr_script], check=True)

# Step 2: Run azure_drawboxes.py and google_drawboxes.py in parallel
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [
        executor.submit(subprocess.run, [python_exe, azure_drawboxes_script], {"check": True}),
        executor.submit(subprocess.run, [python_exe, google_drawboxes_script], {"check": True})
    ]
    concurrent.futures.wait(futures)

# Step 3: Run normalized_token_match.py
subprocess.run([python_exe, normalized_match_script], check=True)

# Step 4: Construct prompts
azure_text_dir = r"H:\\OCR_Automation\\FULLTEXT_OCR\\azure_text"
google_text_dir = r"H:\\OCR_Automation\\FULLTEXT_OCR\\google_text"
unmatched_tokens_dir = r"H:\\OCR_Automation\\UNMATCHED_TOKENS"

prompts = []

for azure_file in glob.glob(os.path.join(azure_text_dir, "*.txt")):
    file_id = os.path.splitext(os.path.basename(azure_file))[0]
    google_file = os.path.join(google_text_dir, f"{file_id}.txt")
    unmatched_file = os.path.join(unmatched_tokens_dir, f"{file_id}.txt")

    if not os.path.exists(google_file) or not os.path.exists(unmatched_file):
        continue

    with open(azure_file, "r", encoding="utf-8") as f:
        azure_text = f.read().strip()

    with open(google_file, "r", encoding="utf-8") as f:
        google_text = f.read().strip()

    with open(unmatched_file, "r", encoding="utf-8") as f:
        unmatched_tokens = f.read().strip()

    prompt = f"""You are an OCR validation assistant. 
Your goal is to check mismatched tokens between two OCR systems (Azure OCR vs Google OCR) 
and determine if they affect critical fields in the document. 
Be precise and structured in your reasoning.

Here is the OCR validation context.
 
Full Azure OCR Reconstructed Text:
<<<{azure_text}>>>
 
Full Google OCR Reconstructed Text:
<<<{google_text}>>>
 
Unmatched Tokens (from Google not found in Azure):
<<<{unmatched_tokens}>>>
 
Critical Fields to Validate:
1. Policy Number
2. Collateral ID (VIN)
3. Loan Number
4. Policy Holder Name
5. Policy Holder Address
 
Task:
- Check if any of the unmatched tokens could correspond to or impact these critical fields. 
- Highlight potential mismatches in these fields.
- Generate clear pointers for the testing team on which areas need closer manual validation.
- If tokens are not related to critical fields, explicitly say they are safe to ignore.
- Respond in JSON with structure:

{{
  "impacted_fields": [
      {{
        "field": "<Critical Field Name>",
        "unmatched_tokens": ["..."],
        "explanation": "<reason why this mismatch matters>"
      }}
  ],
  "safe_tokens": ["..."],
  "testing_team_pointers": [
      "Pointer 1",
      "Pointer 2"
  ]
}}"""

    prompts.append({"file_id": file_id, "prompt": prompt})

# Save prompts to file
with open("ocr_validation_prompts.json", "w", encoding="utf-8") as f:
    json.dump(prompts, f, indent=2)

print(f"✅ Generated {len(prompts)} OCR validation prompts.")