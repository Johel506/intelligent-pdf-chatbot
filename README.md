# 🤖 Intelligent PDF Chatbot: Your Document Companion!

A context-aware chat application designed to provide instant answers from your PDF documents. Get quick, precise information without sifting through pages!

![Python Version](https://img.shields.io/badge/Python-3.11.9-blue?style=flat-square&logo=python)
![Node.js Version](https://img.shields.io/badge/Node.js-22.16.0-green?style=flat-square&logo=node.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?style=flat-square&logo=fastapi)
![React](https://img.shields.io/badge/React-19.1.0-61DAFB?style=flat-square&logo=react)

---

## ✨ Features

* **PDF-Powered Answers**: Ask questions directly about your PDF content and get accurate, context-rich responses.
* **Real-time AI Streaming**: Experience dynamic, real-time AI responses as they are generated.
* **Intuitive Chat Interface**: A clean, responsive single-page chat for seamless interactions.
* **Conversation History**: Maintains context within your chat session for more natural conversations.
* **Easy Reset**: Clear the chat history with a single click to start a new conversation.

---

## 🚀 Quick Start

Get your Intelligent PDF Chatbot up and running in a few simple steps!

### Prerequisites

Before you begin, ensure you have the following installed:

* **Python**: Version 3.11.9 (tested with this version).
* **Node.js**: Version 22.16.0 (tested with this version).
* **FastAPI**: Version 0.104.1 (will be installed via requirements.txt).
* **React**: Version 19.1.0 (will be installed via npm).
* **OpenAI API Key**: Required for AI model integration.

### Installation

1. **Clone the Repository:**
   ```bash
   git clone <your-repository-url>
   cd intelligent-pdf-chatbot
   ```

2. **Create Environment File:**
   Navigate to the `backend` directory and create your `.env` file.
   ```bash
   cd backend
   cp .env.example .env # If .env.example exists, otherwise create it manually
   ```
   Now, open the newly created `.env` file and add your OpenAI API key and the path to your PDF document:
   ```ini
   OPENAI_API_KEY="your_openai_api_key_here"
   PDF_PATH="./assets/PB_TravelAbility_DI-v3.pdf" # Adjust this path if your PDF is elsewhere
   ```

3. **Run the Backend:**
   From the `backend` directory, install dependencies and start the FastAPI server.
   ```bash
   pip install -r requirements.txt
   python main.py
   ```
   The backend API will start, typically on `http://127.0.0.1:8000`. You should see a message indicating the PDF has been loaded successfully.

4. **Run the Frontend:**
   Open a **new terminal** and navigate to the `frontend` directory. Install dependencies and start the React development server.
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```
   The React development server will start, typically on `http://localhost:5173`.

> ⚠️ **Important**: Make sure to add your OpenAI API key to the `.env` file before running the backend application.
> 
> 💡 **Tip**: For optimal performance and compatibility, it's recommended to use a virtual environment for Python dependencies.

---

## 💬 How to Use

Once both the backend and frontend are running, open your web browser to `http://localhost:5173`.

1. **Type your question** into the message input field.
2. **Click "Send"** or press `Enter`.
3. The AI's response will stream directly into the chat history.
4. Use the **"Reset" button** in the header to clear the conversation and start anew.

---

## 📚 Examples

Here are some example questions you can ask, based on the provided `PB_TravelAbility_DI-v3.pdf` document:

* "What is the Accessibility Playbook?"
* "What are the four common disabilities mentioned?"
* "According to the document, what should you avoid doing when communicating with a blind person?"
* "What is the estimated global disability market?"
* "What are some key features of an accessible website?"

**Expected Response Format:**

AI responses will appear as streaming text, accumulating until the full answer is provided. For instance:

> AI: The Accessibility Playbook, created by TravelAbility and in collaboration with Destinations International, serves as a comprehensive guide to help destination organizations navigate the journey towards creating truly accessible and welcoming environments.

**Which PDFs work best?**

This chatbot performs best with PDFs that contain:
* Clear, selectable text (not scanned images).
* Well-structured content (headings, paragraphs).
* Information directly relevant to the questions you plan to ask.

---

## 🔧 Configuration

This section details environment variables and advanced configurations.

### Environment Variables

* `OPENAI_API_KEY`: Your secret key for accessing the OpenAI API. (Required)
* `PDF_PATH`: The relative or absolute path to the PDF document the chatbot will use as context. (Required)

### AI Model Configuration

The current AI model is hardcoded as `gpt-3.5-turbo`. You can change this in `backend/services/ai_service.py`:

```python
# backend/services/ai_service.py
# ...
response = client.chat.completions.create(
    model="gpt-3.5-turbo", # Change this to another compatible model (e.g., "gpt-4")
    messages=messages_to_send,
    temperature=0.2,
    max_tokens=500,
    stream=True
)
# ...
```

### Token Limits Configuration

* `max_tokens`: In `backend/services/ai_service.py`, `max_tokens` controls the maximum length of the AI's response. Adjust this value based on your needs.
* `safe_context`: The `pdf_context` is truncated to `[:48000]` characters in `backend/services/ai_service.py` to fit within the model's context window. This is an immediate solution to prevent `context_length_exceeded` errors.

---

## 🐛 Troubleshooting

Encountered an issue? Here are solutions to common problems:

### "Module not found" errors (Python backend):

* Ensure you are in the `backend/` directory.
* Run `pip install -r requirements.txt` to install all necessary Python dependencies.
* Verify your Python version meets the prerequisites (Python 3.11.9 recommended).
* **Git Bash Specific**: If using Git Bash on Windows and commands like `uvicorn` are not found, try `python -m uvicorn main:app --reload` instead. For better compatibility, it's recommended to use PowerShell or Command Prompt.

### "OpenAI client is not initialized" or API key issues:

* Double-check that your `OPENAI_API_KEY` is correctly set in the `.env` file in the `backend/` directory.
* Ensure `load_dotenv()` is called at the very top of `backend/main.py` before any other local imports that depend on environment variables.
* Verify your internet connection and that the OpenAI API is accessible.

### "Context length exceeded" error:

* This means the PDF content combined with the conversation history is too long for the AI model.
* The current solution truncates the PDF context to 48000 characters. If this error persists, you might need to further reduce this limit in `backend/services/ai_service.py` or consider using a model with a larger context window (e.g., `gpt-4-turbo`).

### Port Conflicts:

* The backend runs on `http://127.0.0.1:8000` and the frontend on `http://localhost:5173`. If these ports are already in use, you might see errors.
* For the backend, you can specify a different port when running uvicorn: `uvicorn main:app --host 0.0.0.0 --port 8001 --reload`. Remember to update the `baseURL` in `frontend/src/services/api.js` if you change the backend port.
* For the frontend, Vite will usually suggest a different port if 5173 is taken.

### PDF Parsing Errors:

* Ensure the `PDF_PATH` in your `.env` file points to a valid PDF file.
* If PyPDF2 struggles with a specific PDF, it might be due to its structure or if it's a scanned image. Try a different PDF to confirm.

### Duplicated AI Response Text in Development:

* This is a known behavior when `React.StrictMode` is enabled in development. It causes components to render twice to help detect side effects.
* This duplication will not occur in a production build (`npm run build`).

---

## 🏗️ Project Structure

The project is organized into two main directories:

```
intelligent-pdf-chatbot/
├── backend/
│   ├── main.py                 # Main FastAPI application
│   ├── services/
│   │   ├── ai_service.py       # AI interaction module
│   │   └── pdf_service.py      # PDF processing module
│   ├── assets/                 # Directory for PDF documents
│   └── requirements.txt        # Python dependencies
└── frontend/
    ├── src/
    │   ├── components/         # React components
    │   ├── services/           # API service integration
    │   └── App.jsx            # Main React app
    ├── public/                 # Static assets
    ├── index.html             # Main HTML file
    ├── package.json           # Node.js dependencies
    └── vite.config.js         # Vite configuration
```

---

## ⚠️ Limitations

* **PDF Size**: Currently, the entire PDF content is loaded into memory and truncated to fit the AI model's context window. This limits the size of PDFs that can be effectively processed. Large documents might lead to information loss or exceed API token limits.
* **PDF Types**: Performance may vary with complex PDF layouts, scanned documents (images of text), or PDFs with non-standard encodings, as text extraction might be imperfect.
* **AI Context Window**: The AI model has a fixed context window. While conversation history is maintained, very long conversations combined with large PDF contexts can still lead to truncation.
* **Single Conversation Session**: The frontend currently supports one active conversation session. Switching between multiple chat sessions is not implemented.

---

## 📚 Technical Specifications

### Core Requirements

#### 1. Frontend (React)
* **Single Page Chat Interface**: The application provides a single-page chat interface in `frontend/src/App.jsx` and `frontend/src/components/ChatInterface.jsx`.
* **Message Input Field**: Implemented in `frontend/src/components/MessageInput.jsx`.
* **Send Button**: Integrated within `frontend/src/components/MessageInput.jsx`.
* **Chat History Display**: Managed by `frontend/src/components/MessageList.jsx`, displaying messages with distinct styling for user and AI.
* **Clear/Reset Conversation Button**: A "Reset" button is available in `frontend/src/components/ChatInterface.jsx`.
* **Clean, Responsive Design**: Achieved using plain CSS with responsive styling.
* **Real-time Streaming of AI Responses**: Implemented using fetch and response.body.getReader().
* **Messages Clearly Distinguished**: Styling differentiates user and AI messages.

#### 2. Backend (FastAPI)
* **Single Endpoint for Chat Messages**: A `POST /chat` endpoint receives user messages and streams AI responses.
* **PDF Context Loading on Startup**: The PDF specified by `PDF_PATH` environment variable is loaded during app startup.
* **Integration with OpenAI API**: Uses the OpenAI Python SDK for chat completion API interaction.
* **Streaming Response Support**: Returns StreamingResponse objects with Server-Sent Events.
* **In-memory Conversation History**: Global dictionary stores chat messages for each conversation_id.
* **Health Check Endpoint**: A `GET /health` endpoint provides status checks.

#### 3. Context Handling
* **Load and Parse the Provided PDF**: Uses PyPDF2 to extract text from PDF files.
* **Include the PDF Content as Context**: PDF content is included in all AI API calls.
* **Accurate PDF-based Responses**: System prompt instructs AI to answer based on document content.

### API Structure

#### Request
```json
POST /chat
{
    "message": "What is the main topic of the document?",
    "conversation_id": "optional-session-id"
}
```

#### Response (SSE stream)
```
data: {"type": "content", "content": "The document discusses..."}
data: {"type": "done"}
```

### Required Dependencies

**Frontend**: React, Vite for development
**Backend**: FastAPI, PyPDF2 for PDF parsing, OpenAI Python SDK

---

## 🤝 Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue on the GitHub repository.

### Reporting Bugs

When reporting a bug, please include:

* A clear and concise description of the issue.
* Steps to reproduce the behavior.
* Expected behavior.
* Screenshots or error messages if applicable.
* Your operating system and environment details.

---

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.