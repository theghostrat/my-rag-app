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

Before running the application, ensure you have the following installed on your system:

*   Python 3.7+
*   Git

## Installation

Follow these steps to set up and run the application locally:

1.  **Clone the repository:**

    Open your terminal or command prompt and run:

    ```bash
    git clone https://github.com/theghostrat/my-rag-app.git
    cd my-rag-app
    ```

2.  **Create a virtual environment (recommended):**

    It's highly recommended to use a virtual environment to manage project dependencies.

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

    With the virtual environment activated, install the necessary libraries using pip:

    ```bash
    pip install -r requirements.txt
    ```

5.  **Set up environment variables:**

    You need to provide your OpenRouter API key. Create a file named `.env` in the root directory of the project (the same directory as `rag_single_file_app.py`). Add the following line to the `.env` file, replacing `"your_openrouter_api_key_here"` with your actual API key:

    ```env
    OPENROUTER_API_KEY="your_openrouter_api_key_here"
    ```

## Running the Application

1.  **Ensure your virtual environment is activated.**
2.  **Start the Flask application:**

    Run the main Python file:

    ```bash
    python rag_single_file_app.py
    ```

3.  The application will start a local development server. You can access it by opening your web browser and navigating to `http://127.0.0.1:5000/`.

## Usage

1.  **Landing Page:** The application starts at the landing page (`/`).
2.  **Login/Signup:** Navigate to `/login` or `/signup`.
    *   **Authentication Placeholder:** Note that the current authentication is a basic placeholder. For demonstration purposes, you can log in as `admin` with the password `adminpass` to access the admin panel and document upload features. Other usernames with any password will be treated as regular users with access only to the chat.
3.  **Admin Panel (`/admin`):** If logged in as `admin`, you can access the admin panel to upload PDF and DOCX documents. Uploaded documents are automatically processed for the RAG system.
4.  **Chat (`/chat`):** After logging in (as either `admin` or any other user), you can access the chat interface. Type your questions, and the language model will use the content of the uploaded documents to provide answers.

## Project Structure

```
.
├── rag_single_file_app.py  # The main Flask application file
├── requirements.txt        # Python dependencies listed for pip installation
├── .gitignore              # Specifies intentionally untracked files that Git should ignore
├── static/                 # Contains static assets like CSS and JavaScript files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
└── templates/              # Contains HTML files used as templates by Flask
    ├── admin.html
    ├── chat.html
    ├── landing.html
    ├── login.html
    └── signup.html
```

*(Note: The `chroma_db/` directory, which stores the vector database, and the `uploads/` directory, where uploaded files are saved, are ignored by Git as specified in `.gitignore`.)*

## Contributing

(Add contributing guidelines here if applicable)

## License

(Add license information here)