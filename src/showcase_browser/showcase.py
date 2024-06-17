from __future__ import annotations

import marshal
import pickle
from pathlib import Path
from queue import Queue
from sys import argv, stderr
from traceback import print_exception
from types import FunctionType
from typing import Callable, Literal
from webbrowser import open_new_tab

from PyQt6.QtCore import QUrl, QThread
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QShortcut
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEnginePage
from PyQt6.QtWidgets import QMainWindow, QToolBar, QLineEdit, QApplication, QTabWidget, QToolButton

import communicate
import webpolicies

# qt.qpa.plugin: From 6.5.0, xcb-cursor0 or libxcb-cursor0 is needed to load the Qt xcb platform plugin.
# qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
# This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.
#
# Available platform plugins are: wayland-egl, xcb, vkkhrdisplay, wayland, vnc, linuxfb, offscreen, eglfs, minimal, minimalegl.

# -> sudo apt-get install -y libxcb-cursor-dev


if debug := 0:
    from PyQt6.QtCore import QLoggingCategory
    web_engine_context_log = QLoggingCategory("qt.webenginecontext")
    web_engine_context_log.setFilterRules("*.info=true")


_proj_root = str(Path(__file__).parent)


class _IsolatedPage(QWebEnginePage):

    def createWindow(self, type):
        page = _IsolatedPage(self.parent())

        def url_change(url):
            _page = self.sender()
            self.setUrl(QUrl(url))
            _page.deleteLater()

        page.urlChanged.connect(url_change)

        return page


class _RejectPage(QWebEnginePage):

    def alt(self, url):
        ...

    def createWindow(self, type):
        page = _RejectPage(self.parent())
        return page

    def acceptNavigationRequest(self, url, type, isMainFrame):
        if type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            self.alt(url)
            return False
        else:
            return super().acceptNavigationRequest(url, type, isMainFrame)


