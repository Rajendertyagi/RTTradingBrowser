import sys
import os
from PyQt6.QtCore import QUrl, Qt, QSize
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLineEdit, QTabWidget, QPushButton, QToolButton)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineUrlRequestInterceptor
from PyQt6.QtGui import QShortcut, QKeySequence

# Chrome UI Styling (QSS)
STYLESHEET = """
    QMainWindow { background-color: #202124; }
    
    QTabWidget::pane { border: none; top: -1px; background-color: #ffffff; }
    
    QTabBar::tab {
        background: #202124;
        color: #9aa0a6;
        padding: 8px 20px;
        margin-right: 2px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        min-width: 120px;
    }

    QTabBar::tab:selected {
        background: #ffffff;
        color: #3c4043;
    }

    QTabBar::tab:hover:!selected {
        background: #2d2e31;
    }

    QLineEdit {
        background-color: #f1f3f4;
        color: #202124;
        border-radius: 14px;
        padding: 5px 15px;
        border: 1px solid #dfe1e5;
        font-size: 13px;
        margin: 5px 10px;
    }

    QLineEdit:focus {
        background-color: #ffffff;
        border: 1px solid #8ab4f8;
        box-shadow: 0 1px 2px rgba(60, 64, 67, 0.3);
    }
    
    #NavWidget { background-color: #ffffff; border-bottom: 1px solid #dfe1e5; }
    
    QPushButton {
        border: none;
        border-radius: 14px;
        background: transparent;
        color: #5f6368;
        font-size: 18px;
        width: 28px;
        height: 28px;
    }
    
    QPushButton:hover { background-color: #f1f3f4; }
"""

class AdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        url = info.requestUrl().toString().lower()
        blocks = ["doubleclick", "ads", "analytics", "tracking", "telemetry"]
        if any(b in url for b in blocks):
            info.block(True)

class RTTrading(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RTTrading")
        self.setMinimumSize(1024, 768)
        
        # Interceptor for uBlock-style blocking
        self.interceptor = AdBlockInterceptor()
        QWebEngineProfile.defaultProfile().setUrlRequestInterceptor(self.interceptor)

        # Container
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.central_widget)

        # 1. Tab Bar
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        
        # 2. Navigation Bar (Chrome White Bar)
        self.nav_widget = QWidget()
        self.nav_widget.setObjectName("NavWidget")
        nav_layout = QHBoxLayout(self.nav_widget)
        nav_layout.setContentsMargins(5, 0, 5, 0)

        self.back_btn = QPushButton("←")
        self.fwd_btn = QPushButton("→")
        self.reload_btn = QPushButton("↻")
        
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.fwd_btn)
        nav_layout.addWidget(self.reload_btn)
        nav_layout.addWidget(self.url_bar)

        # Assemble
        self.main_layout.addWidget(self.tabs)
        self.main_layout.addWidget(self.nav_widget)

        # Connections
        self.back_btn.clicked.connect(lambda: self.current_browser().back())
        self.fwd_btn.clicked.connect(lambda: self.current_browser().forward())
        self.reload_btn.clicked.connect(lambda: self.current_browser().reload())

        # Chrome Shortcuts
        self.setup_shortcuts()

        # Theme Application
        self.setStyleSheet(STYLESHEET)

        # Start
        self.add_new_tab("https://www.tradingview.com/chart")
        self.showMaximized()

    def setup_shortcuts(self):
        QShortcut("Ctrl+T", self).activated.connect(lambda: self.add_new_tab("https://www.google.com"))
        QShortcut("Ctrl+W", self).activated.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        QShortcut("Ctrl+L", self).activated.connect(self.url_bar.setFocus)
        QShortcut("Ctrl+R", self).activated.connect(lambda: self.current_browser().reload())
        QShortcut("F5", self).activated.connect(lambda: self.current_browser().reload())
        QShortcut("Ctrl+Tab", self).activated.connect(lambda: self.tabs.setCurrentIndex((self.tabs.currentIndex() + 1) % self.tabs.count()))

    def add_new_tab(self, url):
        browser = QWebEngineView()
        index = self.tabs.addTab(browser, "New Tab")
        self.tabs.setCurrentIndex(index)
        browser.setUrl(QUrl(url))
        browser.titleChanged.connect(lambda t: self.tabs.setTabText(self.tabs.indexOf(browser), t[:15]))
        browser.urlChanged.connect(lambda q: self.url_bar.setText(q.toString()) if self.tabs.currentWidget() == browser else None)

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
