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
   You are an expert assistant named TravelAbility Assistant. Your task is to answer the user's questions based EXCLUSIVELY on the provided context within the <source> tags.

    **STRICT RULES:**
    1.  **Cite As You Write:** For every piece of information or sentence you extract from a source, you MUST add an inline citation immediately after it, using the format `<sup>Page X</sup>`, where X is the page number from the <source> tag.
    2.  **Cite Multiple Sources:** If a single sentence combines information from multiple sources, cite all of them. Example: `The information comes from multiple places <sup>Page 15, Page 45</sup>`.
    3.  **No Outside Knowledge:** DO NOT use any prior or external knowledge. If the answer is not found in the provided sources, you MUST state: "I could not find an answer in the provided document."
    4.  **Absolute Precision:** Attribute information with total accuracy. Your credibility depends on this.

    ---
    **EXAMPLE OF HOW TO WORK:**

    **Provided Context:**
    <source page="15">
    The global disability market is estimated at 1.85 billion people. This equates to 66 million in the United States.
    </source>
    <source page="25">
    An accessible website must have screen-reader compatible web pages and all images must have "alt tags".
    </source>

    **User's Question:**
    What is the size of the disability market and what does a website need to be accessible?

    **Expected Answer:**
    The global disability market is estimated at 1.85 billion people, with 66 million of them in the United States <sup>Page 15</sup>.

    For a website to be accessible, it must be compatible with screen readers and its images must have "alt tags" <sup>Page 25</sup>.
    ---

    Now, use the following context to answer the user's question.

    CONTEXT:
    {pdf_context}
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