class Showcase(QApplication):

    central_widget: QTabWidget | QWebEngineView
    window: QMainWindow
    _browser: Callable[[], QWebEngineView]
    _make_browser_: Callable[[], QWebEngineView]
    _tabs_dyn_label: Callable[[int], None]
    _tabs_default_url: str
    _tabs_default_label: str
    _tabs_keep_last: bool

    @property
    def browser(self):
        return self._browser()

    def _make_browser(
            self,
            behavior_linktarget: Literal["showcase", "browser"] = None,
            behavior_javascript: bool = False,
            behavior_no_scrollbars: bool = False,
            behavior_scrollanimator: bool = False,
            behavior_policies: dict[str, bool] = None,
    ):
        browser = QWebEngineView()

        if behavior_linktarget == "showcase":
            page = _IsolatedPage(browser)
            browser.setPage(page)

        else:

            page = _RejectPage(browser)
            browser.setPage(page)

            if behavior_linktarget == "browser":

                def alt(_, url: QUrl):
                    open_new_tab(url.toString())

                _RejectPage.alt = alt

        policies = dict()

        if behavior_javascript:

            policies[QWebEngineSettings.WebAttribute.JavascriptEnabled.name] = True
            policies[QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows.name] = True
            policies[QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard.name] = True
            policies[QWebEngineSettings.WebAttribute.JavascriptCanPaste.name] = True
            policies[QWebEngineSettings.WebAttribute.AllowWindowActivationFromJavaScript.name] = True

        if behavior_no_scrollbars:

            policies[QWebEngineSettings.WebAttribute.ShowScrollBars.name] = False

        if behavior_scrollanimator:

            policies[QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled.name] = True

        webpolicies.configure(browser, policies | (behavior_policies or {}))

        return browser

    def __init__(
            self,
            url: str | list[str] | None,
            wg_url: bool = False,
            ks_url: str = None,
            wg_back: bool = False,
            ks_back: str = None,
            wg_forward: bool = False,
            ks_forward: str = None,
            wg_refresh: bool = False,
            ks_refresh: str = None,
            wg_home: bool = False,
            ks_home: str = None,
            home_url: str = None,
            wg_stop: bool = False,
            ks_stop: str = None,
            wg_tabs: bool = False,
            wg_tab_close: bool = False,
            ks_tab_close: str = None,
            wg_tab_add: bool = False,
            ks_tab_add: str = None,
            tabs_default_url: str = None,
            tabs_default_label: str = None,
            tabs_dynamic_labels: bool = False,
            tabs_keep_last: bool = True,
            window_title: str = "",
            window_icon: str = None,
            window_maxsize: bool = True,
            com_address: tuple[str, int] = None,
            behavior_linktarget: Literal["showcase", "browser"] = None,
            behavior_javascript: bool = False,
            behavior_no_scrollbars: bool = False,
            behavior_scrollanimator: bool = False,
            behavior_policies: dict[str, bool] = None,
    ):
        QApplication.__init__(self, argv)

        self.window = QMainWindow()

        if window_icon:
            self.setWindowIcon(QIcon(window_icon))
        self.setApplicationName(window_title or "ShowCase")
        self.window.setWindowTitle(window_title or "ShowCase")

        self._make_browser_ = lambda: self._make_browser(behavior_linktarget, behavior_javascript, behavior_no_scrollbars, behavior_scrollanimator, behavior_policies)

        self.home_url = home_url

        self.tool_bar = QToolBar()
        self.wg_back = QAction(QIcon(_proj_root + '/things/back.png'), 'Back')
        self.wg_forward = QAction(QIcon(_proj_root + '/things/forward.png'), 'Forward')
        self.wg_refresh = QAction(QIcon(_proj_root + '/things/refresh.png'), 'Refresh')
        self.wg_home = QAction(QIcon(_proj_root + '/things/home.png'), 'Home')
        self.wg_url = QLineEdit()
        self.wg_stop = QAction(QIcon(_proj_root + '/things/stop.png'), 'Stop')

        if wg_tabs or isinstance(url, list):
            self.central_widget = QTabWidget()
            self.central_widget = self.central_widget
            self.central_widget.setDocumentMode(True)
            if wg_tab_close:
                self.central_widget.setTabsClosable(True)
            if ks_tab_close:
                ks = QShortcut(QKeySequence(ks_tab_close), self.central_widget)
                ks.activated.connect(self.tab_close)
            if wg_tab_add:
                self.wg_tab_add = QToolButton()
                self.wg_tab_add.setIcon(QIcon(_proj_root + '/things/tab_add.png'))
                self.central_widget.setCornerWidget(self.wg_tab_add)
                self.wg_tab_add.clicked.connect(self.tab_add)
            if ks_tab_add:
                QShortcut(QKeySequence(ks_tab_add), self.central_widget).activated.connect(self.tab_add)

            self._tabs_default_url = tabs_default_url or ""
            self._tabs_default_label = tabs_default_label or ""
            self._tabs_keep_last = tabs_keep_last

            self.central_widget.currentChanged.connect(self.set_urlbar_from_browser)
            self.central_widget.tabCloseRequested.connect(self.tab_close)

            self._browser = lambda: self.central_widget.currentWidget()

            if tabs_dynamic_labels:
                self._tabs_dyn_label = lambda i: self.tab_set_label_from_browser(i)
            else:
                self._tabs_dyn_label = lambda i: None

            if isinstance(url, list):
                for u in url:
                    self.tab_add(u)
            elif url:
                self.tab_add(url)

        else:
            self.central_widget = self._make_browser_()
            self.central_widget.urlChanged.connect(self.set_urlbar_from_browser)
            self._browser = lambda: self.central_widget

            if url:
                self.load(url)

        class BarElement:

            def __init__(self, element, is_action):
                self.element = element
                self.is_action = is_action

            def add(self, bar: QToolBar):
                if self.is_action:
                    bar.addAction(self.element)
                else:
                    bar.addWidget(self.element)

        bar_elements: list[BarElement] = list()

        if wg_back:
            self.wg_back.triggered.connect(self.back)
            bar_elements.append(BarElement(self.wg_back, is_action=True))
        if ks_back:
            QShortcut(QKeySequence(ks_back), self.central_widget).activated.connect(self.back)
        if wg_forward:
            self.wg_forward.triggered.connect(self.forward)
            bar_elements.append(BarElement(self.wg_forward, is_action=True))
        if ks_forward:
            QShortcut(QKeySequence(ks_forward), self.central_widget).activated.connect(self.forward)
        if wg_refresh:
            self.wg_refresh.triggered.connect(self.reload)
            bar_elements.append(BarElement(self.wg_refresh, is_action=True))
        if ks_refresh:
            QShortcut(QKeySequence(ks_refresh), self.central_widget).activated.connect(self.reload)
        if home_url:
            if wg_home:
                self.wg_home.triggered.connect(self.home)
                bar_elements.append(BarElement(self.wg_home, is_action=True))
            if ks_home:
                QShortcut(QKeySequence(ks_home), self.central_widget).activated.connect(self.home)
        if wg_url:
            self.wg_url.returnPressed.connect(self.load_from_urlbar)
            bar_elements.append(BarElement(self.wg_url, is_action=False))
        if ks_url:
            QShortcut(QKeySequence(ks_url), self.central_widget).activated.connect(self.wg_url.setFocus)

        if wg_stop:
            self.wg_stop.triggered.connect(self.stop_load)
            bar_elements.append(BarElement(self.wg_stop, is_action=True))
        if ks_stop:
            QShortcut(QKeySequence(ks_stop), self.central_widget).activated.connect(self.stop_load)

        if bar_elements:
            self.window.addToolBar(self.tool_bar)
            for e in bar_elements:
                e.add(self.tool_bar)

        self.window.setCentralWidget(self.central_widget)

        if window_maxsize:
            self.window.showMaximized()
        else:
            self.window.show()

        if com_address:
            self.com_i_pipe = Queue(1)
            self.com_o_pipe = Queue(1)
            self.com = communicate.ServerSide(self.com_i_pipe, self.com_o_pipe, com_address)
            self.com_thread = QThread()
            self.com.moveToThread(self.com_thread)
            self.com_thread.started.connect(self.com.run)
            self.com_thread.start()
            self.com.pipesig.connect(self.com_exec)

    def com_exec(self):
        data = self.com_i_pipe.get()
        res = dict()
        _exec = None
        msg = "[??]"
        try:
            if data.startswith(communicate.PICKLE_HEADER):
                _exec = pickle.loads(data)
                msg = f"{pickle} (protocol={communicate.PICKLE_PROTOCOL})"
            elif data.startswith(communicate.MARSHAL_HEADER):
                _exec = FunctionType(marshal.loads(data), dict())
                msg = f"{marshal} (version={communicate.MARSHAL_VERSION})"
        except Exception as e:
            print_exception(e)
            stderr.flush()
            print(f"\nThe above error occurred when unpicking an object with {msg}.\n", file=stderr, flush=True)
            res["!"] = e
        else:
            try:
                if _exec is not None:
                    _exec(self, res)
                else:
                    _exec = data
                    exec(data, dict(sc=self, showcase=self), res)
            except Exception as e:
                print_exception(e)
                stderr.flush()
                print(f"\nThe above error occurred when executing {_exec}.\n", file=stderr, flush=True)
                res["!"] = e
        self.com_o_pipe.put(pickle.dumps(res))

    def back(self):
        self.browser.back()

    def forward(self):
        self.browser.forward()

    def reload(self):
        self.browser.reload()

    def home(self):
        self.load(self.home_url)

    def load(self, url: str):
        self.browser.setUrl(self.get_url(url))

    def get_url(self, url: str):
        q = QUrl(url)
        if q.scheme() == "":
            q.setScheme("https")
        return q

    def stop_load(self):
        self.browser.stop()

    def load_from_urlbar(self):
        self.load(self.wg_url.text())

    def set_urlbar_from_browser(self):
        self.wg_url.setText(self.browser.url().toString())

    def tab_set_label(self, label: str, index: int = None):
        if index is None:
            index = self.central_widget.currentIndex()
        self.central_widget.setTabText(index, label)

    def tab_set_label_from_browser(self, index: int = None):
        if index is None:
            index = self.central_widget.currentIndex()
        self.tab_set_label(self.central_widget.widget(index).page().title(), index)

    def tab_add(self, url: str = None):
        url = url or self._tabs_default_url
        browser = self._make_browser_()
        browser.setUrl(self.get_url(url))
        i = self.central_widget.addTab(browser, self._tabs_default_label)
        browser.urlChanged.connect(self.set_urlbar_from_browser)
        browser.loadFinished.connect(lambda *_, _i=i: self._tabs_dyn_label(_i))
        self.central_widget.setCurrentIndex(i)

    def tab_close(self, index: int = None):
        if self.central_widget.count() == 1 and self._tabs_keep_last:
            return
        if index is None:
            index = self.central_widget.currentIndex()
        self.central_widget.removeTab(index)
        self.set_urlbar_from_browser()

    def tab_change(self, index: int):
        self.central_widget.setCurrentIndex(index)


if __name__ == "__main__":
    window = Showcase(
        url="https://google.com",
        wg_url=True,
        ks_url="Ctrl+L",
        wg_back=True,
        ks_back="Ctrl+Backspace",
        wg_forward=True,
        ks_forward="Ctrl+Shift+Backspace",
        wg_refresh=True,
        ks_refresh="Ctrl+R",
        home_url="https://github.com",
        wg_home=True,
        ks_home="Ctrl+H",
        wg_stop=True,
        ks_stop="Ctrl+X",
        wg_tabs=False,
        wg_tab_close=True,
        ks_tab_close="Ctrl+-",
        wg_tab_add=True,
        ks_tab_add="Ctrl++",
        tabs_dynamic_labels=True,
        window_title="Title",
        window_icon=None,
        window_maxsize=False,
    ).exec()
