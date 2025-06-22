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
        # Lanza una excepción para detener el inicio del servidor
        raise RuntimeError("PDF_PATH environment variable not set.")
    
    PDF_CONTEXT = extract_text_from_pdf(pdf_path)
    if not PDF_CONTEXT:
        print(f"❌ CRITICAL ERROR: Could not load PDF context from '{pdf_path}'. Application cannot start.")
        # Lanza una excepción para detener el inicio del servidor
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

    # 1. Añadir el mensaje del usuario al historial
    user_message_entry = {"role": "user", "content": message.message}
    CONVERSATION_HISTORY[conversation_id].append(user_message_entry)

    # Variable para acumular la respuesta completa del asistente
    full_ai_response_content = ""

    # Función generadora asíncrona para procesar el stream
    async def response_stream_generator():
        nonlocal full_ai_response_content # Permite modificar la variable externa

        # Llamar a stream_ai_response para obtener los chunks
        # Nota: stream_ai_response en services/ai_service.py devuelve `data: JSON_STRING\n\n`
        async for chunk_data in stream_ai_response(
            message=message.message,
            pdf_context=PDF_CONTEXT,
            conversation_history=CONVERSATION_HISTORY[conversation_id] # Pasa el historial actual
        ):
            # Parsear el chunk para extraer el contenido real
            # Esto asume el formato 'data: {"type": "content", "content": "..."}\n\n'
            try:
                line = chunk_data.strip()
                if line.startswith("data: "):
                    json_payload = json.loads(line[len("data: "):])
                    if json_payload.get("type") == "content":
                        content_part = json_payload.get("content", "")
                        full_ai_response_content += content_part
                
                # Cuidado: Si el cliente espera `data: ...` y tú solo envías `content`,
                # el frontend podría necesitar ajustarse. Asumimos que el frontend
                # espera el mismo formato de `chunk_data` que `ai_service.py` genera.
                yield chunk_data # Reenviar el chunk al cliente inmediatamente
            except json.JSONDecodeError:
                # Manejar chunks que no son JSON válidos (ej. el chunk 'done')
                yield chunk_data # Aún se envía para no romper el stream del cliente

        # 3. Después de que el generador termine (todo el stream ha sido procesado),
        # guardar la respuesta completa del asistente en el historial.
        # Esto sucede DESPUÉS de que todos los 'yield' se han ejecutado.
        if full_ai_response_content: # Asegurarse de que haya contenido para guardar
            assistant_message_entry = {"role": "assistant", "content": full_ai_response_content}
            CONVERSATION_HISTORY[conversation_id].append(assistant_message_entry)
            print(f"✅ AI Response saved to history for conversation_id: {conversation_id}")
            # print(f"Current history for {conversation_id}: {CONVERSATION_HISTORY[conversation_id]}") # Para depuración
        else:
            print(f"⚠️ AI Response was empty for conversation_id: {conversation_id}, not saved.")

    # Retornar el StreamingResponse que usa nuestro nuevo generador
    return StreamingResponse(
        response_stream_generator(), # Usamos nuestra nueva función generadora
        media_type="text/event-stream"
    )