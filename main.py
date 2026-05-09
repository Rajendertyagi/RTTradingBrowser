import sys
import os
import json
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLineEdit, QTabWidget, QPushButton, QMenu)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineUrlRequestInterceptor
from PyQt6.QtGui import QShortcut, QKeySequence

# File paths for persistence
SESSION_FILE = "last_session.json"

# Chrome UI Styling
STYLESHEET = """
    QMainWindow { background-color: #202124; }
    QTabWidget::pane { border: none; background-color: #ffffff; }
    QTabBar::tab {
        background: #202124; color: #9aa0a6; padding: 10px 20px;
        border-top-left-radius: 8px; border-top-right-radius: 8px; min-width: 150px;
    }
    QTabBar::tab:selected { background: #35363a; color: #ffffff; }
    #NavBar { background-color: #35363a; padding: 5px; border-bottom: 1px solid #202124; }
    QLineEdit { background-color: #202124; color: #e8eaed; border-radius: 15px; padding: 5px 15px; border: 1px solid #5f6368; }
    #BackBtn { color: #ea4335; } #FwdBtn { color: #34a853; } #HomeBtn { color: #4285f4; } #AddBtn { color: #fbbc05; }
    QPushButton { border: none; background: transparent; font-size: 16px; width: 30px; height: 30px; }
    QPushButton:hover { background-color: #494c4e; border-radius: 15px; }
"""

class RTTrading(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RTTrading")
        
        # Enable Persistent Cookies (Maintains Logins)
        storage_path = os.path.join(os.getcwd(), "browser_profile")
        QWebEngineProfile.defaultProfile().setPersistentStoragePath(storage_path)
        QWebEngineProfile.defaultProfile().setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)

        # UI Assembly
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setCentralWidget(self.central_widget)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        # Nav Bar
        self.nav_bar = QWidget(); self.nav_bar.setObjectName("NavBar")
        nav_layout = QHBoxLayout(self.nav_bar)
        self.back_btn = QPushButton("←"); self.back_btn.setObjectName("BackBtn")
        self.fwd_btn = QPushButton("→"); self.fwd_btn.setObjectName("FwdBtn")
        self.home_btn = QPushButton("🏠"); self.home_btn.setObjectName("HomeBtn")
        self.add_btn = QPushButton("+"); self.add_btn.setObjectName("AddBtn")
        self.url_bar = QLineEdit()
        
        nav_layout.addWidget(self.back_btn); nav_layout.addWidget(self.fwd_btn)
        nav_layout.addWidget(self.home_btn); nav_layout.addWidget(self.url_bar)
        nav_layout.addWidget(self.add_btn)

        self.layout.addWidget(self.tabs); self.layout.addWidget(self.nav_bar)

        # Event Connections
        self.add_btn.clicked.connect(lambda: self.add_new_tab(is_home=True))
        self.home_btn.clicked.connect(self.load_home_content)
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        self.setStyleSheet(STYLESHEET)
        self.restore_session()
        self.showMaximized()

    def add_new_tab(self, url=None, is_home=False):
        browser = QWebEngineView()
        index = self.tabs.addTab(browser, "New Tab")
        self.tabs.setCurrentIndex(index)
        
        if is_home: self.load_home_content(browser)
        else: browser.setUrl(QUrl(url if url else "about:blank"))
        
        browser.titleChanged.connect(lambda t: self.tabs.setTabText(self.tabs.indexOf(browser), t[:15]))
        browser.urlChanged.connect(lambda q: self.url_bar.setText(q.toString()) if self.tabs.currentWidget() == browser else None)
        return browser

    def load_home_content(self, browser_instance=None):
        browser = browser_instance or self.current_browser()
        links = [
            ("Zerodha", "https://kite.zerodha.com"), ("Dhan", "https://web.dhan.co"),
            ("Upstox", "https://login.upstox.com"), ("AngelOne", "https://trade.angelone.in"),
            ("TradingView", "https://www.tradingview.com"), ("Investing", "https://www.investing.com")
        ]
        grid = "".join([f'<a class="card" href="{l[1]}"><div>{l[0][0]}</div><span>{l[0]}</span></a>' for l in links])
        html = f"""
        <html><head><style>
            body {{ background: #202124; color: white; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
            .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }}
            .card {{ text-decoration: none; color: #9aa0a6; text-align: center; }}
            .card div {{ width: 70px; height: 70px; background: #35363a; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: bold; margin-bottom: 8px; }}
            .card:hover div {{ background: #4285f4; color: white; }}
        </style></head><body><div class="grid">{grid}</div></body></html>
        """
        browser.setHtml(html)

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if "." not in url: url = f"https://www.google.com/search?q={url}"
        elif not url.startswith("http"): url = "https://" + url
        self.current_browser().setUrl(QUrl(url))

    def current_browser(self): return self.tabs.currentWidget()
    def close_tab(self, index): self.tabs.removeTab(index) if self.tabs.count() > 1 else self.load_home_content()

    # Session Restore Logic
    def closeEvent(self, event):
        urls = [self.tabs.widget(i).url().toString() for i in range(self.tabs.count())]
        with open(SESSION_FILE, "w") as f: json.dump(urls, f)
        event.accept()

    def restore_session(self):
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, "r") as f:
                urls = json.load(f)
                for url in urls: self.add_new_tab(url)
        else:
            self.add_new_tab(is_home=True)

app = QApplication(sys.argv)
window = RTTrading()
sys.exit(app.exec())
