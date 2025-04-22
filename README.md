# RAG Single File App

This is a simple Flask web application that demonstrates a basic Retrieval-Augmented Generation (RAG) system. It allows users to upload PDF and DOCX documents, process them into chunks and embeddings, and then chat with a language model that uses the uploaded documents as context.

## Features

*   Upload PDF and DOCX files.
*   Process documents into text chunks and embeddings.
*   Store embeddings and document chunks in a ChromaDB vector store.
*   Chat interface where the language model uses relevant document chunks to answer questions.
*   Basic user authentication (placeholder).
*   Admin panel for uploading and managing documents.

## Prerequisites

Before running the application, ensure you have the following installed:

*   Python 3.7+
*   Git

## Installation

1.  **Clone the repository:**

    ```bash
    git clone <your-github-repo-url>
    cd <your-repo-name>
    ```
    *(Note: You will replace `<your-github-repo-url>` and `<your-repo-name>` after the repository is created on GitHub.)*

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**

    *   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```

4.  **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5.  **Set up environment variables:**

    Create a `.env` file in the root directory of the project and add your OpenRouter API key:

    ```env
    OPENROUTER_API_KEY="your_openrouter_api_key_here"
    ```
    Replace `"your_openrouter_api_key_here"` with your actual API key from OpenRouter.

## Running the Application

1.  **Ensure your virtual environment is activated.**
2.  **Run the Flask application:**

    ```bash
    python rag_single_file_app.py
    ```

3.  The application will run on `http://127.0.0.1:5000/`. Open this URL in your web browser.

## Usage

1.  **Login/Signup:** Access the login page (`/login`) or signup page (`/signup`). The current authentication is a placeholder; you can log in as `admin` with password `adminpass` to access the admin panel.
2.  **Admin Panel (`/admin`):** If logged in as admin, you can upload PDF and DOCX documents. Uploaded documents will be processed and added to the RAG system.
3.  **Chat (`/chat`):** After logging in (as admin or a regular user), you can access the chat page. Type your questions, and the language model will attempt to answer them using the context from the uploaded documents.

## Project Structure

```
.
├── rag_single_file_app.py  # The main Flask application file
├── requirements.txt        # Python dependencies
├── .gitignore              # Files and directories to ignore in Git
├── static/                 # Static files (CSS, JS)
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
└── templates/              # HTML templates
    ├── admin.html
    ├── chat.html
    ├── landing.html
    ├── login.html
    └── signup.html
```

*(Note: The `chroma_db/` and `uploads/` directories are ignored by Git as they contain generated data and uploaded files.)*

## Contributing

(Add contributing guidelines here if applicable)

## License

(Add license information here)