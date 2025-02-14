# 安装依赖：pip install flask markdown requests
import os
import requests
from pathlib import Path
from flask import Flask, render_template_string, request

app = Flask(__name__)

# 创建静态文件目录结构
static_dirs = {
    "js": ["marked.min.js", "highlight.min.js", "polyfill.min.js"],
    "css": ["highlight.default.min.css"],
    "mathjax/es5": ["tex-mml-chtml.js"]
}

for dir_name, files in static_dirs.items():
    dir_path = Path("static") / dir_name
    dir_path.mkdir(parents=True, exist_ok=True)
    
    # 检查并下载缺失文件
    for filename in files:
        file_urls = {
            "marked.min.js": "https://cdnjs.cloudflare.com/ajax/libs/marked/4.0.2/marked.min.js",
            "highlight.min.js": "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.5.0/highlight.min.js",
            "polyfill.min.js": "https://polyfill.io/v3/polyfill.min.js?features=es6",
            "highlight.default.min.css": "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.5.0/styles/default.min.css",
            "tex-mml-chtml.js": "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"
        }
        
        file_path = dir_path / filename
        if not file_path.exists():
            print(f"正在下载 {filename}...")
            try:
                response = requests.get(file_urls[filename])
                response.raise_for_status()
                with open(file_path, "wb") as f:
                    f.write(response.content)
            except Exception as e:
                print(f"下载失败: {str(e)}")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Markdown 实时编辑器</title>
    <script src="/static/js/marked.min.js"></script>
    <script src="/static/js/polyfill.min.js"></script>
    <script id="MathJax-script" async src="/static/mathjax/es5/tex-mml-chtml.js"></script>
    <link rel="stylesheet" href="/static/css/highlight.default.min.css">
    <script src="/static/js/highlight.min.js"></script>
    <style>
        .container { display: flex; gap: 20px; padding: 20px; }
        #editor { 
            width: 45%; height: 80vh; 
            padding: 15px; font-family: monospace;
            border: 1px solid #ddd; border-radius: 5px;
        }
        #preview { 
            width: 45%; height: 80vh; 
            padding: 15px; overflow-y: auto;
            border: 1px solid #ddd; border-radius: 5px;
        }
        .code-block { background: #f5f5f5; padding: 10px; }
        h1 { text-align: center; margin: 20px 0; }
    </style>
</head>
<body>
    <h1>Markdown 实时编辑器</h1>
    <div class="container">
        <textarea id="editor" oninput="updatePreview()" placeholder="输入 Markdown/LaTeX...">{{ content }}</textarea>
        <div id="preview"></div>
    </div>

    <script>
        // 配置Markdown解析器
        marked.setOptions({
            breaks: true,
            highlight: function(code, lang) {
                return hljs.highlightAuto(code).value;
            }
        });

        // 初始化加载内容
        let isFirstLoad = true;
        
        function updatePreview() {
            const content = document.getElementById('editor').value;
            const parsed = marked.parse(content);
            document.getElementById('preview').innerHTML = parsed;
            
            // 首次加载时初始化代码高亮
            if (isFirstLoad) {
                hljs.highlightAll();
                isFirstLoad = false;
            }
            
            // 数学公式渲染
            if (typeof MathJax !== 'undefined') {
                MathJax.typesetClear();
                MathJax.typesetPromise();
            }
        }

        // 初始化预览
        window.onload = updatePreview;
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    default_content = """# 欢迎使用！

## Markdown 示例
- **加粗文字**
- *斜体文字*
- [链接示例](https://example.com)

## LaTeX 示例
行内公式 \\( E = mc^2 \\)

块级公式：
$$ \\int_0^\\infty x^2 dx $$

矩阵：
$$
\\begin{bmatrix}
1 & 2 \\\\
3 & 4
\\end{bmatrix}
$$

## 代码示例
```python
def hello_world():
    print("Hello, World!")
```"""
    
    content = default_content
    if request.method == 'POST':
        content = request.form.get('content', default_content)
    return render_template_string(HTML_TEMPLATE, content=content)

if __name__ == '__main__':
    app.run(debug=True)
