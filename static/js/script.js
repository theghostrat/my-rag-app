async function uploadDocuments() {
    const fileInput = document.getElementById('documentUpload');
    const uploadStatus = document.getElementById('uploadStatus');
    const files = fileInput.files;
    if (files.length === 0) {
        uploadStatus.textContent = 'Please select files to upload.';
        return;
    }

    const formData = new FormData();
    for (const file of files) {
        formData.append('files', file);
    }

    uploadStatus.textContent = 'Uploading and processing documents...';

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        if (response.ok) {
            uploadStatus.textContent = `Successfully uploaded and processed: ${result.filenames.join(', ')}`;
            fileInput.value = ''; // Clear the file input
            fetchDocumentsAndDisplay(); // Refresh document list after upload
        } else {
            uploadStatus.textContent = `Upload failed: ${result.error}`;
        }
    } catch (error) {
        uploadStatus.textContent = `An error occurred during upload: ${error}`;
        console.error('Upload error:', error);
    }
}

async function sendMessage() {
    const userInput = document.getElementById('userInput');
    const modelSelect = document.getElementById('modelSelect');
    const message = userInput.value.trim();
    const selectedModel = modelSelect ? modelSelect.value : null; // Check if modelSelect exists

    if (message === '') {
        return;
    }

    appendMessage('user', message);
    userInput.value = '';
    userInput.disabled = true; // Disable input while waiting for response

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message, model: selectedModel }) // Include selected model
        });
        const result = await response.json();

        if (response.ok) {
            appendMessage('bot', result.response, result.citation);
        } else {
            appendMessage('bot', `Error: ${result.error}`);
        }
    } catch (error) {
        appendMessage('bot', `An error occurred: ${error}`);
        console.error('Chat error:', error);
    } finally {
        userInput.disabled = false; // Re-enable input
        userInput.focus(); // Focus input field
    }
}

function appendMessage(sender, message, citation = null) {
    const chatBox = document.getElementById('chatBox');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', `${sender}-message`);
    messageElement.textContent = message;

    if (citation) {
        const citationElement = document.createElement('div');
        citationElement.classList.add('citation');
        citationElement.textContent = `Source: ${citation}`;
        messageElement.appendChild(citationElement);
    }

    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to the latest message
}

async function fetchModelsAndPopulateDropdown() {
    const modelSelect = document.getElementById('modelSelect');
    if (!modelSelect) return; // Only run on chat page
    try {
        const response = await fetch('/get_models');
        const result = await response.json();
        if (response.ok && result.models) {
            modelSelect.innerHTML = ''; // Clear existing options
            result.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                modelSelect.appendChild(option);
            });
        } else {
            console.error('Failed to fetch models:', result.error);
            // Optionally add a default or error message option
        }
    } catch (error) {
        console.error('Error fetching models:', error);
        // Optionally add a default or error message option
    }
}

async function fetchDocumentsAndDisplay() {
    const documentList = document.getElementById('documentList');
    if (!documentList) return; // Only run on admin page

    try {
        const response = await fetch('/get_documents');
        const result = await response.json();
        if (response.ok && result.filenames) {
            documentList.innerHTML = ''; // Clear existing list items
            result.filenames.forEach(filename => {
                const listItem = document.createElement('li');
                listItem.innerHTML = `
                    <span>${filename}</span>
                    <button onclick="deleteDocument('${filename}')">Delete</button>
                `;
                documentList.appendChild(listItem);
            });
        } else {
            console.error('Failed to fetch documents:', result.error);
            const listItem = document.createElement('li');
            listItem.textContent = 'Failed to load documents.';
            documentList.appendChild(listItem);
        }
    } catch (error) {
        console.error('Error fetching documents:', error);
        const listItem = document.createElement('li');
        listItem.textContent = 'An error occurred while fetching documents.';
        documentList.appendChild(listItem);
    }
}

async function deleteDocument(filename) {
    if (confirm(`Are you sure you want to delete "${filename}"?`)) {
        try {
            const response = await fetch('/delete_document', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ filename: filename })
            });
            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                fetchDocumentsAndDisplay(); // Refresh the list after deletion
            } else {
                alert(`Failed to delete file: ${result.error}`);
            }
        } catch (error) {
            alert(`An error occurred during deletion: ${error}`);
            console.error('Delete error:', error);
        }
    }
}


// Fetch models or documents when the page loads
document.addEventListener('DOMContentLoaded', () => {
    fetchModelsAndPopulateDropdown(); // Attempt to fetch models (for chat page)
    fetchDocumentsAndDisplay(); // Attempt to fetch documents (for admin page)
});