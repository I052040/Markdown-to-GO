import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit,
    QPushButton, QHBoxLayout, QToolBar, QSizePolicy, QTabWidget, QTextEdit
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QAction
from PySide6.QtCore import QUrl, QEvent
import markdown


class BrowserTab(QWidget):
    """A single browser tab with a web view, URL bar, and Markdown editor."""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface components."""
        self.web_view = QWebEngineView()
        
        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL or drop a markdown file")
        self.url_bar.returnPressed.connect(self.load_url)
        self.url_bar.setAcceptDrops(True)
        self.url_bar.installEventFilter(self)
        
        # Action buttons
        self.init_action_buttons()
        
        # Layouts
        url_layout = self.create_url_layout()
        main_layout = QVBoxLayout()
        main_layout.addLayout(url_layout)
        main_layout.addWidget(self.web_view)
        self.setLayout(main_layout)

    def init_action_buttons(self):
        """Initialize action buttons and connect their signals."""
        self.go_button = QPushButton("Go")
        self.preview_button = QPushButton("Preview")
        self.editor_button = QPushButton("Editor")
        self.go_button.clicked.connect(self.load_url)
        self.preview_button.clicked.connect(self.open_preview_tab)
        self.editor_button.clicked.connect(self.open_editor_tab)

    def create_url_layout(self):
        """Create and return the layout for the URL bar and action buttons."""
        url_layout = QHBoxLayout()
        url_layout.addWidget(self.url_bar)
        url_layout.addWidget(self.go_button)
        url_layout.addWidget(self.preview_button)
        url_layout.addWidget(self.editor_button)
        return url_layout

    def load_url(self):
        """Handle URL loading or Markdown file opening."""
        url = self.url_bar.text()
        if os.path.exists(url) and url.endswith('.md'):
            with open(url, 'r', encoding='utf-8') as file:
                content = file.read()
                self.preview_markdown(content)
        else:
            if not url.startswith(("http://", "https://")):
                url = f"http://{url}"
            self.web_view.load(QUrl(url))

    def preview_markdown(self, markdown_content=None):
        """Render Markdown with LaTeX support."""
        content = markdown_content or self.url_bar.text()
        html = markdown.markdown(content, extensions=['extra', 'toc', 'tables', 'fenced_code'])
        styled_html = self.get_styled_html(html)
        self.web_view.setHtml(styled_html)

    def get_styled_html(self, html):
        """Return styled HTML content including MathJax configuration."""
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; }}
                th {{ background-color: #f2f2f2; }}
                pre {{ background-color: #f5f5f5; padding: 15px; }}
            </style>
            <script>
            MathJax = {{
                tex: {{
                    inlineMath: [['\\(', '\\)']],
                    displayMath: [['\\[', '\\]'], ['$$', '$$']],
                    processEscapes: true
                }},
                options: {{
                    skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
                }}
            }};
            </script>
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        </head>
        <body>{html}</body>
        </html>
        """

    def open_preview_tab(self):
        """Open a new tab to preview the Markdown content."""
        main_window = self.window()
        preview_content = self.url_bar.text()
        preview_tab = PreviewTab(preview_content)
        main_window.tabs.addTab(preview_tab, "Preview Markdown")
        main_window.tabs.setCurrentWidget(preview_tab)

    def open_editor_tab(self):
        """Open a new tab for editing Markdown content."""
        main_window = self.window()
        editor_tab = EditorTab(self.url_bar.text(), self.update_content_area)
        main_window.tabs.addTab(editor_tab, "Markdown Editor")
        main_window.tabs.setCurrentWidget(editor_tab)

    def update_content_area(self, content):
        """Update the content area with the provided content."""
        self.url_bar.setText(content)

    def eventFilter(self, source, event):
        """Handle drag and drop events."""
        if event.type() == QEvent.DragEnter and source is self.url_bar:
            if event.mimeData().hasUrls():
                event.acceptProposedAction()
        elif event.type() == QEvent.Drop and source is self.url_bar:
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if file_path.endswith('.md'):
                    with open(file_path, 'r', encoding='utf-8') as file:
                        markdown_content = file.read()
                        if source is self.url_bar:
                            self.url_bar.setText(file_path)
                        self.preview_markdown(markdown_content)
                        event.acceptProposedAction()
        return super().eventFilter(source, event)


