import os
import json
from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for, session
from dotenv import load_dotenv
import fitz  # PyMuPDF
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
from openai import OpenAI
from functools import wraps

# Load environment variables
load_dotenv()
OPENROUTER_API_KEY = "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"
if not OPENROUTER_API_KEY:
    print("Error: OPENROUTER_API_KEY not found in .env file.")
    # In a real app, you might want to exit or handle this more gracefully
    # For now, we'll just print an error and continue, but LLM calls will fail.

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'your_secret_key_here' # Change this to a random secret key
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- RAG Setup ---
# Initialize ChromaDB client
client = chromadb.PersistentClient(path="./chroma_db")
try:
    collection = client.create_collection(name="rag_documents")
except: # Handle case where collection already exists
    collection = client.get_collection(name="rag_documents")

# Initialize Embedding Model
# Using a smaller, faster model for demonstration
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize Text Splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
)

# Initialize OpenAI client for OpenRouter
# Using a placeholder model name, replace with your desired OpenRouter model
# e.g., "openai/gpt-4o-mini", "mistralai/mistral-large-latest"
llm_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)
LLM_MODEL = "openai/gpt-4o-mini" # Replace with your chosen OpenRouter model

# --- Document Processing Functions ---
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text += page.get_text()
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
    return text

def extract_text_from_docx(docx_path):
    text = ""
    try:
        doc = Document(docx_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        print(f"Error extracting text from DOCX {docx_path}: {e}")
    return text

def process_document_for_rag(filepath):
    filename = os.path.basename(filepath)
    text = ""
    if filepath.lower().endswith('.pdf'):
        text = extract_text_from_pdf(filepath)
    elif filepath.lower().endswith('.docx'):
        text = extract_text_from_docx(filepath)
    else:
        print(f"Unsupported file type: {filename}")
        return

    if text:
        chunks = text_splitter.split_text(text)
        embeddings = embedding_model.encode(chunks).tolist() # Convert numpy array to list
        ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"filename": filename, "chunk_index": i} for i in range(len(chunks))]

        # Add to ChromaDB
        try:
            collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Processed and added {len(chunks)} chunks from {filename} to ChromaDB.")
        except Exception as e:
            print(f"Error adding chunks to ChromaDB for {filename}: {e}")


# --- Authentication and Authorization ---
def login_required(role="user"):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('logged_in') or (role == "admin" and session.get('role') != "admin"):
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Placeholder authentication logic: 'admin' user is admin, others are regular users
        if username == 'admin' and password == 'adminpass': # Replace with actual authentication
            session['logged_in'] = True
            session['username'] = username
            session['role'] = 'admin'
            print(f"Admin user '{username}' logged in.")
            return redirect(url_for('admin'))
        elif username and password: # Placeholder for regular user login
             session['logged_in'] = True
             session['username'] = username
             session['role'] = 'user'
             print(f"Regular user '{username}' logged in.")
             return redirect(url_for('chat'))
        else:
            # Handle failed login (e.g., show error message on login page)
            print(f"Failed login attempt for username: {username}")
            return render_template('login.html', error="Invalid credentials") # You'll need to update login.html to display this

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Add your user creation logic here
        print(f"Received signup attempt for username: {username}")
        # For now, just redirect to login after signup attempt
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/chat')
@login_required() # Regular users and admin can access chat
def chat():
    return render_template('chat.html')

@app.route('/admin')
@login_required(role="admin") # Only admin can access admin panel
def admin():
    # Fetch the list of uploaded documents
    uploaded_files = []
    try:
        uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
    except Exception as e:
        print(f"Error listing uploaded files: {e}")
        # Continue even if listing fails, the template will just show an empty list

    return render_template('admin.html', uploaded_files=uploaded_files)

@app.route('/get_documents', methods=['GET'])
@login_required(role="admin") # Only admin can get the document list
def get_documents():
    try:
        uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
        return jsonify({'filenames': uploaded_files}), 200
    except Exception as e:
        print(f"Error listing uploaded files: {e}")
        return jsonify({'error': 'Failed to retrieve document list'}), 500

