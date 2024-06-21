from showcase_browser import __version__
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from json import loads
from json.decoder import JSONDecodeError

from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR
from PyQt6.QtWebEngineCore import PYQT_WEBENGINE_VERSION_STR, qWebEngineChromiumVersion


dev_PyQt6 = "6.7.0"
dev_Qt = "6.7.1"
dev_PyQt6_WebEngine = "6.7.0"
dev_PyQt6_Chromium = "118.0.5993.220"

__versions_msg__ = f"""\
ShowCase Browser v{__version__} is developed with
    ~ PyQt6 v{dev_PyQt6} 
        ' Qt v{dev_Qt}
    ~ PyQt6.QtWebEngineCore v{dev_PyQt6_WebEngine} 
        ' Chromium v{dev_PyQt6_Chromium}

Your environ provides
    ~ PyQt6 v{PYQT_VERSION_STR} 
        ' Qt v{QT_VERSION_STR}
    ~ PyQt6.QtWebEngineCore v{PYQT_WEBENGINE_VERSION_STR} 
        ' Chromium v{qWebEngineChromiumVersion()}
"""


class available:

    def __init__(self):
        def get():
            self.ShowCase = self.get_available("showcase-browser")
            self.PyQt6 = self.get_available("PyQt6")
            self.PyQt6WebEngine = self.get_available("PyQt6-WebEngine")

        self.get = get

    def __call__(self):
        self.get()
        self.get = lambda: None
        return self

    @staticmethod
    def get_available(package, default=None):
        try:
            with urlopen(f"https://pypi.python.org/pypi/{package}/json") as u:
                return loads(u.read())["info"]["version"]
        except (URLError, HTTPError):
            pass
        except JSONDecodeError:
            pass
        except KeyError:
            pass
        except AttributeError:
            pass
        except Exception:
            pass
        return default


available = available()


def get_available_msg():
    a = available()
    return __versions_msg__ + f"""\

Current available versions:
    - ShowCase Browser v{a.ShowCase or '[could not retrieved]'}
    - PyQt6 v{a.PyQt6 or '[could not retrieved]'} 
    - PyQt6.QtWebEngineCore v{a.PyQt6WebEngine or '[could not retrieved]'} 
"""


def check_msg():
    msg = ""
    a = available()
    if a.ShowCase and __version__ != a.ShowCase:
        msg += f"""\
A new version of `ShowCase Browser' is available ({a.ShowCase}), for an upgrade execute
    py -m pip install showcase_browser --upgrade
"""
    if a.PyQt6 and PYQT_VERSION_STR != a.PyQt6:
        msg += f"""\
A new version of `PyQt6' is available ({a.PyQt6}), for an upgrade execute
    py -m pip install PyQt6 --upgrade
"""
    if a.PyQt6WebEngine and PYQT_WEBENGINE_VERSION_STR != a.PyQt6WebEngine:
        msg += f"""\
A new version of `PyQt6-WebEngine' is available ({a.PyQt6WebEngine}), for an upgrade execute
    py -m pip install PyQt6-WebEngine --upgrade
"""
    if msg:
        return f"""\
{__versions_msg__}
\x1b[31m
[*]

{msg}
[*]
\x1b[m
"""
