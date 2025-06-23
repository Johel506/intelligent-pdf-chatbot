# backend/main.py

# Step 1: Load environment variables
from dotenv import load_dotenv
import os
load_dotenv()

# Step 2: Import libraries and services after loading environment variables
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from contextlib import asynccontextmanager
import json

from services.pdf_service import extract_documents_from_pdf
from services.ai_service import classify_intent, stream_greeting_response, stream_rag_response

# In-memory storage for vector database and conversation history
VECTOR_STORE = None
CONVERSATION_HISTORY = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup logic: Loads documents from PDF, splits them into chunks
    while preserving metadata, and creates the FAISS vector store.
    """
    global VECTOR_STORE

    from langchain_community.vectorstores import FAISS
    from langchain_openai import OpenAIEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    print("Lifespan event: startup")
    pdf_path = os.getenv("PDF_PATH")
    if not pdf_path:
        raise RuntimeError("PDF_PATH environment variable not set.")

    print("Loading PDF for RAG pipeline...")
    page_documents = extract_documents_from_pdf(pdf_path)
    if not page_documents:
        raise RuntimeError(f"Could not load any documents from '{pdf_path}'.")

    # Split documents into chunks (splitter preserves metadata)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(page_documents)
    print(f"PDF processed into {len(chunks)} chunks.")

    # Create embeddings and FAISS vector store
    embeddings = OpenAIEmbeddings()
    VECTOR_STORE = FAISS.from_documents(documents=chunks, embedding=embeddings)
    print("✅ FAISS vector store with metadata created successfully.")

    yield

    print("Lifespan event: shutdown")

app = FastAPI(
    title="Intelligent PDF Chatbot API",
    description="A context-aware chatbot that answers questions based on a PDF document.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    pdf_loaded: bool

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = "default"

@app.get("/")
async def root():
    return {"message": "PDF Chatbot API is online."}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Endpoint to verify the API's status and if the PDF was loaded."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        pdf_loaded=bool(VECTOR_STORE)
    )

@app.post("/chat")
async def chat_endpoint(message: ChatMessage):
    """
    Routes the message: classifies intent, then handles either RAG or greeting.
    """
    global CONVERSATION_HISTORY, VECTOR_STORE
    if not VECTOR_STORE:
        raise HTTPException(status_code=503, detail="Vector store not initialized.")

    conversation_id = message.conversation_id
    if conversation_id not in CONVERSATION_HISTORY:
        CONVERSATION_HISTORY[conversation_id] = []

    # Add user message to history
    user_message_entry = {"role": "user", "content": message.message}
    CONVERSATION_HISTORY[conversation_id].append(user_message_entry)

    # Intent routing
    intent = await classify_intent(message.message)
    print(f"User intent classified as: {intent}")

    if intent == "GREETING":
        async def greeting_generator():
            full_response = ""
            async for chunk in stream_greeting_response(CONVERSATION_HISTORY[conversation_id]):
                try:
                    line = chunk.strip()
                    if line.startswith("data: "):
                        json_payload = json.loads(line[len("data: "):])
                        if json_payload.get("type") == "content":
                            full_response += json_payload.get("content", "")
                except json.JSONDecodeError:
                    pass
                yield chunk
            if full_response:
                CONVERSATION_HISTORY[conversation_id].append({"role": "assistant", "content": full_response})

        return StreamingResponse(greeting_generator(), media_type="text/event-stream")
    else:
        # Handle RAG questions
        retriever = VECTOR_STORE.as_retriever(search_kwargs={"k": 4})
        relevant_docs = retriever.get_relevant_documents(message.message)
        source_list = [{"page_number": doc.metadata.get('page_number', 'N/A'), "content": doc.page_content} for doc in relevant_docs]
        rag_context = "\n\n".join([f'<source page="{doc.metadata.get("page_number", "N/A")}">\n{doc.page_content}\n</source>' for doc in relevant_docs])

        async def rag_generator():
            full_response = ""
            sources_payload = json.dumps({"type": "sources", "sources": source_list})
            yield f'data: {sources_payload}\n\n'
            async for chunk in stream_rag_response(message.message, rag_context, CONVERSATION_HISTORY[conversation_id]):
                try:
                    line = chunk.strip()
                    if line.startswith("data: "):
                        json_payload = json.loads(line[len("data: "):])
                        if json_payload.get("type") == "content":
                            full_response += json_payload.get("content", "")
                except json.JSONDecodeError:
                    pass
                yield chunk
            if full_response:
                 CONVERSATION_HISTORY[conversation_id].append({"role": "assistant", "content": full_response, "sources": source_list})

        return StreamingResponse(rag_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)