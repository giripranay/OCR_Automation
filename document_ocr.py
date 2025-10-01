from google.cloud import documentai_v1 as documentai

def process_document_ocr(project_id: str, location: str, processor_id: str, file_path: str):
    """
    Uses Document AI OCR processor to extract text from a PDF or image.
    """
    # Create the client
    client = documentai.DocumentProcessorServiceClient()

    # Full resource name of the processor
    name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"

    # Read the file into memory
    with open(file_path, "rb") as f:
        document_content = f.read()

    # Create RawDocument
    raw_document = documentai.RawDocument(content=document_content, mime_type="application/pdf")

    # Configure the request
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)

    # Process the document
    result = client.process_document(request=request)

    # OCR result
    document = result.document

    print("=== OCR Text Extraction ===")
    print(document.text)

    return document.text


if __name__ == "__main__":
    project_id = "docuemntocr"
    location = "us"  # or "eu"
    processor_id = "503a951e1331a5be"
    file_path = "c:\\Users\\girip\\Downloads\\test_insurance.pdf"

    text = process_document_ocr(project_id, location, processor_id, file_path)
