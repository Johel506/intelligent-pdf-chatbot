# backend/services/pdf_service.py
import PyPDF2
import os
from langchain.docstore.document import Document

def extract_documents_from_pdf(pdf_path: str) -> list[Document]:
    """
    Opens and extracts text from each page of a PDF file,
    creating a LangChain Document object per page with metadata.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at path: {pdf_path}")
        return []

    print(f"Loading PDF from: {pdf_path}...")
    documents = []
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for i, page in enumerate(pdf_reader.pages):
                page_content = page.extract_text()
                if page_content:
                    # Create a LangChain Document with metadata
                    doc = Document(
                        page_content=page_content,
                        metadata={'page_number': i + 1, 'source': os.path.basename(pdf_path)}
                    )
                    documents.append(doc)
        print(f"✅ PDF loaded and split into {len(documents)} page documents.")
        return documents
    except Exception as e:
        print(f"Error reading the PDF file: {e}")
        return []