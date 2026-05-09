import sys
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtGui import QShortcut, QKeySequence

# Minimalist Ad-Blocker List
BLOCKED_DOMAINS = ["doubleclick.net", "google-analytics.com", "adservice.google.com", "zedo.com"]

class TradingPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if any(domain in url.toString() for domain in BLOCKED_DOMAINS):
            return False
        return True

class RTTrading(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set the name of the browser window
        self.setWindowTitle("RTTrading")
        
        self.browser = QWebEngineView()
        self.page = TradingPage(self.browser)
        self.browser.setPage(self.page)
        # Default home page
        self.browser.setUrl(QUrl("https://www.tradingview.com"))

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("RTTrading | Enter URL or Search...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.url_bar)
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Chrome Parity Shortcuts
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self.browser.reload)
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self.url_bar.setFocus)
        QShortcut(QKeySequence("Ctrl++"), self).activated.connect(lambda: self.browser.setZoomFactor(self.browser.zoomFactor() + 0.1))
        QShortcut(QKeySequence("Ctrl+-"), self).activated.connect(lambda: self.browser.setZoomFactor(self.browser.zoomFactor() - 0.1))
        QShortcut(QKeySequence("Ctrl+0"), self).activated.connect(lambda: self.browser.setZoomFactor(1.0))
        
        self.showMaximized()

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if not url: return
        if "." not in url: 
            url = f"https://www.google.com/search?q={url}"
        elif not url.startswith("http"): 
            url = "https://" + url
        self.browser.setUrl(QUrl(url))

app = QApplication(sys.argv)
window = RTTrading()
sys.exit(app.exec())
