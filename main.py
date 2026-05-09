import sys
import os
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QTabWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineUrlRequestInterceptor

# Optimized for TradingView Performance
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--enable-gpu-rasterization --ignore-gpu-blocklist --disable-background-timer-throttling"

# Professional Ad-Block Interceptor
class AdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self):
        super().__init__()
        # Expanded blocklist (Add more keywords as needed)
        self.block_keywords = [
            "doubleclick.net", "google-analytics.com", "adservice.google", 
            "googlesyndication.com", "adnxs.com", "amazon-adsystem.com",
            "popads.net", "tracking", "telemetry", "analytics"
        ]

    def interceptRequest(self, info):
        url_str = info.requestUrl().toString().lower()
        if any(keyword in url_str for keyword in self.block_keywords):
            # Effectively uBlock-style blocking at the engine level
            info.block(True)

class RTTrading(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RTTrading (Ad-Block Enabled)")
        
        # Setup the global ad-blocker for all tabs
        self.interceptor = AdBlockInterceptor()
        QWebEngineProfile.defaultProfile().setUrlRequestInterceptor(self.interceptor)

        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.central_widget)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(lambda i: self.tabs.removeTab(i) if self.tabs.count() > 1 else None)

        self.url_bar = QLineEdit()
        self.url_bar.setStyleSheet("background: #1e222d; color: #d1d4dc; border: none; padding: 8px;")
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        self.main_layout.addWidget(self.url_bar)
        self.main_layout.addWidget(self.tabs)

        # Standard shortcuts
        QShortcut("Ctrl+T", self).activated.connect(lambda: self.add_new_tab("https://www.tradingview.com"))
        QShortcut("Ctrl+W", self).activated.connect(lambda: self.tabs.removeTab(self.tabs.currentIndex()))
        QShortcut("Ctrl+R", self).activated.connect(lambda: self.current_browser().reload())

        self.add_new_tab("https://www.tradingview.com/chart")
        self.showMaximized()

    def add_new_tab(self, url):
        browser = QWebEngineView()
        index = self.tabs.addTab(browser, "New Tab")
        self.tabs.setCurrentIndex(index)
        browser.setUrl(QUrl(url))
        browser.titleChanged.connect(lambda t: self.tabs.setTabText(self.tabs.indexOf(browser), t[:15]))
        browser.urlChanged.connect(lambda qurl: self.url_bar.setText(qurl.toString()))

    def current_browser(self):
        return self.tabs.currentWidget()

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if "." not in url: url = f"https://www.google.com/search?q={url}"
        elif not url.startswith("http"): url = "https://" + url
        self.current_browser().setUrl(QUrl(url))

app = QApplication(sys.argv)
window = RTTrading()
sys.exit(app.exec())