class PreviewTab(QWidget):
    """Dedicated tab for Markdown preview."""

    def __init__(self, markdown_content):
        super().__init__()
        self.setup_ui(markdown_content)

    def setup_ui(self, markdown_content):
        """Set up the user interface for the preview tab."""
        self.web_view = QWebEngineView()
        layout = QVBoxLayout()
        layout.addWidget(self.web_view)
        self.setLayout(layout)
        self.show_markdown(markdown_content)

    def show_markdown(self, content):
        """Render Markdown content with identical LaTeX setup."""
        html = markdown.markdown(content, extensions=['extra', 'toc', 'tables', 'fenced_code'])
        styled_html = self.get_styled_html(html)
        self.web_view.setHtml(styled_html)

    def get_styled_html(self, html):
        """Return styled HTML content including MathJax configuration."""
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; }}
                th {{ background-color: #f2f2f2; }}
                pre {{ background-color: #f5f5f5; padding: 15px; }}
            </style>
            <script>
            MathJax = {{
                tex: {{
                    inlineMath: [['\\(', '\\)']],
                    displayMath: [['\\[', '\\]'], ['$$', '$$']],
                    processEscapes: true
                }},
                options: {{
                    skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
                }}
            }};
            </script>
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        </head>
        <body>{html}</body>
        </html>
        """


class EditorTab(QWidget):
    """Dedicated tab for Markdown editing."""

    def __init__(self, initial_content, update_callback):
        super().__init__()
        self.update_callback = update_callback
        self.setup_ui(initial_content)

    def setup_ui(self, initial_content):
        """Set up the user interface for the editor tab."""
        layout = QVBoxLayout()
        self.editor_area = QTextEdit()
        self.editor_area.setPlainText(initial_content)

        self.preview_button = QPushButton("Preview Markdown")
        self.preview_button.clicked.connect(self.preview_content)

        layout.addWidget(self.editor_area)
        layout.addWidget(self.preview_button)
        self.setLayout(layout)

    def preview_content(self):
        """Preview the content of the editor."""
        content = self.editor_area.toPlainText()
        self.update_callback(content)
        main_window = self.window()
        preview_tab = PreviewTab(content)
        main_window.tabs.addTab(preview_tab, "Preview Markdown")
        main_window.tabs.setCurrentWidget(preview_tab)


class MainWindow(QMainWindow):
    """Main window that holds the tabbed browser application."""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Set up the main window user interface."""
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.create_toolbar()

        self.setWindowTitle("Markdown to Go")
        self.resize(800, 600)
        self.add_new_tab()

    def create_toolbar(self):
        """Create and configure the toolbar."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Add new tab button
        new_button = QPushButton("New")
        new_button.clicked.connect(self.add_new_tab)
        toolbar.addWidget(new_button)

        # Back button
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)
        toolbar.addWidget(self.back_button)

        # Spacer to push exit action to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close_application)
        toolbar.addAction(exit_action)

    def add_new_tab(self):
        """Add a new tab to the tab widget."""
        new_tab = BrowserTab()
        new_tab.web_view.setUrl(QUrl("about:blank"))
        index = self.tabs.addTab(new_tab, "New Tab")
        self.tabs.setCurrentIndex(index)

    def go_back(self):
        """Navigate the current tab back."""
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.web_view.back()

    def close_application(self):
        """Exit the application."""
        QApplication.instance().quit()

    def close_tab(self, index):
        """Close the tab at the given index."""
        self.tabs.removeTab(index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
