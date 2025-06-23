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
import json

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
    If PDF loading fails, raises an exception to prevent the application from starting.
    """
    global PDF_CONTEXT
    pdf_path = os.getenv("PDF_PATH")
    if not pdf_path:
        print("❌ CRITICAL ERROR: PDF_PATH environment variable not set. Application cannot start.")
        # Raises an exception to stop the server startup
        raise RuntimeError("PDF_PATH environment variable not set.")
    
    PDF_CONTEXT = extract_text_from_pdf(pdf_path)
    if not PDF_CONTEXT:
        print(f"❌ CRITICAL ERROR: Could not load PDF context from '{pdf_path}'. Application cannot start.")
        # Raises an exception to stop the server startup
        raise RuntimeError(f"Could not load PDF context from '{pdf_path}'.")
    else:
        print("✅ PDF loaded and text extracted successfully during startup.")


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
    It now also captures and saves the AI's full response to conversation history.
    """
    global CONVERSATION_HISTORY

    if not PDF_CONTEXT:
        raise HTTPException(status_code=503, detail="PDF context is not loaded yet.")

    conversation_id = message.conversation_id

    if conversation_id not in CONVERSATION_HISTORY:
        CONVERSATION_HISTORY[conversation_id] = []

    # 1. Add the user message to the history
    user_message_entry = {"role": "user", "content": message.message}
    CONVERSATION_HISTORY[conversation_id].append(user_message_entry)

    # Variable to accumulate the complete assistant response
    full_ai_response_content = ""

    # Async generator function to process the stream
    async def response_stream_generator():
        nonlocal full_ai_response_content # Allows modifying the external variable

        # Call stream_ai_response to get the chunks
        # Note: stream_ai_response in services/ai_service.py returns `data: JSON_STRING\n\n`
        async for chunk_data in stream_ai_response(
            message=message.message,
            pdf_context=PDF_CONTEXT,
            conversation_history=CONVERSATION_HISTORY[conversation_id] # Pass the current history
        ):
            # Parse the chunk to extract the real content
            # This assumes the format 'data: {"type": "content", "content": "..."}\n\n'
            try:
                line = chunk_data.strip()
                if line.startswith("data: "):
                    json_payload = json.loads(line[len("data: "):])
                    if json_payload.get("type") == "content":
                        content_part = json_payload.get("content", "")
                        full_ai_response_content += content_part
                
                # Careful: If the client expects `data: ...` and you only send `content`,
                # the frontend might need to be adjusted. We assume the frontend
                # expects the same format of `chunk_data` that `ai_service.py` generates.
                yield chunk_data # Forward the chunk to the client immediately
            except json.JSONDecodeError:
                # Handle chunks that are not valid JSON (e.g. the 'done' chunk)
                yield chunk_data # Still sent to avoid breaking the client stream

        # 3. After the generator ends (all stream has been processed),
        # save the complete assistant response to the history.
        # This happens AFTER all 'yield' statements have been executed.
        if full_ai_response_content: # Make sure there's content to save
            assistant_message_entry = {"role": "assistant", "content": full_ai_response_content}
            CONVERSATION_HISTORY[conversation_id].append(assistant_message_entry)
            print(f"✅ AI Response saved to history for conversation_id: {conversation_id}")
            # print(f"Current history for {conversation_id}: {CONVERSATION_HISTORY[conversation_id]}") # For debugging
        else:
            print(f"⚠️ AI Response was empty for conversation_id: {conversation_id}, not saved.")

    # Return the StreamingResponse that uses our new generator
    return StreamingResponse(
        response_stream_generator(), # We use our new generator function
        media_type="text/event-stream"
    )