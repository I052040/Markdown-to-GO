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
    <script src="/static/js/marked.min.js"></script>
    <script src="/static/js/polyfill.min.js"></script>
    <script id="MathJax-script" async src="/static/mathjax/es5/tex-mml-chtml.js"></script>
    <link rel="stylesheet" href="/static/css/highlight.default.min.css">
    <script src="/static/js/highlight.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">

    <style>
        .container { display: flex; gap: 20px; padding: 20px; }
        #editor, #preview { width: 45%; height: 80vh; position: relative; }
        textarea, #preview {
            width: 100%; height: 100%;
            padding: 15px; font-family: monospace;
            border: 1px solid #ddd; border-radius: 5px;
        }
        h1 { text-align: center; margin: 20px 0; }
        .tool-bar { display: flex; gap: 10px; justify-content: flex-start; margin-bottom: 10px; }
        button { padding: 5px 10px; }
        #editor { position: relative; }
        .tool-bar-container { position: absolute; top: -50px; left: 0; }
    </style>
</head>
<body>
    <h1>Markdown Editor</h1>
    <div class="container">
        <div id="editor">
            <div class="tool-bar-container">
                <div class="tool-bar">
                    <button onclick="selectAllText('editor-textarea')">Select All</button>
                    <button onclick="copyAllText()">Copy All</button>
                </div>
            </div>
            <textarea id="editor-textarea" oninput="updatePreview()" placeholder="Input Markdown/LaTeX...">{{ content }}</textarea>
        </div>
        <div id="preview"></div>
    </div>

    <script>
        function updatedOnLoad() {
            updatePreview();
        }
        
        marked.setOptions({
            breaks: true,
            highlight: function(code, lang) {
                return hljs.highlightAuto(code).value;
            }
        });

        function updatePreview() {
            const content = document.getElementById('editor-textarea').value;
            const parsed = marked.parse(content);
            document.getElementById('preview').innerHTML = parsed;

            hljs.highlightAll();

            if (typeof MathJax !== 'undefined') {
                MathJax.typesetClear();
                MathJax.typesetPromise();
            }
        }

        function selectAllText(elementId) {
            const element = document.getElementById(elementId);
            element.select();
        }

        function copyAllText() {
            const element = document.getElementById('editor-textarea');
            element.select();
            try {
                const successful = document.execCommand('copy');
                alert(successful ? 'All text copied!' : 'Copy failed');
            } catch (err) {
                alert('Browser does not support copying');
            }
        }

        window.onload = updatedOnLoad;
    </script>
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
## Maxwell's Equations
1. Gauss's Law:
$$
\\nabla \\cdot \\mathbf{E} = \\frac{\\rho}{\\varepsilon_0}
$$
2. Gauss's Law for Magnetism:
$$
\\nabla \\cdot \\mathbf{B} = 0
$$
3. Faraday's Law of Induction:
$$
\\nabla \\times \\mathbf{E} = -\\frac{\\partial \\mathbf{B}}{\\partial t}
$$
4. Ampère-Maxwell Law:
$$
\\nabla \\times \\mathbf{B} = \\mu_0 \\mathbf{J} + \\mu_0 \\varepsilon_0 \\frac{\\partial \\mathbf{E}}{\\partial t}
$$
"""
    content = default_content
    if request.method == 'POST':
        content = request.form.get('content', default_content)
    return render_template_string(HTML_TEMPLATE, content=content)

if __name__ == '__main__':
    app.run(debug=False)
