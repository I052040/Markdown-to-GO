# Required packages: flask, requests
import os
import requests
from pathlib import Path
from flask import Flask, render_template_string, request

app = Flask(__name__)

# Static files directory structure and corresponding URLs
static_dirs = {
    "js": ["marked.min.js", "highlight.min.js", "polyfill.min.js"],
    "css": ["highlight.default.min.css"],
    "mathjax/es5": ["tex-mml-chtml.js"]
}

file_urls = {
    "marked.min.js": "https://cdnjs.cloudflare.com/ajax/libs/marked/4.0.2/marked.min.js",
    "highlight.min.js": "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.5.0/highlight.min.js",
    "polyfill.min.js": "https://polyfill.io/v3/polyfill.min.js?features=es6",
    "highlight.default.min.css": "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.5.0/styles/default.min.css",
    "tex-mml-chtml.js": "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"
}

def ensure_static_files():
    """Ensure all static files exist locally; download missing files."""
    for dir_name, files in static_dirs.items():
        dir_path = Path("static") / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)

        for filename in files:
            file_path = dir_path / filename
            if not file_path.exists():
                print(f"Downloading {filename}...")
                try:
                    response = requests.get(file_urls[filename])
                    response.raise_for_status()
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                except Exception as e:
                    print(f"Failed to download {filename}: {e}")

# Check and prepare static files before running the app
ensure_static_files()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Markdown Editor</title>
    <!-- Load required JS and CSS for markdown and LaTeX rendering -->
    <script src="/static/js/marked.min.js"></script>
    <script src="/static/js/polyfill.min.js"></script>
    <script id="MathJax-script" async src="/static/mathjax/es5/tex-mml-chtml.js"></script>
    <link rel="stylesheet" href="/static/css/highlight.default.min.css">
    <script src="/static/js/highlight.min.js"></script>
    <!-- FontAwesome for any icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        /* Basic layout and styling */
        .container { display: flex; gap: 20px; padding: 20px; }
        #editor, #preview-container { flex: 1; height: 80vh; }
        textarea, #preview {
            height: 100%;
            width: 100%;
            padding: 15px;
            font-family: monospace;
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow: auto;
            resize: both;
            box-sizing: border-box;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        h1 { margin: 0; }
        .tool-bar-container { position: relative; padding-top: 60px; }
        .tool-bar { display: flex; gap: 10px; justify-content: flex-start; margin-bottom: 10px; }
        .title-container { position: absolute; top: 0; width: 100%; text-align: center; }
        button { padding: 5px 10px; }
    </style>
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        let currentFileName = ""; // Variable to store current file name if drag-and-drop

        document.getElementById('editor-textarea').addEventListener('drop', handleFileSelect);
        document.getElementById('editor-textarea').addEventListener('paste', function() {
            currentFileName = ""; // Reset file name on paste
        });

        function handleFileSelect(event) {
            event.preventDefault();
            const files = event.dataTransfer.files;
            if (files.length) {
                const file = files[0];
                currentFileName = file.name; // Store file name
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('editor-textarea').value = e.target.result;
                    updatePreview();
                };
                reader.readAsText(file);
            }
        }

        function handleDragOver(event) {
            event.preventDefault();
        }

        function updatePreview() {
            const markdownText = document.getElementById('editor-textarea').value;
            const preview = document.getElementById('preview');
            preview.innerHTML = marked.parse(markdownText);
            document.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightBlock(block);
            });
            MathJax.typesetPromise([preview]);
        }

        document.getElementById('clear-button').addEventListener('click', function() {
            document.getElementById('editor-textarea').value = '';
            updatePreview();
        });

        document.getElementById('save-button').addEventListener('click', function() {
            const markdownContent = document.getElementById('editor-textarea').value;
            let fileName = currentFileName || 'output.md'; // Use current file name or default to 'output.md'
            const blob = new Blob([markdownContent], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = fileName;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
    });
    </script>
</head>
<body>
    <div class="tool-bar-container">
        <div class="title-container">
            <h1>Markdown Editor</h1>
        </div>
        <div class="tool-bar">
            <input type="file" id="file-input" style="display: none;" onchange="handleFileSelect(event)">
            <button onclick="document.getElementById('file-input').click()">Open File</button>
            <button id="clear-button">Clear All</button>
            <button id="save-button">Save As</button>
        </div>
    </div>
    <div class="container">
        <div id="editor">
            <textarea id="editor-textarea" oninput="updatePreview()" ondrop="handleFileSelect(event)" ondragover="handleDragOver(event)" placeholder="Input Markdown/LaTeX...">{{ content }}</textarea>
        </div>
        <div id="preview-container">
            <div id="preview"></div>
        </div>
    </div>
</body>
</html>
"""

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'

@app.route('/shutdown', methods=['POST'])
def shutdown():
    return shutdown_server()

@app.route('/', methods=['GET', 'POST'])
def index():
    default_content = r"""# Welcome!
## Markdown Example
- **Bold Text**
- *Italic Text*
- [Link Example](https://example.com)

## LaTeX Example
Inline formula \\( E = mc^2 \\)

Block formula:
$$ \\int_0^\\infty x^2 dx $$

Matrix:
$$
\begin{bmatrix}
a & b \\\\
c & d \\\\
e & f
\end{bmatrix}
$$

More complex matrix (3x2 example):
$$
\begin{bmatrix}
1 & 2 \\\\
3 & 4 \\\\
5 & 6
\end{bmatrix}
$$

## Code Example
```python
def hello_world():
    print("Hello, World!")
```
"""
    return render_template_string(HTML_TEMPLATE, content=default_content)

if __name__ == '__main__':
    app.run(debug=False)
