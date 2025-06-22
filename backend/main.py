# backend/main.py

# --- Step 1: Load environment variables FIRST ---
from dotenv import load_dotenv
import os
load_dotenv()

# --- Step 2: Import other libraries and services AFTER loading variables ---
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Now we can safely import our services
# We are disabling this specific Pylint warning because we have a good reason
# to load environment variables before this import.
from services.pdf_service import extract_text_from_pdf
from services.ai_service import stream_ai_response  # pylint: disable=C0413


# --- Global In-Memory Storage ---
PDF_CONTEXT = ""
CONVERSATION_HISTORY = {} 

app = FastAPI(
    title="Intelligent PDF Chatbot API",
    description="A context-aware chatbot that answers questions based on a PDF document.",
    version="1.0.0"
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    """
    Loads the PDF content into the global PDF_CONTEXT variable when the application starts.
    """
    global PDF_CONTEXT
    pdf_path = os.getenv("PDF_PATH")
    if not pdf_path:
        print("⚠️ PDF_PATH environment variable not set.")
        return
    PDF_CONTEXT = extract_text_from_pdf(pdf_path) #
    if not PDF_CONTEXT:
        print("❌ Could not load PDF context.")

# --- Pydantic Data Models ---
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    pdf_loaded: bool

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = "default" #

# --- API Endpoints ---
@app.get("/")
async def root():
    return {"message": "PDF Chatbot API is online."}

@app.get("/health", response_model=HealthResponse)
async def health_check(): #
    """Endpoint to verify the API's status and if the PDF was loaded."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        pdf_loaded=bool(PDF_CONTEXT)
    )



@app.post("/chat")
async def chat_endpoint(message: ChatMessage): 
    """
    Main endpoint to receive user messages and stream an AI response.
    This supports real-time streaming using Server-Sent Events (SSE). 
    """
    global CONVERSATION_HISTORY

    if not PDF_CONTEXT:
        raise HTTPException(status_code=503, detail="PDF context is not loaded yet.")

    conversation_id = message.conversation_id
    
    if conversation_id not in CONVERSATION_HISTORY:
        CONVERSATION_HISTORY[conversation_id] = []
    
    user_message_entry = {"role": "user", "content": message.message}
    CONVERSATION_HISTORY[conversation_id].append(user_message_entry)

    # Return the special StreamingResponse object that calls our generator
    return StreamingResponse(
        stream_ai_response(
            message=message.message,
            pdf_context=PDF_CONTEXT, 
            conversation_history=CONVERSATION_HISTORY[conversation_id]
        ), 
        media_type="text/event-stream"
    )
