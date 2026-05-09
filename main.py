import sys
import json
import os
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QInputDialog, QMessageBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtGui import QShortcut, QKeySequence

# File where your bookmarks are saved
CONFIG_FILE = "trading_links.json"

DEFAULT_LINKS = [
    {"name": "Zerodha", "url": "https://kite.zerodha.com", "color": "#03a9f4", "init": "Z"},
    {"name": "Upstox", "url": "https://login.upstox.com", "color": "#673ab7", "init": "U"},
    {"name": "AngelOne", "url": "https://trade.angelone.in", "color": "#2196f3", "init": "A"},
    {"name": "Dhan", "url": "https://web.dhan.co", "color": "#ffeb3b", "init": "D"},
    {"name": "TradingView", "url": "https://www.tradingview.com/chart", "color": "#131722", "init": "TV"},
    {"name": "Investing", "url": "https://www.investing.com", "color": "#f7931a", "init": "I"},
]

class TradingPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        # Ad-blocking logic
        blocked = ["doubleclick.net", "google-analytics.com", "adservice.google.com"]
        if any(domain in url.toString() for domain in blocked):
            return False
        return True

class RTTrading(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RTTrading")
        self.links = self.load_links()
        
        self.browser = QWebEngineView()
        self.browser.setPage(TradingPage(self.browser))
        self.load_home()

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search, Enter URL, or use Ctrl+B to add current page to Home...")
        self.url_bar.setStyleSheet("background: #333; color: white; border: none; padding: 8px;")
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.url_bar)
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Shortcuts
        QShortcut(QKeySequence("Ctrl+H"), self).activated.connect(self.load_home)
        QShortcut(QKeySequence("Ctrl+B"), self).activated.connect(self.add_current_to_home)
        QShortcut(QKeySequence("Ctrl+Shift+X"), self).activated.connect(self.clear_links)
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self.url_bar.setFocus)
        
        self.showMaximized()

    def load_links(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return DEFAULT_LINKS

    def save_links(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.links, f, indent=4)

    def load_home(self):
        # Generate HTML dynamically from the links list
        grid_items = ""
        for item in self.links:
            grid_items += f"""
            <a class="item" href="{item['url']}">
                <div class="icon" style="color: {item.get('color', '#fff')};">{item.get('init', item['name'][0])}</div>
                <span>{item['name']}</span>
            </a>"""

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ background-color: #2b2b2b; color: white; font-family: sans-serif; 
                       display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
                .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 30px; }}
                .item {{ display: flex; flex-direction: column; align-items: center; text-decoration: none; color: #ccc; }}
                .icon {{ width: 64px; height: 64px; background: #3d3d3d; border-radius: 15px; 
                        display: flex; align-items: center; justify-content: center; margin-bottom: 8px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1 style="color:#555">RTTrading</h1>
            <div class="grid">{grid_items}</div>
            <p style="color:#555; margin-top:40px;">Ctrl+B to add current page | Ctrl+H for Home</p>
        </body>
        </html>
        """
        self.browser.setHtml(html)

    def add_current_to_home(self):
        url = self.browser.url().toString()
        if "about:blank" in url or not url:
            return
        
        name, ok = QInputDialog.getText(self, "Add to Home", "Enter Name for Shortcut:")
        if ok and name:
            self.links.append({"name": name, "url": url, "color": "#ffffff", "init": name[:2].upper()})
            self.save_links()
            QMessageBox.information(self, "Success", f"{name} added to Home!")

    def clear_links(self):
        if QMessageBox.question(self, "Reset", "Remove all custom links?") == QMessageBox.StandardButton.Yes:
            self.links = []
            self.save_links()
            self.load_home()

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if not url: return
        if "." not in url: url = f"https://www.google.com/search?q={url}"
        elif not url.startswith("http"): url = "https://" + url
        self.browser.setUrl(QUrl(url))

app = QApplication(sys.argv)
window = RTTrading()
sys.exit(app.exec())
