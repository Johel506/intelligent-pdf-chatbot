# 🤖 Intelligent PDF Chatbot

An advanced, context-aware chat application designed to provide instant, verifiable answers from your PDF documents. Built with a modern, fully responsive interface and a powerful RAG backend.

![Python Version](https://img.shields.io/badge/Python-3.11.9-blue?style=flat-square&logo=python)
![Node.js Version](https://img.shields.io/badge/Node.js-22.16.0-green?style=flat-square&logo=node.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?style=flat-square&logo=fastapi)
![React](https://img.shields.io/badge/React-19.1.0-61DAFB?style=flat-square&logo=react)

![Final Project Showcase](https://github.com/user-attachments/assets/12b659df-65e7-4280-83a1-206babfab976)


---

## ✨ Features

* **Advanced Context with RAG**: Utilizes a Retrieval-Augmented Generation (RAG) pipeline to understand and answer questions based on the *entire* content of the PDF, overcoming context length limitations.
* **Verifiable Answers with Citations**: Provides inline source citations (e.g., `<sup>Page 13</sup>`) for every piece of information, allowing users to verify the AI's answers.
* **Full Conversation Management**: A complete multi-conversation interface allows users to create, automatically name, pin, rename, and delete chat sessions.
* **Modern & Responsive UI**: A clean, dark-mode interface built with React that is fully responsive, providing an excellent user experience on both desktop and mobile.
* **Multi-Language Support (EN/ES)**: A startup modal allows users to select their preferred language for the UI.
* **Real-time AI Streaming**: Experience dynamic, real-time AI responses as they are generated via Server-Sent Events.

---

## 🚀 Quick Start

### Prerequisites

* Python 3.11+
* Node.js 20+
* An OpenAI API Key

### Installation

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd intelligent-pdf-chatbot
    ```

2.  **Backend Setup:**
    ```bash
    cd backend
    # Create and activate a virtual environment (recommended)
    python -m venv venv
    .\venv\Scripts\Activate.ps1 
    or
    source venv/bin/activate  # On Windows: venv\Scripts\activate

    # Create .env file from the example
    cp .env.example .env 

    # Add your OpenAI API key to the .env file
    # OPENAI_API_KEY="your_openai_api_key_here"
    # PDF_PATH="./assets/PB_TravelAbility_DI-v3.pdf"

    # Install dependencies and run the server
    pip install -r requirements.txt
    python main.py
    ```
    The backend API will start on `http://127.0.0.1:8000`.

3.  **Frontend Setup (in a new terminal):**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```
    The frontend will start on `http://localhost:5173`.

---

## 💬 How to Use

Once both servers are running, open your web browser to `http://localhost:5173`.

1.  You will be prompted to select a language (English or Spanish).
2.  Use the **sidebar** on the left to manage your conversations. Click **"+ New Chat"** to start.
3.  The chat will be automatically named after you send your first message.
4.  Use the **three-dot menu** next to each chat to Pin, Rename, or Delete it.
5.  Ask questions in the input field. The AI will respond with citations from the document.
6.  Use the **"Export"** button to download the current conversation as a Markdown file.

---

## 🏗️ Project Structure

The project is organized into two main directories:

```
intelligent-pdf-chatbot/
├── backend/
│   ├── main.py                 # Main FastAPI application
│   ├── services/
│   │   ├── ai_service.py       # AI interaction & RAG logic
│   │   └── pdf_service.py      # PDF processing module
│   ├── assets/                 # Directory for PDF documents
│   └── requirements.txt        # Python dependencies
└── frontend/
    ├── src/
    │   ├── components/         # React components
    │   ├── context/            # React context for i18n
    │   ├── locales/            # JSON files for translations
    │   └── assets/             # SVG icons and other assets
    ├── public/                 # Static assets (e.g., favicon)
    └── ...                     # Config files (package.json, etc.)
```

---

## ⚠️ Limitations and Considerations

* **PDF Quality**: The effectiveness of the RAG pipeline depends on the quality of the source PDF. The document must contain selectable text (not scanned images) for the text extraction to work.
* **API Key Required**: The application's core functionality relies on a valid OpenAI API key for embeddings and chat completions. Some features were implemented without end-to-end testing due to key expiration.
* **Rate Limiting**: The backend includes a simple IP-based rate limiter (`5 requests per minute` on the `/chat` endpoint). This is a basic protection and could be enhanced for production environments.

---

## 🐛 Troubleshooting

* **"Module not found" errors (Python backend):**
    * Ensure you have activated your virtual environment (`source venv/bin/activate`).
    * Run `pip install -r requirements.txt` to install all necessary Python dependencies.

* **API key issues:**
    * Double-check that your `.env` file exists in the `backend/` directory and that `OPENAI_API_KEY` is correctly set.
    * Ensure `load_dotenv()` is called at the very top of `backend/main.py`.

* **PDF Parsing Errors:**
    * Ensure the `PDF_PATH` in your `.env` file points to a valid, text-based PDF file.
    * If PyPDF2 struggles, the PDF might be corrupted, an image, or have a non-standard encoding.

* **Duplicated AI Response Text in Development:**
    * This is a known behavior when `React.StrictMode` is enabled. It causes components to render twice to help detect side effects. This duplication will not occur in a production build (`npm run build`).
