# backend/services/ai_service.py
import os
import openai
import json

try:
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except openai.OpenAIError as e:
    print(f"Error initializing OpenAI client: {e}")
    client = None

async def classify_intent(message: str) -> str:
    """
    Makes a quick, non-streaming call to the LLM to classify user intent.
    """
    if not client:
        return "ERROR"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an intent classifier. Classify the user's message as either 'GREETING' for general conversation and greetings, or 'SEARCH' for questions that require looking up information in a document. Respond with only one of these two words."},
                {"role": "user", "content": message}
            ],
            temperature=0,
            max_tokens=5
        )
        intent = response.choices[0].message.content.strip().upper()
        return intent if intent in ["GREETING", "SEARCH"] else "SEARCH"
    except Exception as e:
        print(f"Error classifying intent: {e}")
        return "SEARCH" # Default to search if classification fails

async def stream_greeting_response(conversation_history: list):
    """
    Streams a simple, conversational response for greetings.
    """
    if not client:
        yield 'data: {"type": "error", "content": "OpenAI client is not initialized."}\n\n'
        return

    system_prompt = "You are a friendly and helpful assistant named TravelAbility Assistant. Respond concisely to the user's greeting or general conversation."
    
    messages_to_send = [{"role": "system", "content": system_prompt}]
    messages_to_send.extend(conversation_history[-4:])

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages_to_send,
            temperature=0.5,
            max_tokens=150,
            stream=True
        )
        for chunk in response:
            if hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content:
                yield f'data: {json.dumps({"type": "content", "content": chunk.choices[0].delta.content})}\n\n'
        yield 'data: {"type": "done"}\n\n'
    except Exception as e:
        print(f"Error streaming greeting: {e}")
        yield f'data: {{"type": "error", "content": "An unexpected error occurred."}}\n\n'


async def stream_rag_response(message: str, pdf_context: str, conversation_history: list):
    """
    Generates a RAG response with citations, based on provided context.
    (This is your previous, highly-tuned prompt)
    """
    if not client:
        yield 'data: {"type": "error", "content": "OpenAI client is not initialized."}\n\n'
        return

    system_prompt = f"""
    You are an expert assistant named TravelAbility Assistant. Your task is to answer the user's questions based EXCLUSIVELY on the provided context within the <source> tags.

    **STRICT RULES:**
    1.  **Cite As You Write:** For every piece of information or sentence you extract from a source, you MUST add an inline citation immediately after it, using the format `<sup>Page X</sup>`, where X is the page number from the <source> tag.
    2.  **Cite Multiple Sources:** If a single sentence combines information from multiple sources, cite all of them. Example: `The information comes from multiple places <sup>Page 15, Page 45</sup>`.
    3.  **No Outside Knowledge:** DO NOT use any prior or external knowledge. If the answer is not found in the provided sources, you MUST state: "I could not find an answer in the provided document."
    4.  **Absolute Precision:** Attribute information with total accuracy. Your credibility depends on this.

    ---
    Now, use the following context to answer the user's question.

    CONTEXT:
    {pdf_context}
    """
    
    messages_to_send = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages_to_send,
            temperature=0.2,
            max_tokens=500,
            stream=True
        )
        for chunk in response:
            if hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content:
                yield f'data: {json.dumps({"type": "content", "content": chunk.choices[0].delta.content})}\n\n'
        yield 'data: {"type": "done"}\n\n'
    except Exception as e:
        print(f"Error in RAG stream: {e}")
        yield f'data: {{"type": "error", "content": "An error occurred while processing your document question."}}\n\n'