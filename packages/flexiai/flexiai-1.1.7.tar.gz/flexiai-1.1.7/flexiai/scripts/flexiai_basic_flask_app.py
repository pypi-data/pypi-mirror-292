# flexiai/scripts/flexiai_basic_flask_app.py
import os
from pathlib import Path

def _detect_project_root():
    """
    Detects the project root directory based on the current working directory.

    Returns:
        str: The detected project root directory path.
    """
    current_dir = Path.cwd()
    project_root = current_dir
    return str(project_root)

def create_folder_structure(project_root):
    """
    Creates the folder structure for the Flask application.

    Args:
        project_root (str): The root directory of the project.
    """
    folder_structure = {
        'logs': [],
        'routes': ['api.py'],
        'static/css': ['styles.css'],
        'static/images': [],
        'static/js': ['scripts.js'],
        'templates': ['index.html'],
        'utils': ['markdown_converter.py']
    }

    for folder, files in folder_structure.items():
        folder_path = os.path.join(project_root, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Created directory: {folder_path}")

        for file in files:
            file_path = os.path.join(folder_path, file)
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    f.write('')  # Creates an empty file
                print(f"Created file: {file_path}")

def write_file_content(project_root):
    """
    Writes predefined content to specific files in the folder structure.

    Args:
        project_root (str): The root directory of the project.
    """
    files_content = {
        'routes/api.py': '''import uuid
from flexiai import FlexiAI
from flask import Blueprint, request, jsonify, session as flask_session
from utils.markdown_converter import convert_markdown_to_html

# Create a Blueprint for the API routes
api_bp = Blueprint('api', __name__)
flexiai = FlexiAI()

def message_to_dict(message):
    """
    Convert a message object to a dictionary, including nested TextContentBlock objects.
    
    Args:
        message (object): The message object to convert.
    
    Returns:
        dict: The converted message dictionary.
    """
    message_dict = {
        'id': message.id,
        'role': message.role,
        'content': [block.text.value for block in message.content if hasattr(block, 'text') and hasattr(block.text, 'value')]
    }
    return message_dict

@api_bp.route('/run', methods=['POST'])
def run():
    """
    Route to handle running the assistant with the user's message.
    
    Retrieves the user's message from the request, manages session and thread IDs,
    sends the message to the assistant, retrieves the responses, converts them to HTML,
    and returns the responses as JSON.
    
    Returns:
        Response: JSON response containing success status, thread ID, and messages.
    """
    data = request.json
    user_message = data['message']
    assistant_id = 'asst_XXXXXXXXXXXXXXXXXXXXXXXXXX'  # Update with your assistant ID
    thread_id = data.get('thread_id')

    session_id = flask_session.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        flask_session['session_id'] = session_id
        flexiai.session_manager.create_session(session_id, {"thread_id": thread_id, "seen_message_ids": []})
    else:
        session_data = flexiai.session_manager.get_session(session_id)
        thread_id = session_data.get("thread_id", thread_id)

    if not thread_id:
        thread_id = flexiai.multi_agent_system.thread_initialization(assistant_id)
        flexiai.session_manager.create_session(session_id, {"thread_id": thread_id, "seen_message_ids": []})

    last_retrieved_id = None
    flexiai.create_advanced_run(assistant_id, thread_id, user_message)
    messages = flexiai.retrieve_messages_dynamically(thread_id, limit=20, retrieve_all=False, last_retrieved_id=last_retrieved_id)

    session_data = flexiai.session_manager.get_session(session_id)
    seen_message_ids = set(session_data.get("seen_message_ids", []))

    filtered_messages = []
    new_seen_message_ids = list(seen_message_ids)

    for msg in messages:
        if msg.id not in seen_message_ids:
            content = " ".join([block.text.value for block in msg.content if hasattr(block, 'text') and hasattr(block.text, 'value')])
            html_content = convert_markdown_to_html(content)
            filtered_messages.append({
                "role": "You" if msg.role == "user" else "Assistant",
                "message": html_content
            })
            new_seen_message_ids.append(msg.id)

    flexiai.session_manager.create_session(session_id, {"thread_id": thread_id, "seen_message_ids": new_seen_message_ids})

    response_data = {
        'success': True,
        'thread_id': thread_id,
        'messages': filtered_messages
    }

    flexiai.logger.debug(f"Sending response data: {response_data}")
    return jsonify(response_data)
''',

        'static/css/styles.css': '''/* Base Styles */
body {
    font-family: 'Open Sans', sans-serif;
    margin: 0;
    padding: 0;
    background-color: #535353;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    height: 100vh;
}

/* Chat Container */
#chat-container {
    width: 100%;
    max-width: 680px;
    height: calc(100vh - 2rem);
    display: flex;
    flex-direction: column;
    background-color: #ffffff;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    border-radius: 8px;
    margin: 1rem 0;
    overflow: hidden;
}

/* Links */
a {
    color: #89e600;
}

/* Messages Container */
#messages {
    padding: 1rem;
    flex: 1;
    overflow-y: auto;
    margin: 0;
    color: #e1e1e6;
}

/* Message Item */
.message {
    padding: 0.5rem 0;
    margin: 0.5rem 0;
    border-radius: 4px;
    word-wrap: break-word;
    display: flex;
    align-items: flex-start;
    animation: fadeIn 0.5s ease-in-out;
}

/* Animation for messages */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Message Container */
.message-container {
    display: flex;
    align-items: flex-start;
    width: 100%;
}

/* Avatar */
.avatar {
    width: 45px;
    height: 45px;
    border-radius: 50%;
    background-color: #25272a;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-right: 10px;
    font-size: 1.2em;
    color: #ffffff;
    border: 1px solid #c6c6c6;
    overflow: hidden;
}

/* Avatar Images */
.avatar img {
    width: 100%;
    height: 100%;
    border-radius: 50%;
}

/* Message Content */
.message-content {
    flex: 1;
    padding: 0.5rem 0.9rem;
    border-radius: 20px;
    font-size: 0.7em;
    line-height: 1.5rem;
    background-color: #3a3f4b;
    color: #e1e1e6;
    position: relative;
    word-break: break-word;
    overflow: hidden;
}

/* User Message */
.user .message-content {
    background-color: #3a3a3a;
    text-align: left;
    color: #e1e1e6;
}

/* Assistant Message */
.assistant .message-content {
    background-color: #404a63;
    text-align: left;
}

/* Error Message */
.error .message-content {
    background-color: #ff4c4c;
    text-align: center;
    color: #fff;
}

/* Input Container */
#input-container {
    display: flex;
    align-items: center;
    padding: 0.75rem 1rem;
    border-top: 1px solid #353940;
    background-color: #ffffff;
    position: relative;
}

/* Message Input */
#message-input {
    width: 91%;
    height: 40px;
    max-height: calc(1.5rem * 10);
    padding: 0.75rem;
    border: 1px solid #484e5c;
    border-radius: 20px;
    margin-right: 0.5rem;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
    transition: border-color 0.3s;
    background-color: #3a3a3a;
    color: #e1e1e6;
    resize: none;
    overflow-y: hidden;
    box-sizing: border-box;
    font-family: 'Open Sans', sans-serif;
    font-size: 1rem;
    line-height: 1.5rem;
}

#message-input:focus {
    border-color: #5a5a5a;
    outline: none;
}

/* Send Button */
#send-button {
    width: 44px;
    height: 44px;
    border: none;
    border-radius: 50%;
    background-color: #404a63;
    cursor: pointer;
    transition: background-color 0.3s, transform 0.1s;
    position: absolute;
    right: 1rem;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
}
#send-button::before {
    content: '';
    display: block;
    width: 0;
    height: 0;
    border-left: 8px solid transparent;
    border-right: 8px solid transparent;
    border-bottom: 12px solid white;
    transition: transform 0.3s;
}
#send-button:hover::before {
    animation: bounce 0.3s infinite alternate;
}
#send-button:hover {
    background-color: #2a3552;
}
#send-button:active {
    transform: scale(0.95);
}

@keyframes bounce {
    from {
        transform: translateY(0);
    }
    to {
        transform: translateY(-3px);
    }
}

/* Markdown Content */
.markdown-content {
    font-size: 1rem;
    line-height: 1.5rem;
    margin: 0;
    word-break: break-word;
}

.markdown-content h1, .markdown-content h2, .markdown-content h3 {
    border-bottom: 1px solid #444;
    padding-bottom: 0.3em;
    margin-top: 0.5em;
    font-size: 1.2em;
    color: #ffffff;
}

.markdown-content p {
    margin: 0.5em 0;
}

.markdown-content code {
    background-color: #2e2e2e;
    border-radius: 3px;
    padding: 0.2em 0.4em;
    color: #e1e1e6;
}

.markdown-content pre {
    background-color: #2e2e2e;
    padding: 6px;
    border-radius: 3px;
    overflow-x: auto;
    font-size: 0.95em;
    color: #e1e1e6;
    position: relative;
}

.markdown-content ol, .markdown-content ul {
    margin-left: 1em;
    padding-left: 0.5em;
    list-style-position: outside !important;
}

.markdown-content ol {
    list-style-type: decimal !important;
}

.markdown-content ul {
    list-style-type: disc !important;
}

.markdown-content li {
    list-style: inherit !important;
    margin: 0.5em 0;
}

.markdown-content blockquote {
    border-left: 4px solid #ccc;
    padding-left: 1em;
    margin-left: 0;
    color: #666;
}

.markdown-content a {
    color: #89e600;
    text-decoration: none;
}

.markdown-content a:hover {
    text-decoration: underline;
}

/* Headers in Messages */
.message-content h3 {
    margin: 0;
    padding: 0.5rem 0;
    font-size: 1rem;
    font-weight: bold;
    color: #ffffff;
}

/* Markdown Headers */
.markdown-content h1,
.markdown-content h2,
.markdown-content h3 {
    border-bottom: 1px solid #444;
    padding-bottom: 0.3em;
    margin-top: 0.5em;
    margin-bottom: 0.5em;
    font-size: 1.2em;
    color: #ffffff;
}

/* Responsive Design */
@media (max-width: 600px) {
    #chat-container {
        height: calc(100vh - 2rem);
    }
    #message-input {
        padding: 0.75rem;
    }
    #send-button {
        padding: 0.75rem;
        width: 40px;
        height: 40px;
    }
    .avatar {
        width: 30px;
        height: 30px;
        font-size: 1em;
    }
    .message-content {
        font-size: 0.7em;
        padding: 0.5rem 0.9rem;
    }
    .markdown-content {
        font-size: 0.85em;
    }
}

.copy-code-button {
    background-color: #373737;
    color: white;
    border: none;
    padding: 5px 10px;
    cursor: pointer;
    position: absolute;
    top: 5px;
    right: 5px;
    border-radius: 2px;
}

.copy-code-button:hover {
    background-color: #333131;
}

pre.sourceCode {
    position: relative;
}''',

        'static/js/scripts.js': '''// static/js/scripts.js
let threadId = null;
let isProcessing = false;

document.getElementById('send-button').addEventListener('click', sendMessage);

const messageInput = document.getElementById('message-input');
messageInput.addEventListener('keydown', function(event) {
    if (event.key === 'Enter' && event.shiftKey) {
        const cursorPosition = this.selectionStart;
        const value = this.value;
        this.value = value.substring(0, cursorPosition) + "\\n" + value.substring(cursorPosition);
        this.selectionStart = cursorPosition + 1;
        this.selectionEnd = cursorPosition + 1;
        event.preventDefault();
    } else if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
    autoResizeTextarea();
});

messageInput.addEventListener('input', autoResizeTextarea);

function autoResizeTextarea() {
    const maxRows = 10;
    const lineHeight = parseInt(window.getComputedStyle(messageInput).lineHeight);
    messageInput.style.height = '40px'; // Reset height to calculate new height
    const currentHeight = messageInput.scrollHeight;

    if (currentHeight > lineHeight * maxRows) {
        messageInput.style.height = (lineHeight * maxRows) + 'px';
        messageInput.style.overflowY = 'scroll';
    } else {
        messageInput.style.height = currentHeight + 'px';
        messageInput.style.overflowY = 'hidden';
    }
}

autoResizeTextarea();

function sendMessage() {
    const message = messageInput.value.trim();

    if (message === '') {
        alert('Message cannot be empty or whitespace.');
        return;
    }

    if (isProcessing) {
        alert('Please wait for the assistant to respond before sending a new message.');
        return;
    }

    addMessage('You', message, 'user', true);

    messageInput.value = '';
    autoResizeTextarea();

    isProcessing = true;

    fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message, thread_id: threadId })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            threadId = data.thread_id;
            updateChat(data.messages).then(() => {
                isProcessing = false;
                addCopyButtons();
            });
        } else {
            addMessage('Error', 'Failed to get response from assistant.', 'error');
            isProcessing = false;
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
        addMessage('Error', 'An error occurred: ' + error.message, 'error');
        isProcessing = false;
    });
}

function addMessage(role, text, className, isUserMessage = false) {
    const messageElement = document.createElement('div');
    messageElement.className = `message ${className}`;

    const avatar = role === 'You' ? '/static/images/user.png' : '/static/images/assistant.png';

    const formattedText = isUserMessage ? text.replace(/\\n/g, '<br>') : text;

    try {
        const htmlContent = window.marked.parse(formattedText);
        messageElement.innerHTML = `
            <div class="message-container">
                <div class="avatar"><img src="${avatar}" alt="${role}"></div>
                <div class="message-content">
                    <div class="markdown-content">${htmlContent}</div>
                </div>
            </div>`;
    } catch (error) {
        console.error('Markdown conversion error:', error);
        messageElement.innerHTML = `
            <div class="message-container">
                <div class="avatar"><img src="${avatar}" alt="${role}"></div>
                <div class="message-content">
                    <div class="markdown-content">${formattedText}</div>
                </div>
            </div>`;
    }

    const messagesContainer = document.getElementById('messages');
    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function updateChat(messages) {
    return new Promise((resolve) => {
        messages.forEach(msg => {
            if (msg.role === 'Assistant') {
                addMessage('Assistant', msg.message, 'assistant');
            }
        });
        resolve();
    });
}

function addCopyButtons() {
    document.querySelectorAll('pre code').forEach((block) => {
        if (block.parentNode.querySelector('.copy-code-button')) {
            return;
        }
        const copyButton = document.createElement('button');
        copyButton.innerText = 'Copy';
        copyButton.className = 'copy-code-button';
        copyButton.addEventListener('click', () => {
            navigator.clipboard.writeText(block.innerText).then(() => {
                copyButton.innerText = 'Copied!';
                setTimeout(() => {
                    copyButton.innerText = 'Copy';
                }, 2000);
            });
        });
        const pre = block.parentNode;
        pre.style.position = 'relative';
        pre.insertBefore(copyButton, block);
    });
}
''',

        'templates/index.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FlexiAI Chat Application</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
    <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}" type="image/x-icon">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
    <div id="chat-container">
        <div id="messages"></div>
        <div id="input-container">
            <textarea id="message-input" placeholder="Type your message here..."></textarea>
            <button id="send-button"></button>
        </div>
    </div>
    <script src="{{ url_for('static', filename='js/scripts.js') }}"></script>
</body>
</html>
''',

        'utils/markdown_converter.py': '''# utils/markdown_converter.py
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def preprocess_markdown(markdown_text):
    """
    Preprocess markdown text to ensure LaTeX formulas are correctly formatted for Pandoc.

    Args:
        markdown_text (str): The markdown text to preprocess.

    Returns:
        str: The preprocessed markdown text.
    """
    preprocessed_text = markdown_text.replace("\\[", "$$").replace("\\]", "$$")
    return preprocessed_text

def convert_markdown_to_html(markdown_text):
    """
    Convert markdown text to HTML using the Pandoc tool and ensure the output is properly handled.

    Args:
        markdown_text (str): The markdown text to convert.

    Returns:
        str: The converted HTML text. If conversion fails, returns the original markdown text.
    """
    try:
        preprocessed_text = preprocess_markdown(markdown_text)

        process = subprocess.Popen(['pandoc', '-f', 'markdown', '-t', 'html', '--mathjax'],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(input=preprocessed_text.encode('utf-8'))

        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, stderr.decode('utf-8'))

        html_output = stdout.decode('utf-8')

        return html_output
    except subprocess.CalledProcessError as e:
        logger.error(f"Pandoc conversion failed: {e}")
        return markdown_text
    except Exception as e:
        logger.error(f"Error converting markdown to HTML: {e}")
        return markdown_text
''',

        'app.py': '''import os
import logging
from flask import Flask, session, render_template
from datetime import timedelta
from routes.api import api_bp
from flexiai import FlexiAI
from flexiai.config.logging_config import setup_logging

# Initialize application-specific logging
setup_logging(
    root_level=logging.INFO,
    file_level=logging.INFO,
    console_level=logging.INFO,
    enable_file_logging=True,
    enable_console_logging=True
)

app = Flask(__name__, static_folder='static', template_folder='templates')

app.secret_key = os.urandom(24)

app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

app.register_blueprint(api_bp, url_prefix='/api')

flexiai = FlexiAI()

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    loggers = ['werkzeug', 'httpx', 'flexiai', 'user_function_mapping']
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        logger.propagate = False
        if logger.hasHandlers():
            logger.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    root_logger.addHandler(console_handler)

    app.run(host='127.0.0.1', port=5000, debug=False)
'''
    }

    for relative_path, content in files_content.items():
        file_path = os.path.join(project_root, relative_path)
        with open(file_path, 'w') as file:
            file.write(content)
            print(f"Written content to: {file_path}")

def setup_project():
    """
    Sets up the project by detecting the project root and creating the necessary folder structure and files.
    """
    project_root = _detect_project_root()
    create_folder_structure(project_root)
    write_file_content(project_root)

if __name__ == '__main__':
    try:
        setup_project()
    except Exception as e:
        print(f"Post-installation step failed: {e}")

