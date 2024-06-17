from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication


# https://www.riverbankcomputing.com/static/Docs/PyQt6/api/qtwebenginecore/qwebenginesettings.html#WebAttribute


MAP = QWebEngineSettings.WebAttribute._member_map_


def get_current(browser: QWebEngineView) -> dict[str, bool]:
    settings = browser.settings()
    return {name: settings.testAttribute(val)
            for name, val in MAP.items()}


def configure(browser: QWebEngineView, __map: dict[str, bool]):
    settings = browser.settings()
    for name, val in __map.items():
        settings.setAttribute(MAP[name], val)


def about():
    app = QApplication(["webpolicies"])
    defaults = get_current(QWebEngineView())
    app.quit()
    enabled = list()
    disabled = list()
    for name, val in defaults.items():
        if val:
            enabled.append(name)
        else:
            disabled.append(name)
    enabled.sort()
    disabled.sort()

    msg = (
        "\n"
        "PyQt6.QtWebEngineCore.QWebEngineSettings\n"
        "----------------------------------------\n"
        "Visit "
        "https://www.riverbankcomputing.com/static/Docs/PyQt6/api/qtwebenginecore/qwebenginesettings.html#WebAttribute"
        " for a description about the attributes.\n"
    )
    msg += (
        "\n"
        "These properties are enabled by default:\n"
        "\n"
    )
    for i in enabled:
        msg += f"  {i}\n"
    msg += (
        "\n"
        "These properties are disabled by default:\n"
        "\n"
    )
    for i in disabled:
        msg += f"  {i}\n"

    return msg
