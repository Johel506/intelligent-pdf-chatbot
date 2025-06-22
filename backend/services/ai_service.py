# backend/services/ai_service.py
import os
import openai

try:
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except openai.OpenAIError as e:
    print(f"Error initializing OpenAI client: {e}")
    client = None

async def get_ai_response(message: str, pdf_context: str, conversation_history: list) -> str:
    """
    Generates a response from the OpenAI API by providing the PDF context,
    conversation history, and the latest user message.
    """
    if not client:
        return "OpenAI client is not initialized. Please check your API key."

    # Truncate the PDF context to a safe character limit to avoid exceeding token limits.
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

    # The conversation_history from main.py already includes previous user/assistant messages.
    # We create the final message list for the API.
    messages_to_send = [
        {"role": "system", "content": system_prompt}
    ]
    # Add the last 4 messages from history to keep conversation context
    messages_to_send.extend(conversation_history[-4:])
    
    try:
        print("Sending request to OpenAI API...")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages_to_send,
            temperature=0.2,
            max_tokens=500
        )

        ai_response = response.choices[0].message.content
        print("✅ Received response from OpenAI API.")
        return ai_response

    except openai.APIError as e:
        error_message = str(e)
        if "context_length_exceeded" in error_message:
            print(f"CONTEXT LENGTH ERROR: {error_message}")
            return "The provided document is too long for the AI model to process."
        else:
            print(f"OPENAI API ERROR: {error_message}")
            return "I'm sorry, an error occurred while communicating with the AI service."
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return "An unexpected error occurred on the server."