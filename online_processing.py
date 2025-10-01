# mypy: disable-error-code="1"
"""
Makes an Online Processing Request to Document AI
and saves the raw OCR text to a file.
"""
import os
from google.api_core.client_options import ClientOptions
from google.cloud import documentai

PROJECT_ID = "docuemntocr"
LOCATION = "us"  # Format is 'us' or 'eu'
PROCESSOR_ID = "503a951e1331a5be"  # Create processor in Cloud Console

FILE_PATH = "c:\\Users\\girip\\Downloads\\Infrrd.pdf"
MIME_TYPE = "application/pdf"

# Output folder
OUTPUT_FOLDER = "RAW_OCR"

# Instantiates a client
docai_client = documentai.DocumentProcessorServiceClient(
    client_options=ClientOptions(api_endpoint=f"{LOCATION}-documentai.googleapis.com")
)

# Full resource name of the processor
name = docai_client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID)

# Read the file into memory
with open(FILE_PATH, "rb") as f:
    image_content = f.read()

# Load Binary Data into Document AI RawDocument Object
raw_document = documentai.RawDocument(content=image_content, mime_type=MIME_TYPE)

# Configure the process request
request = documentai.ProcessRequest(name=name, raw_document=raw_document)

# Process the document
result = docai_client.process_document(request=request)

document_object = result.document
print("Document processing complete.")

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Construct output file path
input_filename = os.path.basename(FILE_PATH)
output_filename = os.path.splitext(input_filename)[0] + ".txt"
output_path = os.path.join(OUTPUT_FOLDER, output_filename)

# Save extracted text to file
with open(output_path, "w", encoding="utf-8") as f:
    f.write(document_object.text)

print(f"Raw OCR text saved to: {output_path}")
