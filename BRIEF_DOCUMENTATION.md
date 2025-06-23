# Brief Documentation: Intelligent PDF Chatbot

This document provides an overview of the design decisions, technical challenges encountered, and key features implemented for the Intelligent PDF Chatbot application.

## 1. Design Decisions

### Overall Architecture

The application follows a **client-server architecture**, with a React frontend and a FastAPI backend. This separation of concerns allows for independent development, scalability, and clear API boundaries.

#### Backend (FastAPI) & RAG Pipeline
- **Technology Choice**: Selected for its high performance, ease of use, and native asynchronous capabilities, crucial for handling streaming responses and the RAG pipeline.
- **Context Handling**: The core of the application is its **Retrieval-Augmented Generation (RAG)** pipeline. On startup, the PDF is chunked, converted into vector embeddings, and stored in an in-memory FAISS vector database. This allows the chatbot to perform semantic searches over the entire document, overcoming the context limitations of LLMs.
- **Communication**: Server-Sent Events (SSE) are used for streaming AI responses, providing a real-time, interactive user experience.

#### Frontend (React) & State Management
- **Technology Choice**: Chosen for its component-based structure and efficient UI updates.
- **Advanced State Management**: As features grew, the state management strategy evolved from simple local `useState` hooks to a centralized approach:
    - **Lifting State Up**: All application-critical state (like the list of conversations, the active chat ID, and the input value) is managed in the top-level `App.jsx` component. This provides a single source of truth and allows state to be shared cleanly between sibling components (e.g., `ConversationSidebar` and `ChatInterface`).
    - **React Context**: For cross-cutting concerns like internationalization (i18n), a dedicated `LanguageContext` was implemented. This allows any component in the tree to access the current language and translation functions without "prop drilling".

## 2. Key Implemented Features (Exceeding Core Requirements)

The final application includes not only the core requirements but also several advanced "bonus" features:

-   **Retrieval-Augmented Generation (RAG)**: The initial context truncation limitation was fully resolved by implementing a RAG pipeline, enabling queries over the entire document.
-   **Advanced Conversation Management**: A full-featured sidebar allows users to create, automatically name, pin, rename, and delete chat sessions.
-   **Verifiable Citations**: The AI provides inline citations (`<sup>Page X</sup>`) for its answers, a feature powered by meticulous prompt engineering and metadata handling in the RAG pipeline.
-   **Full Responsiveness and Modern UI**: The UI was completely overhauled with a modern dark theme and is fully responsive, offering a seamless experience on both desktop and mobile.
-   **Internationalization (i18n)**: The UI supports both English and Spanish, with language selection handled by a startup modal.
-   **API Rate Limiting**: The backend `/chat` endpoint is protected with basic rate limiting (`slowapi`) to prevent abuse.

## 3. Challenges Faced and Solutions

### Initial Setup and Dependencies
- **Dependency Conflicts & Environment Issues**: Solved by standardizing on Python 3.11.9, pinning key dependencies like `httpx`, and using `python -m uvicorn` for reliable script execution across different terminals.
- **Environment Variable Loading Order**: Resolved by ensuring `load_dotenv()` is called at the absolute start of `main.py` before any other local module imports.

### From Basic Chat to Advanced RAG
- **OpenAI API Context Length Limit**: The most significant technical challenge. The initial solution of truncating the PDF context was replaced with the full RAG architecture described in the design decisions.
- **Ensuring Factual Accuracy and Citation**: Initial RAG responses were inconsistent. This was solved through **High-Fidelity Prompt Engineering**:
    - Context chunks were formatted with XML-like tags (`<source page="X">`) to provide clear references for the LLM.
    - A strict system prompt was developed with explicit rules for inline citation, a prohibition on using external knowledge, and a "few-shot" example to guide the model's output format.

### Frontend Architecture and User Experience
- **State Management Complexity**: As multi-conversation features were added, managing state locally became unfeasible. This was solved by refactoring the application to "lift state up" to the `App.jsx` component.
- **Responsive Design Bugs**: The initial two-column layout broke on mobile. This was fixed by implementing a professional responsive pattern with CSS media queries, hiding the sidebar behind a "hamburger" menu and using an overlay to handle its dismissal.
- **Minor UX/CSS Bugs**: Several small but impactful bugs (e.g., invisible close buttons, unreadable selected text in inputs, flawed "new chat" logic) were identified and fixed through iterative debugging and refinement of CSS and component logic.