# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os
from dotenv import load_dotenv

# Import our new PDF specialist function
from services.pdf_service import extract_text_from_pdf

load_dotenv()  # Load environment variables from .env file

app = FastAPI(
    title="Intelligent PDF Chatbot API",
    description="A contect-aware chatbot that answers questions based on a PDF document.",
    version="1.0.0",
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Application Events ---
@app.on_event("startup")
def startup_event():
    """
    This function runs once when the API starts up.
    It's the perfect place to load the PDF context. 
    """
    global PDF_CONTEXT
    # Use the environment variable to find the PDF
    pdf_path = os.getenv("PDF_PATH")
    
    if not pdf_path:
        print("⚠️ PDF_PATH environment variable not set.")
        return

    # Call our service to do the heavy lifting
    PDF_CONTEXT = extract_text_from_pdf(pdf_path)
    
    if not PDF_CONTEXT:
        print("❌ Could not load PDF context. The API will work without it.")


# --- Data Models (Pydantic) ---
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    pdf_loaded: bool

# --- API Endpoints ---
@app.get("/")
async def root():
    return {"message": "PDF Chatbot API is online."}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Endpoint to check the health and status of the API. 
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        pdf_loaded=bool(PDF_CONTEXT) # True if PDF_CONTEXT has text, False otherwise
    )