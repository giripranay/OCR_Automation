# mypy: disable-error-code="1"
"""
Automated pipeline: PDF -> Google Document AI -> Raw OCR -> LLM field extraction -> JSON
"""
import os
import json
from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from openai import OpenAI

# --- Configuration ---
PROJECT_ID = "docuemntocr"
LOCATION = "us"
PROCESSOR_ID = "503a951e1331a5be"

INPUT_PDF_FOLDER = "PDF_INPUTS"  # Place PDFs here
RAW_OCR_FOLDER = "RAW_OCR"
EXTRACTED_FOLDER = "EXTRACTED_OCR_DATA"

os.makedirs(RAW_OCR_FOLDER, exist_ok=True)
os.makedirs(EXTRACTED_FOLDER, exist_ok=True)

# LLM fields
FIELDS = ["Policy Number", "Collateral ID (VIN)", "Loan Number", "Policy Holder Name", "Policy Holder Address"]

# Initialize clients
docai_client = documentai.DocumentProcessorServiceClient(
    client_options=ClientOptions(api_endpoint=f"{LOCATION}-documentai.googleapis.com")
)
llm_client = OpenAI(api_key="YOUR_OPENAI_API_KEY")  # Replace with your key

# --- Functions ---
def process_pdf_with_docai(pdf_path: str) -> str:
    """Processes a PDF with Google Document AI and returns the extracted text."""
    with open(pdf_path, "rb") as f:
        content = f.read()
    raw_document = documentai.RawDocument(content=content, mime_type="application/pdf")
    name = docai_client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID)
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)
    result = docai_client.process_document(request=request)
    return result.document.text

def save_raw_text(text: str, pdf_filename: str) -> str:
    """Save raw OCR text to RAW_OCR folder."""
    output_filename = os.path.splitext(pdf_filename)[0] + ".txt"
    output_path = os.path.join(RAW_OCR_FOLDER, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    return output_path

def extract_fields_from_text(text: str) -> dict:
    """Pass text to LLM to extract key fields."""
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
    response = llm_client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
        # temperature=0
    )
    try:
        content = response.choices[0].message.content.strip()
        data = json.loads(content)
    except Exception as e:
        print("Error parsing LLM output, returning nulls:", e)
        data = {field: None for field in FIELDS}
    return data

def save_json(data: dict, pdf_filename: str) -> str:
    """Save extracted JSON to EXTRACTED_OCR_DATA folder."""
    output_filename = os.path.splitext(pdf_filename)[0] + ".json"
    output_path = os.path.join(EXTRACTED_FOLDER, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return output_path

# --- Main Pipeline ---
for pdf_file in os.listdir(INPUT_PDF_FOLDER):
    if not pdf_file.lower().endswith(".pdf"):
        continue
    pdf_path = os.path.join(INPUT_PDF_FOLDER, pdf_file)
    
    print(f"Processing PDF: {pdf_file}")
    
    # 1. Document AI OCR
    text = process_pdf_with_docai(pdf_path)
    
    # 2. Save raw OCR text
    raw_text_path = save_raw_text(text, pdf_file)
    print(f"Raw OCR saved: {raw_text_path}")
    
    # 3. Extract fields with LLM
    extracted_data = extract_fields_from_text(text)
    
    # 4. Save JSON
    json_path = save_json(extracted_data, pdf_file)
    print(f"Extracted fields saved: {json_path}")
    print("-" * 50)
