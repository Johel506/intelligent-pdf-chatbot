# backend/services/ai_service.py
import os
import openai
import json # <-- Make sure to import json!

try:
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except openai.OpenAIError as e:
    print(f"Error initializing OpenAI client: {e}")
    client = None

async def stream_ai_response(message: str, pdf_context: str, conversation_history: list):
    """
   Generates a response from the OpenAI API and streams it in parts using yield for SSE (Server-Sent Events).
    """
    if not client:
        # Ensure that error messages are also valid JSON
        yield 'data: {"type": "error", "content": "OpenAI client is not initialized."}\n\n'
        return

    system_prompt = f"""
    You are a helpful assistant named TravelAbility Assistant.
    Your main goal is to provide concise and accurate answers based *only* on the RELEVANT DOCUMENT EXCERPTS provided below.
    Do not use external knowledge.
    If the answer is not in the provided excerpts, state clearly that you cannot find the answer in the provided information.

    RELEVANT DOCUMENT EXCERPTS:
    ---
    {pdf_context} 
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
                    # Serialize the dictionary to a JSON string
                    yield f'data: {json.dumps({"type": "content", "content": content})}\n\n'
        
        # Indicate to the frontend that it's finished
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