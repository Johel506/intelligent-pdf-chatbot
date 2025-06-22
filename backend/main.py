# backend/main.py

# --- Step 1: Load environment variables FIRST ---
# This ensures that any subsequent module imports have access to the environment variables.
from dotenv import load_dotenv
import os
load_dotenv()
print(f"OpenAI API Key loaded: {os.getenv('OPENAI_API_KEY')[:15] if os.getenv('OPENAI_API_KEY') else 'None'}") # You can remove this diagnostic line later

# --- Step 2: Import other libraries and services AFTER loading variables ---
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Now we can safely import our services
from services.pdf_service import extract_text_from_pdf
from services.ai_service import get_ai_response

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
    allow_origins=["http://localhost:3000"],
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
    """Main endpoint to receive user messages and return an AI response."""
    global CONVERSATION_HISTORY

    if not PDF_CONTEXT:
        raise HTTPException(status_code=503, detail="PDF context is not loaded yet.")

    conversation_id = message.conversation_id
    
    if conversation_id not in CONVERSATION_HISTORY:
        CONVERSATION_HISTORY[conversation_id] = []
    
    # Add user message to history
    user_message_entry = {"role": "user", "content": message.message}
    CONVERSATION_HISTORY[conversation_id].append(user_message_entry)

    # Pass the current history (which includes the new user message) to the AI service
    ai_response_content = await get_ai_response(
        message=message.message,
        pdf_context=PDF_CONTEXT,
        conversation_history=CONVERSATION_HISTORY[conversation_id]
    )

    # Add AI response to history
    CONVERSATION_HISTORY[conversation_id].append({"role": "assistant", "content": ai_response_content})

    return {"response": ai_response_content}

