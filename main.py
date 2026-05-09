import sys
import os
from PyQt6.QtCore import QUrl, Qt, QPoint
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLineEdit, QTabWidget, QPushButton, QMenu)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineUrlRequestInterceptor
from PyQt6.QtGui import QShortcut, QKeySequence, QAction

# Professional Chrome Theme
STYLESHEET = """
    QMainWindow { background-color: #202124; }
    
    /* Tab Bar at the very top */
    QTabWidget::pane { border: none; background-color: #ffffff; }
    QTabBar::tab {
        background: #202124;
        color: #9aa0a6;
        padding: 10px 20px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        min-width: 150px;
    }
    QTabBar::tab:selected { background: #35363a; color: #ffffff; }
    QTabBar::tab:hover:!selected { background: #2d2e31; }

    /* Address Bar Area (Below Tabs) */
    #NavBar { background-color: #35363a; border-bottom: 1px solid #202124; padding: 5px; }
    
    QLineEdit {
        background-color: #202124;
        color: #e8eaed;
        border-radius: 15px;
        padding: 5px 15px;
        border: 1px solid #5f6368;
    }

    /* Colorful Buttons */
    #BackBtn { color: #ea4335; font-weight: bold; }
    #FwdBtn { color: #34a853; font-weight: bold; }
    #HomeBtn { color: #4285f4; font-weight: bold; }
    #AddTabBtn { color: #fbbc05; font-weight: bold; font-size: 20px; margin-left: 5px; }
    
    QPushButton { border: none; background: transparent; font-size: 16px; width: 30px; }
    QPushButton:hover { background-color: #494c4e; border-radius: 15px; }

    /* Right Click Menu Style */
    QMenu { background-color: #2b2b2b; color: white; border: 1px solid #555; }
    QMenu::item:selected { background-color: #4285f4; }
"""

class RTTrading(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RTTrading")
        
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setCentralWidget(self.central_widget)

        # 1. TABS AT TOP
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        
        # Custom Right Click for Tabs
        self.tabs.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabs.tabBar().customContextMenuRequested.connect(self.show_tab_menu)

        # 2. ADDRESS BAR BELOW TABS
        self.nav_bar = QWidget()
        self.nav_bar.setObjectName("NavBar")
        nav_layout = QHBoxLayout(self.nav_bar)
        
        self.back_btn = QPushButton("←"); self.back_btn.setObjectName("BackBtn")
        self.fwd_btn = QPushButton("→"); self.fwd_btn.setObjectName("FwdBtn")
        self.home_btn = QPushButton("🏠"); self.home_btn.setObjectName("HomeBtn")
        self.add_tab_btn = QPushButton("+"); self.add_tab_btn.setObjectName("AddTabBtn")
        
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.fwd_btn)
        nav_layout.addWidget(self.home_btn)
        nav_layout.addWidget(self.url_bar)
        nav_layout.addWidget(self.add_tab_btn)

        # Assembly
        self.layout.addWidget(self.tabs)
        self.layout.addWidget(self.nav_bar)

        # Logic
        self.add_tab_btn.clicked.connect(lambda: self.add_new_tab("https://www.tradingview.com"))
        self.back_btn.clicked.connect(lambda: self.current_browser().back())
        self.fwd_btn.clicked.connect(lambda: self.current_browser().forward())
        self.home_btn.clicked.connect(lambda: self.current_browser().setUrl(QUrl("https://www.tradingview.com")))

        self.setStyleSheet(STYLESHEET)
        self.add_new_tab("https://www.tradingview.com/chart")
        self.showMaximized()

    def show_tab_menu(self, position):
        index = self.tabs.tabBar().tabAt(position)
        if index == -1: return
        
        menu = QMenu()
        # Screenshot Options Implementation
        menu.addAction("New tab to the right").triggered.connect(lambda: self.add_new_tab())
        menu.addAction("Add tab to new split view")
        menu.addAction("Add tab to new group")
        menu.addSeparator()
        menu.addAction("Reload (Ctrl+R)").triggered.connect(self.current_browser().reload)
        menu.addAction("Duplicate").triggered.connect(lambda: self.add_new_tab(self.current_browser().url().toString()))
        menu.addAction("Pin")
        menu.addAction("Mute site").triggered.connect(lambda: self.current_browser().page().setAudioMuted(True))
        menu.addSeparator()
        menu.addAction("Close (Ctrl+W)").triggered.connect(lambda: self.close_tab(index))
        menu.addAction("Close other tabs").triggered.connect(lambda: self.close_others(index))
        
        menu.exec(self.tabs.tabBar().mapToGlobal(position))

    def add_new_tab(self, url="https://www.google.com"):
        browser = QWebEngineView()
        index = self.tabs.addTab(browser, "New Tab")
        self.tabs.setCurrentIndex(index)
        browser.setUrl(QUrl(url))
        browser.titleChanged.connect(lambda t: self.tabs.setTabText(self.tabs.indexOf(browser), t[:15]))
        browser.urlChanged.connect(lambda q: self.url_bar.setText(q.toString()))

    def current_browser(self): return self.tabs.currentWidget()
    def close_tab(self, index): self.tabs.removeTab(index) if self.tabs.count() > 1 else None
    
    def close_others(self, index):
        for i in reversed(range(self.tabs.count())):
            if i != index: self.tabs.removeTab(i)

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if "." not in url: url = f"https://www.google.com/search?q={url}"
        elif not url.startswith("http"): url = "https://" + url
        self.current_browser().setUrl(QUrl(url))

app = QApplication(sys.argv)
window = RTTrading()
sys.exit(app.exec())
