# backend/services/pdf_service.py
import PyPDF2
import os

def extract_text_from_pdf(pdf_path: str) -> str | None:
    """
    Opens and extracts text from a PDF file.
    Returns the extracted text or None if an error occurs.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at path: {pdf_path}")
        return None
    
    try:
        print(f"Loading PDF from: {pdf_path}...")
        text_content = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
        print("✅ PDF loaded and text extracted successfully.")
        return text_content
    except Exception as e:
        print(f"Error reading the PDF file: {e}")
        return None