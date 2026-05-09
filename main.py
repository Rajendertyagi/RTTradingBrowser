import sys
import os
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLineEdit, QTabWidget)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
from PyQt6.QtGui import QShortcut, QKeySequence

# TradingView Optimization: Force Hardware Acceleration and WebGL
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
    "--enable-gpu-rasterization "
    "--enable-oop-rasterization "
    "--ignore-gpu-blocklist "
    "--enable-webgl2-compute-context "
    "--disable-background-timer-throttling " # Prevents lag in inactive tabs
)

class TradingPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        # Basic Ad-block for trading sites
        blocked = ["doubleclick.net", "google-analytics.com", "adservice.google.com"]
        if any(domain in url.toString() for domain in blocked):
            return False
        return True

class RTTrading(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RTTrading (Optimized)")
        self.setStyleSheet("background-color: #131722; color: white;") # TradingView Dark Theme

        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.central_widget)

        # Tab Widget Configuration
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        
        # URL Bar
        self.url_bar = QLineEdit()
        self.url_bar.setStyleSheet("background: #1e222d; color: #d1d4dc; border: none; padding: 5px; height: 25px;")
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        self.main_layout.addWidget(self.url_bar)
        self.main_layout.addWidget(self.tabs)

        self.setup_shortcuts()
        self.add_new_tab("https://www.tradingview.com/chart")
        self.showMaximized()

    def setup_shortcuts(self):
        # Full Chrome Shortcut Suite
        QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(lambda: self.add_new_tab("https://www.tradingview.com/chart"))
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self.url_bar.setFocus)
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(lambda: self.current_browser().reload())
        QShortcut(QKeySequence("F5"), self).activated.connect(lambda: self.current_browser().reload())
        QShortcut(QKeySequence("Ctrl++"), self).activated.connect(lambda: self.current_browser().setZoomFactor(self.current_browser().zoomFactor() + 0.1))
        QShortcut(QKeySequence("Ctrl+-"), self).activated.connect(lambda: self.current_browser().setZoomFactor(self.current_browser().zoomFactor() - 0.1))
        QShortcut(QKeySequence("Ctrl+0"), self).activated.connect(lambda: self.current_browser().setZoomFactor(1.0))

    def add_new_tab(self, url):
        browser = QWebEngineView()
        browser.setPage(TradingPage(browser))
        # High-performance profile setting
        browser.page().profile().setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
        
        index = self.tabs.addTab(browser, "Chart")
        self.tabs.setCurrentIndex(index)
        browser.setUrl(QUrl(url))
        browser.titleChanged.connect(lambda title: self.tabs.setTabText(self.tabs.indexOf(browser), title[:15]))

    def current_browser(self):
        return self.tabs.currentWidget()

    def close_tab(self, index):
        if self.tabs.count() > 1: self.tabs.removeTab(index)

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if "." not in url: url = f"https://www.google.com/search?q={url}"
        elif not url.startswith("http"): url = "https://" + url
        self.current_browser().setUrl(QUrl(url))

app = QApplication(sys.argv)
window = RTTrading()
sys.exit(app.exec())
