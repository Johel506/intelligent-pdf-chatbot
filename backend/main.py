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
# PDF_CONTEXT = "" <-- We no longer need this
VECTOR_STORE = None # <-- We will store our vector database here
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
    Loads the PDF, splits it into chunks, creates embeddings, and stores them
    in an in-memory FAISS vector database.
    """
    global VECTOR_STORE
    from langchain_community.vectorstores import FAISS
    from langchain_openai import OpenAIEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    pdf_path = os.getenv("PDF_PATH")
    if not pdf_path:
        raise RuntimeError("PDF_PATH environment variable not set.")
    print("Loading PDF for RAG pipeline...")
    pdf_text = extract_text_from_pdf(pdf_path)
    if not pdf_text:
        raise RuntimeError(f"Could not load PDF context from '{pdf_path}'.")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    chunks = text_splitter.split_text(pdf_text)
    print(f"PDF split into {len(chunks)} chunks.")
    embeddings = OpenAIEmbeddings()
    VECTOR_STORE = FAISS.from_texts(texts=chunks, embedding=embeddings)
    print("✅ FAISS vector store created successfully.")


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
        pdf_loaded=bool(VECTOR_STORE)
    )



@app.post("/chat")
async def chat_endpoint(message: ChatMessage):
    """
    Chat endpoint that uses a RAG pipeline to get answers.
    """
    global CONVERSATION_HISTORY, VECTOR_STORE
    if not VECTOR_STORE:
        raise HTTPException(status_code=503, detail="Vector store is not initialized yet.")
    conversation_id = message.conversation_id
    if conversation_id not in CONVERSATION_HISTORY:
        CONVERSATION_HISTORY[conversation_id] = []
    user_message_entry = {"role": "user", "content": message.message}
    CONVERSATION_HISTORY[conversation_id].append(user_message_entry)
    full_ai_response_content = ""
    # --- RAG Logic ---
    print(f"Searching for relevant chunks for: '{message.message}'")
    retriever = VECTOR_STORE.as_retriever(search_kwargs={"k": 4})
    relevant_docs = retriever.get_relevant_documents(message.message)
    rag_context = "\n\n---\n\n".join([doc.page_content for doc in relevant_docs])
    print("RAG context created.")
    async def response_stream_generator():
        nonlocal full_ai_response_content
        async for chunk_data in stream_ai_response(
            message=message.message,
            pdf_context=rag_context,
            conversation_history=CONVERSATION_HISTORY[conversation_id]
        ):
            try:
                line = chunk_data.strip()
                if line.startswith("data: "):
                    import json
                    json_payload = json.loads(line[len("data: "):])
                    if json_payload.get("type") == "content":
                        content_part = json_payload.get("content", "")
                        full_ai_response_content += content_part
                yield chunk_data
            except Exception:
                yield chunk_data
        if full_ai_response_content:
            assistant_message_entry = {"role": "assistant", "content": full_ai_response_content}
            CONVERSATION_HISTORY[conversation_id].append(assistant_message_entry)
            print(f"✅ AI Response saved to history for conversation_id: {conversation_id}")
        else:
            print(f"⚠️ AI Response was empty for conversation_id: {conversation_id}, not saved.")
    return StreamingResponse(
        response_stream_generator(),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)