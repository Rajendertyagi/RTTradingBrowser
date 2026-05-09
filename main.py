import sys
import json
import os
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLineEdit, QTabWidget, QPushButton, QToolButton)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtGui import QShortcut, QKeySequence

CONFIG_FILE = "trading_links.json"

class TradingPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        blocked = ["doubleclick.net", "google-analytics.com", "adservice.google.com"]
        if any(domain in url.toString() for domain in blocked):
            return False
        return True

class RTTrading(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RTTrading")
        self.setStyleSheet("background-color: #202124;")

        # Main Layout
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.central_widget)

        # 1. Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)

        # 2. Navigation Bar
        self.nav_bar = QWidget()
        nav_layout = QHBoxLayout(self.nav_bar)
        nav_layout.setContentsMargins(5, 5, 5, 5)
        
        self.url_bar = QLineEdit()
        self.url_bar.setStyleSheet("""
            QLineEdit { background-color: #35363a; color: white; border-radius: 15px; 
            padding: 5px 15px; border: 1px solid #5f6368; }
            QLineEdit:focus { border: 1px solid #8ab4f8; }
        """)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        
        nav_layout.addWidget(self.url_bar)
        self.main_layout.addWidget(self.nav_bar)
        self.main_layout.addWidget(self.tabs)

        # Load dynamic links
        self.links = self.load_links()
        
        # Initialize Shortcuts
        self.setup_chrome_shortcuts()

        # Start with Home
        self.add_new_tab(is_home=True)
        self.showMaximized()

    def setup_chrome_shortcuts(self):
        # --- Tab Management ---
        QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(lambda: self.add_new_tab(is_home=True))
        QShortcut(QKeySequence("Ctrl+Shift+T"), self).activated.connect(self.reopen_closed_tab) # Placeholder logic
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        QShortcut(QKeySequence("Ctrl+Tab"), self).activated.connect(lambda: self.tabs.setCurrentIndex((self.tabs.currentIndex() + 1) % self.tabs.count()))
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), self).activated.connect(lambda: self.tabs.setCurrentIndex((self.tabs.currentIndex() - 1) % self.tabs.count()))
        
        # --- Navigation ---
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self.url_bar.setFocus)
        QShortcut(QKeySequence("Alt+Left"), self).activated.connect(lambda: self.current_browser().back())
        QShortcut(QKeySequence("Alt+Right"), self).activated.connect(lambda: self.current_browser().forward())
        QShortcut(QKeySequence("F5"), self).activated.connect(lambda: self.current_browser().reload())
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(lambda: self.current_browser().reload())
        QShortcut(QKeySequence("Ctrl+Shift+R"), self).activated.connect(lambda: self.current_browser().triggerPageAction(QWebEnginePage.WebAction.ReloadAndBypassCache))

        # --- Zoom & View ---
        QShortcut(QKeySequence("Ctrl++"), self).activated.connect(lambda: self.current_browser().setZoomFactor(self.current_browser().zoomFactor() + 0.1))
        QShortcut(QKeySequence("Ctrl+-"), self).activated.connect(lambda: self.current_browser().setZoomFactor(self.current_browser().zoomFactor() - 0.1))
        QShortcut(QKeySequence("Ctrl+0"), self).activated.connect(lambda: self.current_browser().setZoomFactor(1.0))
        QShortcut(QKeySequence("F11"), self).activated.connect(self.toggle_fullscreen)

        # --- Quick Access ---
        QShortcut(QKeySequence("Ctrl+H"), self).activated.connect(self.load_home_page)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(lambda: print("Find logic here")) # Find in page

    def load_links(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f: return json.load(f)
        return [{"name": "Zerodha", "url": "https://kite.zerodha.com", "init": "Z"}, 
                {"name": "TradingView", "url": "https://www.tradingview.com", "init": "TV"}]

    def add_new_tab(self, url=None, is_home=False):
        browser = QWebEngineView()
        browser.setPage(TradingPage(browser))
        
        index = self.tabs.addTab(browser, "Loading...")
        self.tabs.setCurrentIndex(index)

        if is_home or not url:
            self.load_home_page(browser)
        else:
            browser.setUrl(QUrl(url))

        # Update Tab Title and URL bar
        browser.titleChanged.connect(lambda title: self.tabs.setTabText(self.tabs.indexOf(browser), title[:20]))
        browser.urlChanged.connect(lambda qurl: self.url_bar.setText(qurl.toString()) if self.current_browser() == browser else None)

    def current_browser(self):
        return self.tabs.currentWidget()

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.load_home_page()

    def tab_changed(self, index):
        if self.tabs.widget(index):
            self.url_bar.setText(self.tabs.widget(index).url().toString())

    def load_home_page(self, target_browser=None):
        browser = target_browser or self.current_browser()
        grid_items = "".join([f'<a class="item" href="{i["url"]}"><div class="icon">{i.get("init", "S")}</div><span>{i["name"]}</span></a>' for i in self.links])
        html = f"""
        <html><head><style>
            body {{ background-color: #2b2b2b; color: white; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
            .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }}
            .item {{ text-decoration: none; color: #ccc; text-align: center; }}
            .icon {{ width: 60px; height: 60px; background: #3d3d3d; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-weight: bold; font-size: 20px; color: #8ab4f8; }}
        </style></head>
        <body><h1>RTTrading</h1><div class="grid">{grid_items}</div></body></html>
        """
        browser.setHtml(html)

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if "." not in url: url = f"https://www.google.com/search?q={url}"
        elif not url.startswith("http"): url = "https://" + url
        self.current_browser().setUrl(QUrl(url))

    def toggle_fullscreen(self):
        if self.isFullScreen(): self.showMaximized()
        else: self.showFullScreen()

    def reopen_closed_tab(self):
        # Basic implementation: opens home
        self.add_new_tab(is_home=True)

app = QApplication(sys.argv)
window = RTTrading()
sys.exit(app.exec())
