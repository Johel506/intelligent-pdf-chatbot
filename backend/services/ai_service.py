# backend/services/ai_service.py
import os
import openai
import json # <-- ¡Asegúrate de importar json!

try:
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except openai.OpenAIError as e:
    print(f"Error initializing OpenAI client: {e}")
    client = None

def stream_ai_response(message: str, pdf_context: str, conversation_history: list):
    """
    Genera una respuesta de la API de OpenAI y la transmite por partes usando yield para streaming SSE.
    """
    if not client:
        # Asegúrate de que los mensajes de error también sean JSON válido
        yield 'data: {"type": "error", "content": "OpenAI client is not initialized."}\n\n'
        return

    safe_context = pdf_context[:48000]
    system_prompt = f"""
    You are a helpful assistant named TravelAbility Assistant. Answer questions exclusively based on the DOCUMENT CONTENT provided below.
    Do not use external knowledge. If the answer is not in the document, state that you cannot find the answer in the provided document.
    If the user asks for the exact wording of a section or quote, provide it verbatim from the DOCUMENT CONTENT.

    DOCUMENT CONTENT:
    ---
    {safe_context}
    ---
    """

    messages_to_send = [
        {"role": "system", "content": system_prompt}
    ]
    messages_to_send.extend(conversation_history[-4:])

    try:
        print("Sending request to OpenAI API (streaming)...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages_to_send,
            temperature=0.2,
            max_tokens=500,
            stream=True
        )

        for chunk in response:
            if hasattr(chunk.choices[0].delta, "content"):
                content = chunk.choices[0].delta.content
                if content:
                    # **Línea corregida:** Serializa el diccionario a un string JSON
                    yield f'data: {json.dumps({"type": "content", "content": content})}\n\n'
        
        # Indica al frontend que terminó
        yield 'data: {"type": "done"}\n\n'

    except openai.APIError as e:
        error_message = str(e)
        if "context_length_exceeded" in error_message:
            print(f"CONTEXT LENGTH ERROR: {error_message}")
            yield 'data: {"type": "error", "content": "The provided document is too long for the AI model to process."}\n\n'
        else:
            print(f"OPENAI API ERROR: {error_message}")
            yield 'data: {"type": "error", "content": "I\'m sorry, an error occurred while communicating with the AI service."}\n\n'
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        yield f'data: {{"type": "error", "content": "An unexpected error occurred on the server."}}\n\n'