@app.route('/delete_document', methods=['POST'])
@login_required(role="admin") # Only admin can delete documents
def delete_document_route():
    data = request.json
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Basic security: Prevent directory traversal
    if not os.path.abspath(filepath).startswith(os.path.abspath(app.config['UPLOAD_FOLDER'])):
        return jsonify({'error': 'Invalid filename'}), 400

    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            # TODO: Also remove embeddings from ChromaDB for this document
            print(f"Deleted file: {filename}")
            return jsonify({'message': f'File {filename} deleted successfully'}), 200
        else:
            return jsonify({'error': f'File {filename} not found'}), 404
    except Exception as e:
        print(f"Error deleting file {filename}: {e}")
        return jsonify({'error': f'Failed to delete file {filename}'}), 500


@app.route('/upload', methods=['POST'])
@login_required(role="admin") # Only admin can upload documents
def upload_documents_route():
    if 'files' not in request.files:
        return jsonify({'error': 'No files part in the request'}), 400
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No selected file'}), 400

    uploaded_filenames = []
    for file in files:
        if file.filename == '':
            continue
        # Basic security: Sanitize filename and check extension
        filename = os.path.basename(file.filename) # Get filename without path
        if '.' in filename and filename.rsplit('.', 1)[1].lower() in ['pdf', 'docx']:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                file.save(filepath)
                uploaded_filenames.append(filename)
                # Process the uploaded file for RAG
                process_document_for_rag(filepath)
            except Exception as e:
                print(f"Error saving or processing file {filename}: {e}")
                # Optionally remove partially saved file
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({'error': f'Failed to process file {filename}'}), 500
        else:
            return jsonify({'error': f'Unsupported file type: {filename}'}), 400


    return jsonify({'message': 'Files uploaded and processed successfully', 'filenames': uploaded_filenames}), 200

@app.route('/get_models', methods=['GET'])
@login_required() # Both admin and regular users can get models
def get_models():
    try:
        # Fetch models from OpenRouter API
        # Note: This is a simplified example. You might need to handle pagination
        # and filter models based on capabilities (e.g., chat completion)
        models_response = llm_client.models.list()
        models = [model.id for model in models_response.data]
        return jsonify({'models': models}), 200
    except Exception as e:
        print(f"Error fetching models from OpenRouter: {e}")
        return jsonify({'error': 'Failed to fetch models'}), 500


@app.route('/chat', methods=['POST'])
@login_required() # Both admin and regular users can chat
def chat_route():
    data = request.json
    user_message = data.get('message')
    selected_model = data.get('model', LLM_MODEL) # Get selected model, default to LLM_MODEL
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # --- RAG Logic ---
    # 1. Perform similarity search in vector DB using user_message
    try:
        query_embedding = embedding_model.encode(user_message).tolist()
        # Query ChromaDB for similar documents
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3 # Get top 3 relevant chunks
        )
        retrieved_chunks = results['documents'][0] if results and results['documents'] else []
        retrieved_metadatas = results['metadatas'][0] if results and results['metadatas'] else []

        context = "\n".join(retrieved_chunks)
        citation = None
        if retrieved_metadatas:
             # Simple citation: list filenames from retrieved chunks
             cited_files = list(set([m['filename'] for m in retrieved_metadatas if 'filename' in m]))
             if cited_files:
                 citation = ", ".join(cited_files)

    except Exception as e:
        print(f"Error during RAG retrieval: {e}")
        context = "" # Proceed without RAG context if retrieval fails
        citation = None


    # 2. Prepare prompt for LLM
    # Instruct the LLM to use the context if relevant, otherwise use its own knowledge.
    # This is a simplified instruction; more sophisticated prompting might be needed.
    messages = [{"role": "system", "content": "You are a helpful assistant. Answer the user's question based on the provided context if possible. If the question cannot be answered from the context, use your own knowledge. Indicate if you are using the provided context."}]

    if context:
        messages.append({"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_message}\n\nAnswer:"})
    else:
         messages.append({"role": "user", "content": f"Question: {user_message}\n\nAnswer:"})


    # 3. Send prompt to LLM via OpenRouter
    bot_response = "Could not get response from LLM." # Default error message
    try:
        chat_completion = llm_client.chat.completions.create(
            model=selected_model, # Use the selected model
            messages=messages,
            temperature=0.7, # Adjust temperature as needed
        )
        bot_response = chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenRouter API: {e}")
        bot_response = f"Error communicating with the language model: {e}"
        citation = None # Clear citation if LLM call fails

    # 4. Process LLM response (already done above) and return

    return jsonify({'response': bot_response, 'citation': citation}), 200

@app.route('/logout')
@login_required()
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Consider using a production-ready server like Gunicorn or uWSGI for production
    # For development, debug=True is fine
    app.run(debug=True, port=5000) # Running on port 5000